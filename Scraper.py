# Created by Alexander Clark of Metatheria, LLC
# Creative Commons CC0 v1.0 Universal Public Domain Dedication. No Rights Reserved
# Version 0.5

import tkinter as tk
from tkinter import *
import sys
import os
import datetime
import urllib
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import csv
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
if sys.platform == "win32":
    import winsound


# Add argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()


def validate(date_text):
    try: 
        datetime.datetime.strptime(date_text, '%m/%d/%Y')
    except ValueError:
        raise ValueError("Incorrect Date format, should be mm/dd/yyyy")

def fetch_single_docket(address_url, username, password, index, total, attempt=1, max_attempts=2, debug=False):
    """
    Fetch a single docket page. Thread-safe function for parallel execution.
    Returns a list with the docket information or error information, plus retry flag.
    Returns: (data_list, should_retry)
    """
    percent = int((index / total) * 100)
    attempt_str = f" (attempt {attempt}/{max_attempts})" if attempt > 1 else ""
    print(f"[{percent:3d}%] Case {index}/{total}{attempt_str}")
    
    try:
        response = requests.get(address_url, auth=(username, password), timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract defendant information - it's in <pre> tags, not tables
        defendant_info_fields = ['error', 'error  ', 'error']
        
        # Look for "Defendant ACTIVE" in pre tags
        pre_tags = soup.find_all('pre')
        for pre in pre_tags:
            text = pre.get_text()
            if 'Defendant ACTIVE' in text or 'Defendant' in text:
                # Split into lines and clean up
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # Find the line with "Defendant"
                for i, line in enumerate(lines):
                    if 'Defendant' in line:
                        # Next few lines should be: Name, Address, City/State/Zip
                        if i + 3 < len(lines):
                            name = lines[i + 1]  # Name is right after "Defendant ACTIVE"
                            address_line1 = lines[i + 2]  # First address line
                            
                            # Check if we have an apartment/unit number or go straight to city/state/zip
                            next_line = lines[i + 3]
                            
                            # If next line looks like city/state/zip (has state code), use it directly
                            # Otherwise, it's probably an apartment number
                            has_state = any(f' {state} ' in f' {next_line} ' or next_line.startswith(state) 
                                          for state in ['NE', 'IA', 'KS', 'MO', 'SD', 'CO', 'WY'])
                            
                            if has_state:
                                # No apartment line - next_line is city/state/zip
                                address = address_line1
                                city_state_zip = next_line
                            else:
                                # Apartment/unit on separate line
                                if i + 4 < len(lines):
                                    address = address_line1 + ' ' + next_line  # Combine address lines
                                    city_state_zip = lines[i + 4]
                                else:
                                    address = address_line1
                                    city_state_zip = next_line
                            
                            defendant_info_fields = [name, address, city_state_zip]
                            break
                
                if defendant_info_fields != ['error', 'error  ', 'error']:
                    break
        
        # If we didn't find defendant info, save HTML for debugging
        if defendant_info_fields == ['error', 'error  ', 'error'] and debug:
            case_id = address_url.split('case_id=')[1].split('&')[0] if 'case_id=' in address_url else 'unknown'
            debug_file = f"debug_docket_{case_id}.html"
            with open(debug_file, 'w') as f:
                f.write(response.text)
            print(f"      ⚠️  No defendant info found - saved to {debug_file}")
        
        return ([address_url] + defendant_info_fields, False)
        
    except requests.exceptions.Timeout:
        should_retry = attempt < max_attempts
        retry_msg = " - will retry later" if should_retry else " - max attempts reached"
        print(f"      ❌ Timeout after 60 seconds{retry_msg}")
        return ([address_url, 'error', 'error  ', 'error'], should_retry)
    except Exception as e:
        should_retry = attempt < max_attempts
        retry_msg = " - will retry later" if should_retry else " - max attempts reached"
        print(f"      ❌ Error: {e}{retry_msg}")
        return ([address_url, 'error', 'error  ', 'error'], should_retry)


def process_county_dockets(case_urls, county_name, username, password, debug=False):
    """
    Process all docket URLs for a specific county.
    Returns list of address records.
    """
    if not case_urls:
        return []
    
    unique_urls = list(set(case_urls))
    
    print(f"\n{'='*70}")
    print(f"PROCESSING {county_name.upper()} DOCKETS")
    print(f"{'='*70}")
    print(f"📊 {len(unique_urls)} unique case(s) to retrieve")
    print(f"⚡ Using up to 3 concurrent connections\n")
    
    # Track attempts for each URL
    url_attempts = {url: 0 for url in unique_urls}
    pending_urls = list(unique_urls)
    addresses = []
    
    while pending_urls:
        current_batch = pending_urls.copy()
        pending_urls = []  # Reset for retry queue
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all URLs in current batch
            future_to_url = {}
            for url in current_batch:
                url_attempts[url] += 1
                idx = list(url_attempts.keys()).index(url) + 1
                future = executor.submit(
                    fetch_single_docket, 
                    url, 
                    username, 
                    password, 
                    idx, 
                    len(url_attempts), 
                    url_attempts[url],
                    2,  # max_attempts
                    debug
                )
                future_to_url[future] = url
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data_list, should_retry = future.result()
                    
                    if should_retry:
                        # Add to retry queue
                        pending_urls.append(url)
                    else:
                        # Final result (success or max attempts reached)
                        addresses.append(data_list)
                except Exception as e:
                    print(f"      ❌ Exception for {url}: {e}")
                    addresses.append([url, 'error', 'error', 'error'])
        
        # If we have retries, add a small delay before next batch
        if pending_urls:
            retry_count = len(pending_urls)
            print(f"\n⏳ Retrying {retry_count} case(s) after brief delay...\n")
            time.sleep(2)  # Brief pause before retrying
    
    print(f"✓ {county_name} complete: {len(addresses)} docket(s) processed\n")
    return addresses

def load_credentials():
    """
    Load credentials from .creds file if it exists.
    File format (plain text, two lines):
    username
    password
    
    Returns tuple: (username, password) or (None, None) if file doesn't exist
    """
    creds_file = ".creds"
    try:
        if os.path.exists(creds_file):
            with open(creds_file, 'r') as f:
                lines = f.read().strip().split('\n')
                if len(lines) >= 2:
                    username = lines[0].strip()
                    password = lines[1].strip()
                    print(f"✓ Loaded credentials from {creds_file}")
                    return (username, password)
                else:
                    print(f"⚠ {creds_file} exists but doesn't have 2 lines")
                    return (None, None)
        else:
            return (None, None)
    except Exception as e:
        print(f"⚠ Error reading {creds_file}: {e}")
        return (None, None)

def fetch_calendar_with_selenium(county, target_date):
    """
    Use Selenium to fetch the calendar page, allowing user to solve reCAPTCHA if needed.
    Returns the page HTML after successful submission.
    """
    print(f"\n{'='*60}")
    print(f"Opening browser for {county} county...")
    print(f"{'='*60}")
    print("⏳ If reCAPTCHA appears, you have 60 seconds to complete it.")
    print("📌 The scraper will automatically continue once the page loads.")
    print("🔄 You get 3 attempts if the CAPTCHA fails.")
    
    # Set up Chrome options
    chrome_options = Options()
    # Don't use headless mode so user can see and interact with reCAPTCHA
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the calendar page
        url = 'https://www.nebraska.gov/courts/calendar/index.cgi'
        driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Fill in the form using JavaScript to avoid overlay issues (reCAPTCHA iframe can block clicks)
        # Select County Court radio button
        court_radio = driver.find_element(By.ID, "courtC")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", court_radio)
        time.sleep(0.3)
        if not court_radio.is_selected():
            driver.execute_script("arguments[0].click();", court_radio)
        
        # Select the county from dropdown
        county_dropdown = driver.find_element(By.ID, "countyC")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", county_dropdown)
        time.sleep(0.3)
        # Set the value and trigger change event to ensure it registers
        driver.execute_script(f"""
            arguments[0].value = '{county}';
            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
        """, county_dropdown)
        
        # Verify county was selected
        selected_county = county_dropdown.get_attribute("value")
        print(f"📍 County selected: {selected_county}")
        
        # Select "Search By Date" radio button
        date_radio = driver.find_element(By.ID, "dateRadio")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", date_radio)
        time.sleep(0.3)
        if not date_radio.is_selected():
            driver.execute_script("arguments[0].click();", date_radio)
        
        # Small delay to ensure radio selection is processed
        time.sleep(0.5)
        
        # Enter the date - use JavaScript to set value directly to avoid datepicker issues
        search_field = driver.find_element(By.ID, "searchField")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_field)
        time.sleep(0.3)
        driver.execute_script("arguments[0].value = '';", search_field)  # Clear first
        driver.execute_script(f"arguments[0].value = '{target_date}';", search_field)
        
        # Verify the date was entered
        entered_value = search_field.get_attribute("value")
        print(f"📅 Date field value: {entered_value}")
        
        # Scroll to the submit button to make it visible
        submit_button = driver.find_element(By.ID, "submitButton")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
        time.sleep(0.5)
        
        # Display form summary and give user a moment to verify
        print("\n" + "="*60)
        print("📋 FORM READY - PLEASE VERIFY")
        print("="*60)
        print(f"✓ County: {selected_county}")
        print(f"✓ Date: {entered_value}")
        print("\n⏱️  Auto-submitting in 3 seconds...")
        print("   (You can manually click Search if you see any issues)")
        print("="*60 + "\n")
        
        # Give user 3 seconds to review before auto-clicking
        time.sleep(3)
        
        # Auto-click the submit button
        print("🔘 Clicking Search button...")
        driver.execute_script("arguments[0].click();", submit_button)
        
        print("\n⏳ Waiting for reCAPTCHA...")
        print("👉 Complete the reCAPTCHA challenge if it appears")
        print("👉 The scraper will automatically continue after you pass\n")
        
        # Wait for navigation to complete after user clicks submit and completes reCAPTCHA
        # We'll wait for either results table or error message, with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Wait up to 120 seconds for user to click submit and complete reCAPTCHA
                print(f"⏳ Waiting for you to submit and complete reCAPTCHA (attempt {retry_count + 1}/{max_retries})...")
                
                # Wait for page to change after submission
                initial_url = driver.current_url
                
                # First wait for the form to be submitted (URL changes or page content changes)
                WebDriverWait(driver, 120).until(
                    lambda d: d.current_url != initial_url or 
                             "submitted=Submit" in d.current_url or
                             len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 1
                )
                
                # Give the page a moment to fully load
                time.sleep(2)
                
                # Give the page a moment to fully load
                time.sleep(2)
                
                # Check if we have results or need to retry
                current_url = driver.current_url
                page_source = driver.page_source
                
                # Check for reCAPTCHA validation failure message
                if "Recaptcha Validation failed" in page_source or "reCAPTCHA validation failed" in page_source:
                    print("\n❌ reCAPTCHA validation failed!")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"⚠  Please try again. Attempt {retry_count + 1}/{max_retries}")
                        print("👉 The form is still showing - click the 'Search' button again")
                        print("👉 Make sure to check the 'I'm not a robot' box and complete any challenges\n")
                        time.sleep(3)
                    continue
                
                # Check if we successfully got results
                soup = BeautifulSoup(page_source, 'lxml')
                rows = soup.find_all('tr')
                
                # Check if "No results found" or similar message
                if "No results" in page_source or "no results" in page_source or "No Results" in page_source:
                    print("ℹ️  No cases found for this date/county")
                    return page_source
                
                # Look for data rows
                has_data = any("Restitution" in row.get_text() or "Real Fed" in row.get_text() 
                               or "LLT" in row.get_text() or "FED" in row.get_text() 
                               for row in rows)
                
                if has_data:
                    print("✓ Successfully loaded calendar page with case data!")
                    return page_source
                
                # If we have a table with multiple rows (even if no eviction cases)
                if len(rows) > 5:
                    print("✓ Successfully loaded calendar page!")
                    return page_source
                
                # If we're still here and on a results page (not the form), accept it
                if "submitButton" not in page_source:
                    print("✓ Results page loaded (may be empty)")
                    return page_source
                
                # Still on form page but no error message - might have timed out
                print("⚠ Still on search form. Did you click Search and complete reCAPTCHA?")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"   Attempt {retry_count + 1}/{max_retries} - please try again\n")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error during wait: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    time.sleep(2)
        
        # If we exhausted retries, return what we have
        print("⚠ Max retries reached. Returning current page content.")
        return driver.page_source
        
    finally:
        # Close the browser
        time.sleep(2)  # Give user a moment to see the results
        driver.quit()
        print("Browser closed.")


