#!/bin/bash
# Run script for Linux/Mac

# Activate virtual environment
source venv/bin/activate

# Run the scraper
python3 Scraper.py "$@"

# Note: venv stays activated. User can deactivate manually if desired.
