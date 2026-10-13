@echo off
title BrowserShield-X Launcher
echo ===================================================
echo Starting BrowserShield-X Backend and Frontend...
echo ===================================================

cd /d "%~dp0"

:: Start Python Backend in a separate window
echo [1/2] Starting Python Backend on port 8000...
start "BrowserShield-X Backend (Port 8000)" cmd /k "cd backend && (if exist ..\.venv\Scripts\activate.bat call ..\.venv\Scripts\activate.bat) && (if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat) && python main.py"

:: Wait 3 seconds
timeout /t 3 /nobreak >nul

:: Start React Frontend in a separate window
echo [2/2] Starting React Frontend Dashboard...
start "BrowserShield-X Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo BrowserShield-X is running!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ===================================================
pause
