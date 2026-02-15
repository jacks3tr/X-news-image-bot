@echo off
REM Twitter Bot Scheduler
REM This script runs the Twitter bot from the current directory

REM Change to the script's directory
cd /d "%~dp0"

REM Run the bot using python (uses system PATH)
python Main.py

REM Pause to see output (comment out for automated scheduling)
pause
