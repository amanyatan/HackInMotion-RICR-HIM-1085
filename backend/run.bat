@echo off
REM COSMOS backend launcher (Windows).
REM Creates a venv if missing, installs deps, then starts uvicorn on :8000.

cd /d "%~dp0"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)

call ".venv\Scripts\activate.bat"

if not exist ".env" (
  echo WARNING: backend\.env not found. Copy .env.example to .env first.
)

echo Installing/verifying dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo.
echo Starting COSMOS API on http://localhost:8000  (docs: /docs)
py -m uvicorn app.main:app --reload --port 8000
