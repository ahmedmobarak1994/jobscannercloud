#!/usr/bin/env python3
"""Quick test of both search engines"""
import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key] = val

print("=" * 70)
print("TESTING SEARCH ENGINES")
print("=" * 70)

# Test RemoteOK
print("\n1. Testing RemoteOK...")
try:
    from src.sources.remoteok import RemoteOKSource
    source = RemoteOKSource()
    jobs = source.fetch_jobs('all')
    print(f"✅ RemoteOK: {len(jobs)} jobs fetched")

    if jobs:
        relevant = [j for j in jobs if any(kw in j.title.lower() for kw in ['sre', 'reliability', 'platform', 'devops', 'infrastructure'])]
        print(f"   Relevant (SRE/Platform): {len(relevant)} jobs")
        if relevant:
            print(f"   Example: {relevant[0].title} @ {relevant[0].company}")
except Exception as e:
    print(f"❌ RemoteOK failed: {e}")

# Test Adzuna
print("\n2. Testing Adzuna...")
try:
    from src.sources.adzuna import AdzunaSource
    source = AdzunaSource()
    jobs = source.fetch_jobs('nl:site reliability engineer:1')
    print(f"✅ Adzuna: {len(jobs)} jobs fetched (query: 'site reliability engineer')")

    if jobs:
        print(f"   Example: {jobs[0].title} @ {jobs[0].company} ({jobs[0].location})")
except Exception as e:
    print(f"❌ Adzuna failed: {e}")

print("\n" + "=" * 70)
print("BOTH SOURCES TESTED!")
print("=" * 70)