def scrapeCalendar():
    #counties_list = ["Douglas", "Lancaster", "Sarpy"]
    if (c_option.get() == "2"):
        counties_list = ["Adams", "Antelope", "Arthur", "Banner", "Blaine", "Boone", "Box Butte", "Boyd", "Brown", "Buffalo", "Burt", "Butler", "Cass", "Cedar", "Chase", "Cherry", "Cheyenne", "Clay", "Colfax", "Cuming", "Custer", "Dakota", "Dawes", "Dawson", "Deuel", "Dixon", "Dodge", "Douglas", "Dundy", "Fillmore", "Franklin", "Frontier", "Furnas", "Gage", "Garden", "Garfield", "Gosper", "Grant", "Greeley", "Hall", "Hamilton", "Harlan", "Hayes", "Hitchcock", "Holt", "Hooker", "Howard", "Jefferson", "Johnson", "Kearney", "Keith", "Keya Paha", "Kimball", "Knox", "Lancaster", "Lincoln", "Logan", "Loup", "Madison", "McPherson", "Merrick", "Morrill", "Nance", "Nemaha", "Nuckolls", "Otoe", "Pawnee", "Perkins", "Phelps", "Pierce", "Platte", "Polk", "Red Willow", "Richardson", "Rock", "Saline", "Sarpy", "Saunders", "Scotts Bluff", "Seward", "Sheridan", "Sherman", "Sioux", "Stanton", "Thayer", "Thomas", "Thurston", "Valley", "Washington", "Wayne", "Webster", "Wheeler", "York"]
    if (c_option.get() == "1"):
        counties_list = ["Douglas", "Lancaster", "Sarpy"]
    if (c_option.get() == "3"):
        counties_list = ["Douglas", "Lancaster", "Sarpy", "Hall", "Buffalo", "Dodge", "Scotts Bluff", "Madison", "Platte", "Lincoln"]
    
    print("\n" + "="*70)
    print("STARTING SCRAPER")
    print("="*70)
    print(f"📅 Target Date: {entry1.get()}")
    print(f"📍 Counties to Process: {len(counties_list)}")
    print(f"🔍 Counties: {', '.join(counties_list)}")
    print("="*70)
    print("\n⚠️  IMPORTANT: You must be present to solve reCAPTCHA challenges!")
    print("    A browser window will open for each county.\n")
    
    targetDate = entry1.get()
    username= user_entry.get()
    password= pass_entry.get()
    validate(targetDate)
    urlEncodedDate = urllib.parse.quote(targetDate, safe='')
    #label1 = tk.Label(root, text="Processing")
    #canvas1.create_window(200, 230, window=label1)
    cases = list()
    listrow = list()
    restitution_cases = list()
    addresses = list()
    address = list()
    
    # PHASE 1 & 2: Fetch calendar and process dockets county-by-county
    print("\n" + "="*70)
    print("FETCHING CALENDARS AND PROCESSING DOCKETS")
    print("="*70)
    print("Note: Each county is processed independently (calendar + dockets)")
    print("="*70 + "\n")
    
    all_addresses = []
    
    for idx, county in enumerate(counties_list, 1):
        print(f"\n{'='*70}")
        print(f"COUNTY {idx}/{len(counties_list)}: {county.upper()}")
        print(f"{'='*70}\n")
        print(f"📅 Fetching calendar for {targetDate}...")
        root.update_idletasks()
        
        # Use Selenium to fetch the page and handle reCAPTCHA
        page_html = fetch_calendar_with_selenium(county, targetDate)
        
        if args.debug:
            print("HTML Content:")
            print(page_html)
        
        # Parse calendar page and extract case URLs
        soup = BeautifulSoup(page_html, 'lxml')
        rows = soup.find_all('tr')
        county_case_urls = []
        
        for row in rows:
            if "Restitution" in row.get_text() or "Real Fed" in row.get_text() or "LLT" in row.get_text() or "FED" in row.get_text():
                listrow = row.get_text().splitlines()
                if ("CR" not in listrow[6]):
                    case_number = listrow[6]
                    print(f"  Found case: {case_number}")
                    
                    # Build case URL
                    case_url = 'https://www.nebraska.gov/justice/case.cgi?search=1&from_case_search=1&court_type=C&county_num='
                    case_url += county_numbers_dict.get(county)
                    case_url += '&case_type=CI&case_year='
                    case_url += case_number[2:4]
                    case_url += '&case_id='
                    case_url += case_number[4:]
                    case_url += '&client_data=&search=Search+Now'
                    county_case_urls.append(case_url)
        
        print(f"✓ Found {len(county_case_urls)} case(s) in {county} county")
        
        # Process this county's dockets immediately
        if county_case_urls:
            county_addresses = process_county_dockets(county_case_urls, county, username, password, args.debug)
            # Add county name to each record
            for address_record in county_addresses:
                address_record.append(county)
            all_addresses.extend(county_addresses)
        else:
            print(f"  No cases to process for {county}\n")
    
    print("\n" + "="*70)
    print("ALL COUNTIES COMPLETE")
    print("="*70)
    print(f"✓ Total records retrieved: {len(all_addresses)}\n")
    
    # Format address records for CSV
    print("="*70)
    print("FINALIZING RESULTS")
    print("="*70)
    
    for address in all_addresses:
        if (len(address) == 2):
            address.insert(1, " ")
            address.insert(2, " ")
            address.insert(3, " ")
            address.insert(4, " ")
        if (len(address) == 3):
            address.insert(2, " ")
            address.insert(3, " ")
            address.insert(4, " ")
        if (len(address) == 4):
            address.insert(3, " ")
            address.insert(4, " ")
        if (len(address) == 5):
            address.insert(4, " ")
        address[5] = " ".join(address[5].split())
        address.append(address[0][120:122] + "CI" + address[0][131:138])
        # County is already appended, so we don't need to look it up
        address.pop(1)
        address[2] = address[2] + " " + address[3]
        address.pop(3)
        address[2].rstrip(" ,")
    for address in all_addresses:
        address.pop(0)
        if len(address) == 6:
            if address[3] == "":
                address.pop(3)
    headers = ['name', 'address', 'city state zip', 'case number', 'county']
    all_addresses.insert(0, headers)
    filename = "eviction_cases_for_" + datetime.datetime.strptime(targetDate, '%m/%d/%Y').strftime('%Y-%m-%d') + "_generated_on_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".csv"
    
    print(f"📝 Writing CSV spreadsheet file: {filename}")
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(all_addresses)
    
    print(f"✓ Successfully wrote {len(all_addresses)-1} record(s) to {filename}")
    
    if sys.platform == "win32":
        winsound.Beep(2500,250)
    
    print("\n" + "="*70)
    print("✓ SCRAPING COMPLETE!")
    print("="*70 + "\n")

    




