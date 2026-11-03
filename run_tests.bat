@echo off
REM Windows regression runner: runs the pytest suite, saves a log,
REM then scans the log for failures. Equivalent of run_tests.sh.
REM Usage (Command Prompt, inside the project folder):  run_tests.bat

if not exist logs mkdir logs
set LOG=logs\run_latest.log

echo Running regression suite... (log: %LOG%)
python -m pytest -v > %LOG% 2>&1
set PYTEST_STATUS=%ERRORLEVEL%
type %LOG%

echo.
echo ---- Log check: %LOG% ----
for /f %%A in ('findstr /c:" PASSED" %LOG% ^| find /c /v ""') do set PASSED=%%A
for /f %%A in ('findstr /c:" FAILED" %LOG% ^| find /c /v ""') do set FAILED=%%A
echo Passed: %PASSED%  Failed: %FAILED%

if not "%FAILED%"=="0" (
  echo Failing tests:
  findstr /c:" FAILED" %LOG%
)

if not "%PYTEST_STATUS%"=="0" (
  echo RESULT: FAIL
  exit /b 1
)
echo RESULT: PASS
