# Nebraska Courts E-Services Eviction Scraper

The Nebraska Courts E-Services Scraper allows authorized users of Justice E-Services to speed up workflows involving the monitoring of eviction cases in Nebraska and outreach to Defendants in eviction cases. 

As with all software involving automation of interactions with web servers, please be considerate of how often you run this software to minimize burden on E-Services servers.

Although this software is licensed under a public domain license and may be used without license restriction, this software was developed with humanitarian and charitable purposes in mind, with the intention of allowing tenant advocates to monitor and conduct outreach to tenants at risk of homelessness. 

This software requires Python. It runs with a GUI interface, but messages about status of the scraping process are output to the console, so it is best to run it from the console.

The output of scraped information is dumped to .csv spreadsheet files in the folder the tool is executed from.

This tool was developed on Windows and uses the winsound library to play a beep when the process finishes. If you are running on Linux, commenting out the winsound import and commenting out line 110 that reads `winsound.Beep(2500,250)` should allow it to run.

You may need to install the tkinter and beautifulsoup Python libraries if they are not already installed. 
