@echo off
REM Setup script for Windows

echo ==========================================
echo Nebraska Courts E-Services Scraper Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo + Python found
python --version

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo X pip is not installed.
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

echo + pip found
python -m pip --version

REM Check if Chrome is installed
where chrome >nul 2>&1
if errorlevel 1 (
    echo.
    echo ! Warning: Google Chrome might not be installed.
    echo The scraper requires Chrome for Selenium WebDriver.
    echo Install Chrome from: https://www.google.com/chrome/
    echo.
    pause
)

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo ! Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo + Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo ==========================================
echo + Setup complete!
echo ==========================================
echo.
echo To run the scraper:
echo   1. Activate the virtual environment: venv\Scripts\activate
echo   2. Run the scraper: python Scraper.py
echo   3. When done, deactivate: deactivate
echo.
pause
