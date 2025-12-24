"""
Main job scanner orchestration
"""
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .sources import SOURCE_REGISTRY
from .models import Job
from .filtering import JobFilter
from .state import StateManager
from .alerting import SlackAlerter


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
        print_all: bool = False
    ):
        self.sources = sources
        self.filter = JobFilter(filter_config)
        self.state = state_manager
        self.slack = slack_alerter
        self.max_workers = max_workers
        self.dry_run = dry_run
        self.explain = explain
        self.print_all = print_all

        self.stats = {
            "sources_scanned": 0,
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
        for source_type, identifiers in self.sources.items():
            source_class = SOURCE_REGISTRY.get(source_type)
            if not source_class:
                print(f"  ⚠️  Unknown source: {source_type}")
                continue

            for identifier in identifiers:
                tasks.append((source_type, identifier, source_class))

        print(f"  📦 Scanning {len(tasks)} sources...")

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
                    print(f"  ✓ {src_type}/{ident}: {len(jobs)} jobs")
                except Exception as e:
                    print(f"  ✗ {src_type}/{ident}: {e}")
                    self.stats['errors'] += 1

        # Filter jobs
        print(f"\n🔍 Filtering {len(all_jobs)} jobs...")
        alerts = []

        for job in all_jobs:
            result = self.filter.filter_job(job, explain=self.explain or self.print_all)

            if result.passed:
                self.stats['jobs_passed'] += 1

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

        # Summary
        self._print_summary()

        return self.stats

    def _fetch_jobs(self, source_type: str, identifier: str, source_class) -> List[Job]:
        source = source_class()
        jobs = source.fetch_jobs(identifier)
        self.stats['sources_scanned'] += 1
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
        print(f"  Jobs fetched:      {self.stats['jobs_fetched']}")
        print(f"  Jobs passed:       {self.stats['jobs_passed']}")
        print(f"  New jobs:          {self.stats['jobs_new']}")
        print(f"  Updated jobs:      {self.stats['jobs_updated']}")
        print(f"  Alerts sent:       {self.stats['alerts_sent']}")
        print(f"  Errors:            {self.stats['errors']}")
        print(f"{'='*60}\n")

