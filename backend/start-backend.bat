@echo off
title COMUSE Backend - Dev Server

cd /d "%~dp0"

if not exist "app\main.py" (
    echo [ERROR] app\main.py not found in "%CD%"
    pause
    exit /b 1
)

rem Use the existing virtual environment if present, otherwise fall back to system Python.
rem Never hardcodes a Python path or any secret.
set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo Using existing virtual environment: .venv
) else (
    echo [WARN] .venv not found. Using system Python.
    echo        Install dependencies first with: pip install -r requirements.txt
)

rem Guard: only ONE backend instance should run on port 8000.
netstat -ano | findstr "LISTENING" | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8000 is already in use - backend may already be running.
    echo        Do NOT start a second instance.
    echo        Close the other COMUSE window, then run this file again.
    pause
    exit /b 0
)

echo Starting COMUSE backend with: uvicorn app.main:app --reload --port 8000
echo API:   http://127.0.0.1:8000
echo Docs:  http://127.0.0.1:8000/docs
echo -----------------------------------------------------------
"%PYTHON_EXE%" -m uvicorn app.main:app --reload --port 8000

echo.
echo Backend process stopped.
pause