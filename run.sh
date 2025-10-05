#!/bin/bash
# Run script for Linux/Mac

# Activate virtual environment (it's in bin/, not venv/bin/)
source bin/activate

# Run the scraper
python3 Scraper.py "$@"
