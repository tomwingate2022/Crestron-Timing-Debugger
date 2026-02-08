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

REM Edit OUT as desired:
set "OUT=timing_view.edges.html"

echo.
echo Running: Custom output name (edges) --out "%OUT%"
py "%SCRIPT%" "%LOG%" --mode edges --max-signals 40 --out "%OUT%"
echo.
echo Done. Open: "%OUT%" (created in the current working folder).
pause
