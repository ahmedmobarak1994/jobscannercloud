#!/usr/bin/env python3
"""
Remote SRE Job Scanner CLI
"""
import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Auto-load .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key] = val

from src.config import Config
from src.state import StateManager
from src.scanner import JobScanner
from src.alerting import SlackAlerter
from src.source_health import SourceHealth


def cmd_scan(args):
    """Run job scan"""
    config = Config(args.config)
    state = StateManager(config.get_state_path())

    # Setup Slack - always try if webhook is available
    slack = None
    if not args.dry_run:
        webhook = config.get_slack_webhook()
        if webhook:
            print(f"✅ Slack webhook configured")
            slack = SlackAlerter(webhook)
        else:
            print("⚠️  No Slack webhook found (set SLACK_WEBHOOK_URL env var)")

    # Create scanner
    scanner = JobScanner(
        sources=config.get_sources(),
        filter_config=config.get_filters(),
        state_manager=state,
        slack_alerter=slack,
        max_workers=args.workers,
        dry_run=args.dry_run,
        explain=args.explain,
        print_all=args.print_all
    )

    # Run scan
    stats = scanner.scan()
    state.close()

    return 0


def cmd_test_slack(args):
    """Test Slack integration"""
    config = Config(args.config)
    webhook = config.get_slack_webhook()

    if not webhook:
        print("❌ Slack not configured")
        return 1

    slack = SlackAlerter(webhook)
    slack.send_test()

    return 0


def cmd_source_health(args):
    """Show source health status"""
    health = SourceHealth()
    stats = health.get_stats()

    print("\n" + "=" * 60)
    print("📊 SOURCE HEALTH STATUS")
    print("=" * 60)
    print(f"  OK:              {stats.get('OK', 0)}")
    print(f"  TEMP_FAIL:       {stats.get('TEMP_FAIL', 0)}")
    print(f"  PERM_FAIL:       {stats.get('PERM_FAIL', 0)}")
    print("=" * 60)

    failed = health.get_failed_sources()
    if failed:
        print(f"\n❌ Failed Sources ({len(failed)}):")
        print("=" * 60)
        for source in failed:
            print(f"\n  {source['type']}/{source['id']}")
            print(f"    Status: {source['status']}")
            print(f"    Fail count: {source['fail_count']}")
            if source['http_status']:
                print(f"    HTTP status: {source['http_status']}")
            print(f"    Error: {source['error']}")
        print("=" * 60)
    else:
        print("\n✅ All sources are healthy!")

    print()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Remote SRE Job Scanner")

    parser.add_argument("--config", default="config.balanced.json", help="Config file")
    parser.add_argument("--workers", type=int, default=10, help="Workers")

    subparsers = parser.add_subparsers(dest="command")

    # scan
    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--dry-run", action="store_true")
    scan_parser.add_argument("--explain", action="store_true")
    scan_parser.add_argument("--print-all", action="store_true")

    # test-slack
    test_slack_parser = subparsers.add_parser("test-slack")

    # source-health
    source_health_parser = subparsers.add_parser("source-health", help="Show source health status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    handlers = {
        "scan": cmd_scan,
        "test-slack": cmd_test_slack,
        "source-health": cmd_source_health,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

