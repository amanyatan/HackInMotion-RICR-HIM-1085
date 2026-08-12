@echo off
REM COSMOS full-stack launcher (Windows).
REM Starts the FastAPI backend (:8000) and the Next.js frontend (:3000) in
REM two separate console windows. Requires backend\.env to be configured.

cd /d "%~dp0"

echo ============================================================
echo  COSMOS - starting backend and frontend
echo ============================================================

start "COSMOS Backend (:8000)" cmd /k "cd /d %~dp0backend && call run.bat"
start "COSMOS Frontend (:3000)" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo Backend : http://localhost:8000  (API docs at /docs)
echo Frontend: http://localhost:3000
echo.
echo Close each window to stop that server.
pause
