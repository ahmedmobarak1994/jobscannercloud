#!/bin/bash
# Quick test script - clears state and runs fresh scan

set -e

cd "$(dirname "$0")"

echo "🗑️  Clearing state..."
rm -rf .state/

echo "📡 Loading .env..."
export $(grep -v '^#' .env | xargs)

echo "🚀 Running fresh scan..."
python3 jobhunt.py --config config.balanced.json scan

echo ""
echo "✅ Done! Check Slack for alerts."

