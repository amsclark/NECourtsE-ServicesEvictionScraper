@echo off
REM Activate virtual environment and run the scraper
call venv\Scripts\activate.bat
python Scraper.py %*

