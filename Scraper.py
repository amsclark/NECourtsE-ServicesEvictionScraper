# Created by Alexander Clark of Metatheria, LLC
# Creative Commons CC0 v1.0 Universal Public Domain Dedication. No Rights Reserved

import tkinter as tk
from tkinter import *
import sys
import datetime
import urllib
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import csv
import winsound





def validate(date_text):
    try: 
        datetime.datetime.strptime(date_text, '%m/%d/%Y')
    except ValueError:
        raise ValueError("Incorrect Date format, should be mm/dd/yyyy")
        
def scrapeCalendar():
    #counties_list = ["Douglas", "Lancaster"]
    if (c_option.get() == "2"):
        counties_list = ["Adams", "Antelope", "Arthur", "Banner", "Blaine", "Boone", "Box Butte", "Boyd", "Brown", "Buffalo", "Burt", "Butler", "Cass", "Cedar", "Chase", "Cherry", "Cheyenne", "Clay", "Colfax", "Cuming", "Custer", "Dakota", "Dawes", "Dawson", "Deuel", "Dixon", "Dodge", "Douglas", "Dundy", "Fillmore", "Franklin", "Frontier", "Furnas", "Gage", "Garden", "Garfield", "Gosper", "Grant", "Greeley", "Hall", "Hamilton", "Harlan", "Hayes", "Hitchcock", "Holt", "Hooker", "Howard", "Jefferson", "Johnson", "Kearney", "Keith", "Keya Paha", "Kimball", "Knox", "Lancaster", "Lincoln", "Logan", "Loup", "Madison", "McPherson", "Merrick", "Morrill", "Nance", "Nemaha", "Nuckolls", "Otoe", "Pawnee", "Perkins", "Phelps", "Pierce", "Platte", "Polk", "Red Willow", "Richardson", "Rock", "Saline", "Sarpy", "Saunders", "Scotts Bluff", "Seward", "Sheridan", "Sherman", "Sioux", "Stanton", "Thayer", "Thomas", "Thurston", "Valley", "Washington", "Wayne", "Webster", "Wheeler", "York"]
    if (c_option.get() == "1"):
        counties_list = ["Douglas", "Lancaster"]
    print("Processing...")
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
    for county in counties_list:
        print("Getting case numbers for eviction cases (Restitution, Real Fed, FED or LLT is in description) for " + targetDate + " from the calendar for " + county + " county...")
        root.update_idletasks()
        #label1 = tk.Label(root, text="Getting case numbers from " + county + " county.")
        params = {
          ('court', 'C'),
          ('countyC', county),
          ('countyD', ''),
          ('selectRadio', 'date'),
          ('searchField', targetDate),
          ('submitButton', 'Submit'),
        }
        response = requests.get('https://www.nebraska.gov/courts/calendar/index.cgi', params=params)
        soup = BeautifulSoup(response.content, 'lxml')
        rows = soup.find_all('tr')
        for row in rows:
            if "Restitution" in row.get_text() or "Real Fed" in row.get_text() or "LLT" in row.get_text() or "FED" in row.get_text():
                listrow = row.get_text().splitlines()
                if ("CR" not in listrow[6]):
                    listrow.append(county)
                    print("Adding " + listrow[7] + " county case number " + listrow[6] + " to the list to scrape.")
                    case_url = 'https://www.nebraska.gov/justice/case.cgi?search=1&from_case_search=1&court_type=C&county_num='
                    case_url += county_numbers_dict.get(listrow[7])
                    case_url += '&case_type=CI&case_year='
                    case_url += listrow[6][2:4]
                    case_url += '&case_id='
                    case_url += listrow[6][4:]
                    case_url += '&client_data=&search=Search+Now'
                    listrow.append(case_url)
                    restitution_cases.append(listrow)
    
    
    #create new list of lists to store deduplicated URLs for cases and the docket info we are going to get back.
    print("Deduplicating list...")
    for restitution_case in restitution_cases:
        address = [restitution_case[8]]
        if address not in addresses:
            addresses.append(address)
    
    
    for address in addresses:
        print("Retrieving " + address[0])
        docket_response = requests.get(address[0], auth=(username, password))
        docket_soup = BeautifulSoup(docket_response.content, 'lxml')
        docket_blocks = docket_soup.find_all('pre')
        attorney_column_offset = docket_blocks[1].get_text().find("Attorney")
        addresslines = docket_blocks[1].get_text().splitlines()
        addresslines_no_attys = list()
        if attorney_column_offset > 0:
            for addressline in addresslines:
                addresslines_no_attys.append(addressline[0:attorney_column_offset])
        addresslines = addresslines_no_attys
        addresslines_trimmed = list()
        for addressline in addresslines:
            addresslines_trimmed.append(addressline.strip())
        addresslines = addresslines_trimmed
        start_yet = 0
        defendant_count = 0
        current_line = -1
        for addressline in addresslines:
            current_line = current_line + 1
            if addressline.find("Defendant") > -1:
                start_yet = 1
                defendant_count = defendant_count + 1
            if start_yet == 1 and defendant_count == 1:
                address.append(addressline)
            if start_yet == 1 and defendant_count > 1:
                if addressline.find("Defendant") > -1:
                    if "ccupants" not in addresslines[current_line + 1] and "CCUPANTS" not in addresslines[current_line + 1]:
                        address[2] = address[2] + ", " + (addresslines[current_line + 1])
            
    for address in addresses:
        if (len(address) == 5):
            address.insert(4, " ")
        address[5] = " ".join(address[5].split())
        address.append(address[0][120:122] + "CI" + address[0][131:138])
        address.append(list(county_numbers_dict.keys())[list(county_numbers_dict.values()).index(address[0][94:96])])
    filename = "eviction_cases_for_" + datetime.datetime.strptime(targetDate, '%m/%d/%Y').strftime('%Y-%m-%d') + "_generated_on_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".csv"
    print("Writing csv spreadsheet file")
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(addresses)
    winsound.Beep(2500,250)
    print("Done.")

    




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



# date options area
date_frame = LabelFrame(root, text="Target Date", padx=5, pady=5, relief=RIDGE)
label1 = Label(date_frame, text="Please enter a date \n in mm/dd/yyyy format.")
entry1=Entry(date_frame)

# county options area
options_frame = LabelFrame(root, text="Choose a County Option", padx=5, pady=5, relief=RIDGE)
c_option = tk.StringVar(None, "1")
option1 = Radiobutton(options_frame, text="Douglas and Lancaster Only", variable=c_option, value="1")
option2 = Radiobutton(options_frame, text="All Nebraska Counties", variable=c_option, value="2")  

#button to press
button1 = tk.Button(text="Scrape Justice", command=scrapeCalendar)

# credentials
cred_frame = LabelFrame(root, text="Justice Login Credentials", padx=5, pady=5, relief=RIDGE)
user_entry_label = Label(cred_frame, text="Username")
user_entry=Entry(cred_frame)
pass_entry_label = Label(cred_frame, text="Password")
pass_entry=Entry(cred_frame)

date_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10)
label1.grid(row=0, column=0)
entry1.grid(row=1, column=0)

options_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10)
option1.grid(row=0, column=0, sticky="W")
option2.grid(row=1, column=0, sticky="W")

cred_frame.grid(row=0, column=3, rowspan=5, padx=10, pady=10)
user_entry_label.grid(row=0, column=0, sticky="W")
user_entry.grid(row=0, column=1, sticky="W")
pass_entry_label.grid(row=1, column=0, sticky="W")
pass_entry.grid(row=1, column=1, sticky="W")

button1.grid(row=7, column=1, sticky="W", padx=10, pady=10)


root.mainloop()


