@echo off
REM Daily fetch script for Gothic arXiv
REM This script activates the virtual environment and runs the daily fetch task

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run daily fetch
python backend\tasks\daily_fetch.py

REM Deactivate virtual environment
deactivate
