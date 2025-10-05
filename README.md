# Nebraska Courts E-Services Eviction Scraper

The Nebraska Courts E-Services Scraper allows authorized users of Justice E-Services to speed up workflows involving the monitoring of eviction cases in Nebraska and outreach to defendants in eviction cases. 

<img src="https://github.com/amsclark/NECourtsE-ServicesEvictionScraper/blob/main/screenshot.png">

## Important Notes

As with all software involving automation of interactions with web servers, please be considerate of how often you run this software to minimize burden on E-Services servers.

Also please check the terms of use of any system you intend to scrape before scraping. The organization I developed this for already had gotten permission from the courts to automate interactions with the court docketing system and had been doing so in a different way for several years before this tool was developed. 

Although this software is licensed under a public domain license and may be used without license restriction, this software was developed with humanitarian and charitable purposes in mind, with the intention of allowing tenant advocates to monitor and conduct outreach to tenants at risk of homelessness. 

## Features

- GUI interface for easy operation
- Automated browser handling for reCAPTCHA challenges
- Support for single county or batch processing of multiple counties
- Extracts defendant names and addresses from eviction case dockets
- Outputs data to CSV spreadsheet files

## Requirements

- **Python 3.7 or higher**
- **Google Chrome browser** (required for Selenium WebDriver)
- **Internet connection**
- **Justice E-Services credentials** (for accessing individual case dockets)

## Quick Start (Automated Setup)

For a faster setup experience, use the included setup scripts:

### Windows
```cmd
setup.bat
```

### Linux/Mac
```bash
./setup.sh
```

These scripts will automatically:
- Check if Python and pip are installed
- Check if Chrome is installed
- Create a virtual environment
- Install all required dependencies

After setup, use the run scripts to launch the scraper:
- **Windows:** `run.bat` or `run.bat --debug`
- **Linux/Mac:** `./run.sh` or `./run.sh --debug`

## Manual Installation Instructions

If you prefer to set up manually, follow these steps:

### Step 1: Install Python

#### Windows

1. **Check if Python is already installed:**
   - Open Command Prompt (search for "cmd" in Start menu)
   - Type `python --version` and press Enter
   - If you see a version number (e.g., "Python 3.11.x"), Python is installed. Skip to Step 2.

2. **Download and install Python:**
   - Visit https://www.python.org/downloads/
   - Download the latest Python 3.x installer for Windows
   - **Important:** During installation, check the box "Add Python to PATH"
   - Click "Install Now"
   - After installation, restart your terminal/command prompt

3. **Verify installation:**
   - Open a new Command Prompt window
   - Type `python --version` - you should see the Python version
   - Type `pip --version` - you should see the pip version

#### Linux

1. **Check if Python is already installed:**
   ```bash
   python3 --version
   ```
   Most Linux distributions come with Python pre-installed.

2. **If Python is not installed or version is too old:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
   
   **Fedora:**
   ```bash
   sudo dnf install python3 python3-pip
   ```
   
   **Arch Linux:**
   ```bash
   sudo pacman -S python python-pip
   ```

3. **Verify installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

### Step 2: Install Google Chrome

The scraper uses Selenium with Chrome to handle reCAPTCHA challenges.

#### Windows
- Download and install from: https://www.google.com/chrome/

#### Linux
**Ubuntu/Debian:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

**Fedora:**
```bash
sudo dnf install google-chrome-stable
```

### Step 3: Download the Scraper

#### Option A: Using Git (Recommended)
```bash
git clone https://github.com/amsclark/NECourtsE-ServicesEvictionScraper.git
cd NECourtsE-ServicesEvictionScraper
```

#### Option B: Manual Download
1. Go to https://github.com/amsclark/NECourtsE-ServicesEvictionScraper
2. Click the green "Code" button and select "Download ZIP"
3. Extract the ZIP file to a folder of your choice
4. Open a terminal/command prompt in that folder

### Step 4: Set Up Virtual Environment

Using a virtual environment keeps dependencies isolated and prevents conflicts.

#### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
*Note: If you get an execution policy error, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

When activated, you should see `(venv)` at the beginning of your command prompt.

### Step 5: Install Requirements

With the virtual environment activated:

#### Windows
```cmd
pip install -r requirements.txt
```

#### Linux
```bash
pip install -r requirements.txt
```

This will install:
- beautifulsoup4 (HTML parsing)
- requests (HTTP requests)
- lxml (XML/HTML parser)
- selenium (browser automation)
- webdriver-manager (automatic ChromeDriver management)

### Step 6: Running the Scraper

#### Using Run Scripts (Recommended)
The run scripts automatically activate the virtual environment:

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