county_numbers_dict = {"Adams" : "14",
 "Antelope" : "26",
 "Arthur" : "91",
 "Banner" : "85",
 "Blaine" : "86",
 "Boone" : "23",
 "Box Butte" : "65",
 "Boyd" : "63",
 "Brown" : "75",
 "Buffalo" : "09",
 "Burt" : "31",
 "Butler" : "25",
 "Cass" : "20",
 "Cedar" : "13",
 "Chase" : "72",
 "Cherry" : "66",
 "Cheyenne" : "39",
 "Clay" : "30",
 "Colfax" : "43",
 "Cuming" : "24",
 "Custer" : "04",
 "Dakota" : "70",
 "Dawes" : "69",
 "Dawson" : "18",
 "Deuel" : "78",
 "Dixon" : "35",
 "Dodge" : "05",
 "Douglas" : "01",
 "Dundy" : "76",
 "Fillmore" : "34",
 "Franklin" : "50",
 "Frontier" : "60",
 "Furnas" : "38",
 "Gage" : "03",
 "Garden" : "77",
 "Garfield" : "83",
 "Gosper" : "73",
 "Grant" : "92",
 "Greeley" : "62",
 "Hall" : "08",
 "Hamilton" : "28",
 "Harlan" : "51",
 "Hayes" : "79",
 "Hitchcock" : "67",
 "Holt" : "36",
 "Hooker" : "93",
 "Howard" : "49",
 "Jefferson" : "33",
 "Johnson" : "57",
 "Kearney" : "52",
 "Keith" : "68",
 "Keya Paha" : "82",
 "Kimball" : "71",
 "Knox" : "12",
 "Lancaster" : "02",
 "Lincoln" : "15",
 "Logan" : "87",
 "Loup" : "88",
 "Madison" : "07",
 "McPherson" : "90",
 "Merrick" : "46",
 "Morrill" : "64",
 "Nance" : "58",
 "Nemaha" : "44",
 "Nuckolls" : "42",
 "Otoe" : "11",
 "Pawnee" : "54",
 "Perkins" : "74",
 "Phelps" : "37",
 "Pierce" : "40",
 "Platte" : "10",
 "Polk" : "41",
 "Red Willow" : "48",
 "Richardson" : "19",
 "Rock" : "81",
 "Saline" : "22",
 "Sarpy" : "59",
 "Saunders" : "06",
 "Scotts Bluff" : "21",
 "Seward" : "16",
 "Sheridan" : "61",
 "Sherman" : "56",
 "Sioux" : "80",
 "Stanton" : "53",
 "Thayer" : "32",
 "Thomas" : "89",
 "Thurston" : "55",
 "Valley" : "47",
 "Washington" : "29",
 "Wayne" : "27",
 "Webster" : "45",
 "Wheeler" : "84",
 "York" : "17"}



