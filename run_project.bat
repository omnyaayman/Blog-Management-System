@echo off
echo Starting Blog Management System...

:: Start Backend
start "Backend - FastAPI" /d "%~dp0" cmd /k "echo Starting Backend... && .venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Start Frontend
start "Frontend - Static Server" /d "%~dp0frontend" cmd /k "echo Starting Frontend... && ..\.venv\Scripts\python -m http.server 3000"

echo Project is running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause
