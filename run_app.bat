@echo off
cd /d "%~dp0"
py -3 main.py
if errorlevel 1 (
  echo.
  echo Could not start. Please install Python 3 and try again.
  pause
)