root = tk.Tk()
root.title("Nebraska Courts E-Services Scraper")

# Load credentials from .creds file if available
saved_username, saved_password = load_credentials()

# date options area
date_frame = LabelFrame(root, text="Target Date", padx=5, pady=5, relief=RIDGE)
label1 = Label(date_frame, text="Please enter a date \n in mm/dd/yyyy format.")
entry1=Entry(date_frame)

# county options area
options_frame = LabelFrame(root, text="Choose a County Option", padx=5, pady=5, relief=RIDGE)
c_option = tk.StringVar(None, "1")
option1 = Radiobutton(options_frame, text="Douglas, Lancaster and Sarpy Only", variable=c_option, value="1")
option3 = Radiobutton(options_frame, text="Top 10 Counties", variable=c_option, value="3")
option2 = Radiobutton(options_frame, text="All Nebraska Counties", variable=c_option, value="2")  


#button to press
button1 = tk.Button(text="Scrape Justice", command=scrapeCalendar)

# credentials
cred_frame = LabelFrame(root, text="Justice Login Credentials", padx=5, pady=5, relief=RIDGE)
user_entry_label = Label(cred_frame, text="Username")
user_entry=Entry(cred_frame)
pass_entry_label = Label(cred_frame, text="Password")
pass_entry=Entry(cred_frame)
pass_entry.config(show="*")

# Pre-populate credentials if loaded from .creds file
if saved_username and saved_password:
    user_entry.insert(0, saved_username)
    pass_entry.insert(0, saved_password)

date_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10)
label1.grid(row=0, column=0)
entry1.grid(row=1, column=0)

options_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10)
option1.grid(row=0, column=0, sticky="W")
option3.grid(row=1, column=0, sticky="W")
option2.grid(row=2, column=0, sticky="W")

cred_frame.grid(row=0, column=3, rowspan=5, padx=10, pady=10)
user_entry_label.grid(row=0, column=0, sticky="W")
user_entry.grid(row=0, column=1, sticky="W")
pass_entry_label.grid(row=1, column=0, sticky="W")
pass_entry.grid(row=1, column=1, sticky="W")

button1.grid(row=7, column=1, sticky="W", padx=10, pady=10)


root.mainloop()