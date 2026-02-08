@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM Companion BAT template for: plot_crestron_debug_steps.py
REM Assumptions:
REM   - This .bat file lives in the SAME folder as plot_crestron_debug_steps.py
REM   - Pass the log file as the first argument, or you'll be prompted.
REM ============================================================

set "SCRIPT=%~dp0plot_crestron_debug_steps.py"

if not exist "%SCRIPT%" (
  echo ERROR: Could not find "%SCRIPT%"
  echo Put plot_crestron_debug_steps.py in the same folder as this .bat.
  pause
  exit /b 1
)

set "LOG=%~1"
if "%LOG%"=="" (
  echo.
  echo Drag-and-drop a debug log onto this .bat, or type the full path now.
  set /p LOG=Log file path: 
)

if not exist "%LOG%" (
  echo.
  echo ERROR: Log file not found: "%LOG%"
  pause
  exit /b 1
)

echo.
echo Running: Overview (edges) --max-signals 40
py "%SCRIPT%" "%LOG%" --mode edges --max-signals 40
echo.
echo Done. Open the generated .edges.html file next to the log (or the --out file if used).
pause
