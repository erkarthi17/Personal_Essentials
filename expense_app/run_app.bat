@echo off
REM ============================================
REM Expense Tracker - Auto Launcher
REM ============================================

cd /d "%~dp0"

echo.
echo ====================================
echo   💰 Expense Tracker Launcher
echo ====================================
echo.
echo Starting Streamlit app...
echo.

REM Start Streamlit in a new terminal window and keep it running
start /B "" cmd /c "py -3 -m streamlit run expense_tracker.py --logger.level=error"

REM Wait a few seconds for Streamlit to start
timeout /t 3 /nobreak

REM Automatically open the app in default browser
echo Opening app in your browser...
start http://localhost:8501

echo.
echo ✅ App launched! Browser should open automatically.
echo 💻 If browser doesn't open, visit: http://localhost:8501
echo.
echo Press Ctrl+C in this window to stop the app.
echo.

REM Keep the window open to show messages
cmd /k