#### Manual Execution
If you prefer to run manually:

**Windows:**
```cmd
venv\Scripts\activate
python Scraper.py
```

**Linux/Mac:**
```bash
source venv/bin/activate
python3 Scraper.py
```

#### With Debug Mode (shows detailed output)
```cmd
python Scraper.py --debug
# or with run scripts:
run.bat --debug    # Windows
./run.sh --debug   # Linux/Mac
```

## How reCAPTCHA Handling Works

The Nebraska Courts calendar search page now uses Google reCAPTCHA to prevent automated access. This scraper handles it by:

1. **Opening a real Chrome browser window** (not headless) for each county
2. **Automatically filling** the search form with your criteria
3. **Waiting for you** to complete any reCAPTCHA challenges that appear
4. **Detecting when results load** and capturing the data
5. **Closing the browser** automatically after success

### Workflow

The scraper operates in two phases:

**Phase 1: Calendar Pages (reCAPTCHA required)**
- Opens browser for each selected county
- You may need to solve reCAPTCHA for each county
- Collects case numbers for eviction cases

**Phase 2: Individual Case Dockets (no reCAPTCHA)**
- Uses standard HTTP requests (no browser needed)
- Retrieves defendant information from each case
- Generates CSV file with results

### Timing & Retry Logic

- **60 seconds per CAPTCHA attempt** - You have 1 minute to complete each challenge
- **3 retry attempts per county** - If CAPTCHA fails, you can try again
- **Progress indicators** - Clear console messages show which county/case is being processed

**Important:** You must be present during Phase 1 to solve reCAPTCHA challenges. The scraper will wait for you, but if you're scraping many counties (e.g., "All Nebraska Counties" = 93 counties), you'll need to solve many CAPTCHAs in sequence before seeing results.

**Recommendation:** Start with "Douglas, Lancaster and Sarpy Only" (3 counties) to get familiar with the process.

Individual case/docket pages do not have reCAPTCHA and are fetched normally with the requests library.

## Usage Instructions

1. **Launch the scraper** using the commands above
2. **Fill in the GUI form:**
   - Enter a date in MM/DD/YYYY format
   - Select county option (individual counties or batch processing)
   - Enter your Justice E-Services username and password
3. **Click "Scrape Justice"**
4. **Browser automation:**
   - A Chrome browser window will open for each county
   - The form will be filled automatically
   - **If reCAPTCHA appears, complete the challenge manually**
   - The scraper will automatically continue after you solve it
   - The browser will close automatically once data is retrieved
5. **Output:**
   - CSV files are saved in the same directory as the script
   - Filename format: `eviction_cases_for_YYYY-MM-DD_generated_on_YYYY-MM-DD-HH-MM.csv`

### Saving Credentials (Optional)

To avoid entering your Justice E-Services credentials every time:

1. Create a file named `.creds` in the project directory
2. Add your credentials in plain text (two lines):
   ```
   your_username
   your_password
   ```
3. The credentials will be automatically loaded when you launch the scraper

**Example:**
```bash
cp .creds.example .creds
nano .creds  # or use any text editor
# Edit the file to add your actual credentials
```

**Security Note:** The `.creds` file is automatically excluded from git commits via `.gitignore`. However, it stores credentials in plain text on your local machine. Keep your computer secure and don't share this file.

## Troubleshooting

### "Python not found" or "command not found"
- **Windows:** Python may not be in your PATH. Reinstall Python and check "Add Python to PATH"
- **Linux:** Use `python3` instead of `python`

### "pip not found"
- **Windows:** Try `python -m pip` instead of `pip`
- **Linux:** Install with `sudo apt install python3-pip` (Ubuntu/Debian)

### ChromeDriver issues
- Ensure Google Chrome is installed and up to date
- The `webdriver-manager` package should handle ChromeDriver automatically
- If issues persist, try: `pip install --upgrade webdriver-manager`

### reCAPTCHA not appearing or failing
- Make sure you're present to solve the CAPTCHA when the browser opens
- The scraper will wait up to 60 seconds for you to complete it
- You get 3 retry attempts if the CAPTCHA fails

### Virtual environment not activating
- **Windows PowerShell:** You may need to adjust execution policy (see Step 4)
- Make sure you're in the project directory when activating

## Deactivating Virtual Environment

When you're done using the scraper:

#### Windows
```cmd
deactivate
```

#### Linux
```bash
deactivate
```

## Updating the Scraper

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Support

For issues, questions, or contributions, please visit:
https://github.com/amsclark/NECourtsE-ServicesEvictionScraper/issues 
