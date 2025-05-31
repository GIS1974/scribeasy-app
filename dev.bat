@echo off
title ScribeEasy Development Server

echo.
echo ================================
echo 🚀 ScribeEasy Development Server
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo ❌ Frontend dependencies not installed.
    echo Please run: cd frontend && npm install
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed

REM Check if backend dependencies are installed
cd backend
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend dependencies not installed.
    echo Please run: cd backend && pip install -r requirements.txt
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✅ Backend dependencies installed

echo.
echo Starting development servers...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in a new window
start "ScribeEasy Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "ScribeEasy Frontend" cmd /k "cd frontend && npm run dev"

echo Both servers are starting in separate windows...
echo Close this window or press any key to exit
pause >nul
