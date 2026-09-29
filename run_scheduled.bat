@echo off
REM Runs the daily check-in on a repeating schedule until you close this window.
REM
REM This is opt-in. run.bat still performs a single cycle and exits, so
REM upgrading does not start unattended sign-ins on its own.
REM
REM Options can be passed through, e.g. run_scheduled.bat --rest-hours 12
call .venv\Scripts\activate.bat
python -m app.headless_app --schedule %*
pause
