@echo off
REM Easy startup script for Diagnosis Quiz Tool
REM For Windows users

echo.
echo ========================================
echo   Diagnosis Quiz Tool
echo ========================================
echo.
echo Starting the app...
echo.
echo The app will open at: http://localhost:3000
echo (Your browser will open automatically)
echo.
echo IMPORTANT: Keep this window open while using the app!
echo Press Ctrl+C when you're done to stop everything
echo.
echo ========================================
echo.

REM Check if in correct directory
if not exist "venv" (
    echo ERROR: Can't find 'venv' folder
    echo Make sure you're in the diagnosis-quiz-tool directory
    echo and have run the setup first (see EASY_INSTALL.md)
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set FLASK_APP=src.app:create_app
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Start backend in background
echo Starting backend server...
start /B python -m flask run --host=0.0.0.0 --port=5000

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 4 /nobreak >nul

echo Backend ready!
echo.

REM Start frontend
echo Starting frontend...
echo (Browser will open automatically)
echo.
cd frontend
npm start

REM When frontend closes, this will continue
echo.
echo App stopped. Thanks for using Diagnosis Quiz Tool!
pause
