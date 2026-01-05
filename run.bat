@echo off
SETLOCAL
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
REM Run backend/app.py directly without cd, to avoid import confusion
python backend/app.py
pause
