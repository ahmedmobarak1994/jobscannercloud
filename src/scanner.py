"""
Main job scanner orchestration
"""
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from .sources import SOURCE_REGISTRY
from .models import Job
from .filtering import JobFilter
from .state import StateManager
from .alerting import SlackAlerter
from .source_health import SourceHealth


class JobScanner:
    """Orchestrate job scanning pipeline"""

    def __init__(
        self,
        sources: Dict[str, List[str]],
        filter_config: dict,
        state_manager: StateManager,
        slack_alerter: Optional[SlackAlerter] = None,
        max_workers: int = 10,
        dry_run: bool = False,
        explain: bool = False,
        print_all: bool = False,
        skip_failed_sources: bool = True
    ):
        self.sources = sources
        self.filter = JobFilter(filter_config)
        self.state = state_manager
        self.slack = slack_alerter
        self.max_workers = max_workers
        self.dry_run = dry_run
        self.explain = explain
        self.print_all = print_all
        self.skip_failed_sources = skip_failed_sources

        # Source health tracking
        self.source_health = SourceHealth()

        # Explore mode output
        self.explore_mode = filter_config.get('explore_mode', False)
        self.explore_jobs = []  # Collect all passed jobs for explore output

        self.stats = {
            "sources_scanned": 0,
            "sources_skipped": 0,
            "jobs_fetched": 0,
            "jobs_passed": 0,
            "jobs_new": 0,
            "jobs_updated": 0,
            "alerts_sent": 0,
            "errors": 0,
        }

    def scan(self) -> Dict:
        """Run full scan pipeline"""
        print("🚀 Starting job scan...")

        # Collect tasks
        tasks = []
        skipped = 0
        for source_type, identifiers in self.sources.items():
            source_class = SOURCE_REGISTRY.get(source_type)
            if not source_class:
                print(f"  ⚠️  Unknown source: {source_type}")
                continue

            for identifier in identifiers:
                # Check source health
                if self.skip_failed_sources and self.source_health.should_skip(source_type, identifier):
                    status = self.source_health.get_status(source_type, identifier)
                    skipped += 1
                    if self.explain:
                        print(f"  ⏭️  Skipping {source_type}/{identifier} (status: {status})")
                    continue

                tasks.append((source_type, identifier, source_class))

        if skipped > 0:
            print(f"  ⏭️  Skipped {skipped} failed sources")

        print(f"  📦 Scanning {len(tasks)} sources...")
        self.stats['sources_skipped'] = skipped

        # Fetch jobs in parallel
        all_jobs = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_jobs, src_type, ident, src_class): (src_type, ident)
                for src_type, ident, src_class in tasks
            }

            for future in as_completed(futures):
                src_type, ident = futures[future]
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                    self.stats['sources_scanned'] += 1

                    # Record success
                    self.source_health.record_success(src_type, ident)

                    print(f"  ✓ {src_type}/{ident}: {len(jobs)} jobs")
                except Exception as e:
                    error_msg = str(e)

                    # Extract HTTP status if available
                    http_status = None
                    if "404" in error_msg:
                        http_status = 404
                    elif "403" in error_msg:
                        http_status = 403

                    # Record failure
                    self.source_health.record_failure(src_type, ident, error_msg, http_status)

                    print(f"  ✗ {src_type}/{ident}: {e}")
                    self.stats['errors'] += 1

        # Filter jobs
        print(f"\n🔍 Filtering {len(all_jobs)} jobs...")
        alerts = []

        for job in all_jobs:
            result = self.filter.filter_job(job, explain=self.explain or self.print_all)

            if result.passed:
                self.stats['jobs_passed'] += 1

                # Store for explore mode
                if self.explore_mode:
                    self.explore_jobs.append((job, result))

                should_alert, is_new = self._check_should_alert(job)

                if should_alert:
                    if is_new:
                        self.stats['jobs_new'] += 1
                    else:
                        self.stats['jobs_updated'] += 1

                    alerts.append((job, result))

                    if self.explain or self.print_all:
                        print(f"\n✅ MATCH: {job.title} @ {job.company}")
                        if self.explain:
                            print(self.filter.explain_job(job))

            elif self.print_all:
                print(f"\n❌ REJECT: {job.title} @ {job.company}")
                print(f"Reason: {result.drop_reason}")

        # Send alerts
        if not self.dry_run and self.slack and alerts:
            print(f"\n📢 Sending {len(alerts)} alerts to Slack...")
            self._send_alerts(alerts)

        # Generate explore output
        if self.explore_mode and self.explore_jobs:
            self._write_explore_output()

        # Summary
        self._print_summary()

        return self.stats

    def _fetch_jobs(self, source_type: str, identifier: str, source_class) -> List[Job]:
        source = source_class()
        jobs = source.fetch_jobs(identifier)
        self.stats['jobs_fetched'] += len(jobs)
        return jobs

    def _check_should_alert(self, job: Job) -> tuple:
        """Check if should alert (new or updated)"""
        db_key = job.get_db_key()
        existing = self.state.get_job_state(db_key)

        if not existing:
            self.state.save_job(job, is_new=True)
            return True, True

        is_updated = job.is_updated(
            existing.get("updated_at"),
            existing["content_hash"]
        )

        if is_updated:
            self.state.save_job(job, is_new=False)
            return True, False

        return False, False

    def _send_alerts(self, alerts: List[tuple]):
        for job, result in alerts:
            try:
                self.slack.send_alert(job, result)
                self.stats['alerts_sent'] += 1
            except Exception as e:
                print(f"  ⚠️  Failed alert: {e}")
                self.stats['errors'] += 1

    def _print_summary(self):
        print(f"\n{'='*60}")
        print("📊 SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"  Sources scanned:   {self.stats['sources_scanned']}")
        if self.stats['sources_skipped'] > 0:
            print(f"  Sources skipped:   {self.stats['sources_skipped']} (failed)")
        print(f"  Jobs fetched:      {self.stats['jobs_fetched']}")
        print(f"  Jobs passed:       {self.stats['jobs_passed']}")
        print(f"  New jobs:          {self.stats['jobs_new']}")
        print(f"  Updated jobs:      {self.stats['jobs_updated']}")
        print(f"  Alerts sent:       {self.stats['alerts_sent']}")
        print(f"  Errors:            {self.stats['errors']}")

        # Source health summary
        health_stats = self.source_health.get_stats()
        if health_stats.get('TEMP_FAIL', 0) > 0 or health_stats.get('PERM_FAIL', 0) > 0:
            print(f"\n  Source Health:")
            print(f"    OK:              {health_stats.get('OK', 0)}")
            if health_stats.get('TEMP_FAIL', 0) > 0:
                print(f"    TEMP_FAIL:       {health_stats['TEMP_FAIL']}")
            if health_stats.get('PERM_FAIL', 0) > 0:
                print(f"    PERM_FAIL:       {health_stats['PERM_FAIL']}")

        print(f"{'='*60}\n")

    def _write_explore_output(self):
        """Write explore mode output to markdown file"""
        from pathlib import Path

        output_dir = Path("out")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "explore.md"

        # Sort by score (descending)
        sorted_jobs = sorted(self.explore_jobs, key=lambda x: x[1].score, reverse=True)

        # Take top 50
        top_jobs = sorted_jobs[:50]

        with open(output_file, 'w') as f:
            f.write(f"# Job Scanner Explore Mode\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"**Stats:**\n")
            f.write(f"- Jobs scanned: {self.stats['jobs_fetched']}\n")
            f.write(f"- Jobs passed: {self.stats['jobs_passed']}\n")
            f.write(f"- Showing top: {len(top_jobs)}\n\n")
            f.write("---\n\n")

            for i, (job, result) in enumerate(top_jobs, 1):
                f.write(f"## {i}. {job.title}\n\n")
                f.write(f"**Company:** {job.company} ({job.source})\n\n")
                f.write(f"**Location:** {job.location}\n\n")
                f.write(f"**Score:** {result.score}\n\n")

                # Show scoring breakdown
                if result.scoring_breakdown:
                    f.write(f"**Score Breakdown:**\n")
                    for category, points in result.scoring_breakdown.items():
                        f.write(f"- {category}: +{points}\n")
                    f.write("\n")

                # Show matched keywords
                if result.keyword_matches:
                    f.write(f"**Matched Keywords:**\n")
                    for category, keywords in result.keyword_matches.items():
                        if keywords:
                            f.write(f"- {category}: {', '.join(keywords)}\n")
                    f.write("\n")

                f.write(f"**URL:** {job.url}\n\n")
                f.write("---\n\n")

        print(f"\n📝 Explore output written to: {output_file}")
        print(f"   Top {len(top_jobs)} jobs saved for review")

