#!/usr/bin/env bash
# Regression runner: runs the pytest suite, saves a timestamped log,
# then scans the log for failures. Exit code is non-zero if anything failed.
#
# Usage:  ./run_tests.sh            (tests the local mock API)
#         BASE_URL=https://jsonplaceholder.typicode.com ./run_tests.sh
set -u

cd "$(dirname "$0")"
mkdir -p logs
LOG="logs/run_$(date +%Y%m%d_%H%M%S).log"

echo "Running regression suite... (log: $LOG)"
python3 -m pytest -v 2>&1 | tee "$LOG"
PYTEST_STATUS=${PIPESTATUS[0]}

./check_logs.sh "$LOG"
LOG_STATUS=$?

if [ "$PYTEST_STATUS" -ne 0 ] || [ "$LOG_STATUS" -ne 0 ]; then
  echo "RESULT: FAIL"
  exit 1
fi
echo "RESULT: PASS"
