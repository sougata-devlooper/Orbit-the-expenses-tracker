@echo off
echo Starting Expense Tracker Server...
call venv\Scripts\activate.bat
uvicorn app.main:app --reload
pause
