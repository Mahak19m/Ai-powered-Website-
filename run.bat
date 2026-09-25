@echo off
echo ===================================================
echo   Starting WebCraft AI Website Builder
echo ===================================================

echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "WebCraft AI - Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 2 /nobreak > nul

echo Starting React Vite Frontend on http://localhost:5173 ...
start "WebCraft AI - Frontend" cmd /k "cd frontend && npm.cmd run dev"

echo.
echo Both servers are launching! Open your browser to:
echo http://localhost:5173
echo.
pause
