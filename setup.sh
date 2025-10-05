#!/bin/bash
# Setup script for Linux/Mac

echo "=========================================="
echo "Nebraska Courts E-Services Scraper Setup"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed."
    echo "Please install pip3 first:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

echo "✓ pip3 found: $(pip3 --version)"

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null
then
    echo "⚠ Warning: Google Chrome or Chromium not found."
    echo "The scraper requires Chrome for Selenium WebDriver."
    echo "Install Chrome from: https://www.google.com/chrome/"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 1
    fi
else
    echo "✓ Chrome/Chromium browser found"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "To run the scraper:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the scraper: python3 Scraper.py"
echo "  3. When done, deactivate: deactivate"
echo ""
