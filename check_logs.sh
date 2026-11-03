#!/usr/bin/env bash
# Scan a test log for failures and print a short summary.
# Usage: ./check_logs.sh logs/run_YYYYMMDD_HHMMSS.log
# With no argument it checks the newest log in ./logs.
set -u

cd "$(dirname "$0")"
LOG="${1:-$(ls -t logs/*.log 2>/dev/null | head -n 1)}"

if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
  echo "No log file found."
  exit 2
fi

PASSED=$(grep -c " PASSED" "$LOG")
FAILED=$(grep -c " FAILED" "$LOG")
ERRORS=$(grep -c " ERROR" "$LOG")

echo "---- Log check: $LOG ----"
echo "Passed: $PASSED  Failed: $FAILED  Errors: $ERRORS"

if [ "$FAILED" -gt 0 ] || [ "$ERRORS" -gt 0 ]; then
  echo "Failing tests:"
  grep -E " (FAILED|ERROR)" "$LOG"
  exit 1
fi
echo "No failures found."
