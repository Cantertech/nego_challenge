@echo off

REM Check for virtual environment
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: No .env file found!
    echo Please create a .env file with your OPENAI_API_KEY
    echo Example: copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Run the server
echo Starting Nego Challenge API...
python main.py


