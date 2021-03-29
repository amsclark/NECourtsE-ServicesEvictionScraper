# Nebraska Courts E-Services Eviction Scraper

The Nebraska Courts E-Services Scraper allows authorized users of Justice E-Services to speed up workflows involving the monitoring of eviction cases in Nebraska and outreach to defendants in eviction cases. 

<img src="https://github.com/amsclark/NECourtsE-ServicesEvictionScraper/blob/main/screenshot.png">

As with all software involving automation of interactions with web servers, please be considerate of how often you run this software to minimize burden on E-Services servers.

Also please check the terms of use of any system you intend to scrape before scraping. The organization I developed this for already had gotten permission from the courts to automate interactions with the court docketing system and had been doing so in a different way for several years before this tool was developed. 

Although this software is licensed under a public domain license and may be used without license restriction, this software was developed with humanitarian and charitable purposes in mind, with the intention of allowing tenant advocates to monitor and conduct outreach to tenants at risk of homelessness. 

This software requires Python. It runs with a GUI interface, but messages about status of the scraping process are output to the console, so it should be launched from the console.

The output of scraped information is dumped to .csv spreadsheet files in the folder the tool is executed from.

This tool was developed on Windows and uses the winsound library to play a beep when the process finishes. If you are running on Linux, commenting out the winsound import and commenting out line 110 that reads `winsound.Beep(2500,250)` should allow it to run.


### Installation Instructions

Steps 1-3 are not necessary if you already have Python 3 installed and working without path issues on your computer.

1. Install Python from https://ninite.com/pythonx3/ if it is not already installed.
2. Add C:\Program Files\Python39 to your path. You can do this in Windows Explorer by right-clicking on "This PC", selecting "Properties" then "Advanced system settings", selecting the "Advanced" tab, and then clicking "Environment Variables". Click on "Path" and "Edit". Then click "New" and add the path. Click "OK" on all open dialogs.
3. Click on the start button and search for "manage app execution aliases". Switch "App Installer" off for "python.exe" and "python3.exe"
4. Open a terminal window and install the beautifulsoup, requests, and lxml modules with `python.exe -m pip install bs4 requests lxml` if you don't already have these modules installed
7. Download the script by going to https://raw.githubusercontent.com/amsclark/NECourtsE-ServicesEvictionScraper/main/Scraper.py in your browser, right-clicking in the page and selecting "Save As." Save it in a location where you are going to want to run it from. Note that the .csv files it generates will be outputted to the same folder. So you may want to make a new empty folder within your Documents to save the script to and execute it from.
8. If desired, download run.bat from https://raw.githubusercontent.com/amsclark/NECourtsE-ServicesEvictionScraper/main/run.bat in the same manner. All that this batch file does is run the command listed in #10 so the program can be launched by double-clicking run.bat. 
9. Open a terminal window in the folder where you saved the file by right-clicking in the folder and selecting "Open in Windows Terminal". Skip this is using the run.bat.
10. Start the scraper by typing `python.exe .\Scraper.py` or double-clicking run.bat. 
