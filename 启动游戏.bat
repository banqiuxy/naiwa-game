@echo off
rem Double-click launcher for the local mirror in .\site
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"

where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0serve.py"
  goto :eof
)

where py >nul 2>nul
if not errorlevel 1 (
  py "%~dp0serve.py"
  goto :eof
)

echo.
echo Python 3 not found. Install it, or serve the "site" folder with any static web server.
echo.
pause
