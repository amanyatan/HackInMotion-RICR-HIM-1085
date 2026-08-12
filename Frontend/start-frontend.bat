@echo off
title COMUSE Frontend - Dev Server

rem This batch file lives inside the Frontend/ folder.
rem The Next.js project root (package.json) is one level up, so we cd up.
cd /d "%~dp0.."

if not exist package.json (
    echo [ERROR] package.json not found in "%CD%"
    echo The batch file must stay inside the Frontend folder of the COMUSE project.
    pause
    exit /b 1
)

rem Guard: only ONE dev server must run. If port 3000 is already listening,
rem a second instance would break the shared .next cache and cause 404s.
netstat -ano | findstr "LISTENING" | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 3000 is already in use - frontend may already be running.
    echo        Do NOT start a second instance - it causes 404 errors.
    echo        Close the other COMUSE window, then run this file again.
    pause
    exit /b 0
)

echo Starting COMUSE frontend with: npm run dev
echo URL:  http://localhost:3000
echo -----------------------------------------------------------
npm run dev

echo.
echo Frontend process stopped.
pause