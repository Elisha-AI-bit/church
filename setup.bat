@echo off
echo ================================================
echo UCZ Church Management System - Setup Script
echo ================================================
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to run migrations
    pause
    exit /b 1
)

echo.
echo ================================================
echo Setup completed successfully!
echo ================================================
echo.
echo Next steps:
echo 1. Create a superuser account by running: python manage.py createsuperuser
echo 2. Start the server by running: python manage.py runserver
echo 3. Access the application at: http://127.0.0.1:8000/
echo.
pause
