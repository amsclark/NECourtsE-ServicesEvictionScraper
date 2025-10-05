#!/usr/bin/env python3
"""Quick test to fetch one docket page and save HTML for analysis"""

import requests
from bs4 import BeautifulSoup

# Read credentials
with open('.creds', 'r') as f:
    lines = f.read().strip().split('\n')
    username = lines[0]
    password = lines[1] if len(lines) > 1 else ''

# Test with one case from Douglas county
test_url = "https://www.nebraska.gov/justice/case.cgi?search=1&from_case_search=1&court_type=C&county_num=01&case_type=CI&case_year=25&case_id=0024543&client_data=&search=Search+Now"

print(f"Fetching: {test_url}")
print(f"Username: {username}")
print("Requesting...")

try:
    response = requests.get(test_url, auth=(username, password), timeout=60)
    print(f"Status: {response.status_code}")
    
    # Save raw HTML
    with open('debug_raw_docket.html', 'w') as f:
        f.write(response.text)
    print("✓ Saved to debug_raw_docket.html")
    
    # Try to parse it
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Look for defendant info
    print("\n=== Looking for defendant info ===")
    defendant_info = soup.find_all('td', attrs={'colspan': '3'})
    print(f"Found {len(defendant_info)} td elements with colspan=3")
    
    for i, td in enumerate(defendant_info[:5]):
        text = td.get_text(strip=True)
        print(f"[{i}] {text[:200]}")
        if 'Defendant' in text:
            print(f"    ✓ Found defendant!")
    
    # Look for 'Defendant' anywhere
    if 'Defendant' in response.text:
        print("\n'Defendant' found in HTML")
        idx = response.text.find('Defendant')
        snippet = response.text[max(0,idx-100):idx+300]
        print(f"Context:\n{snippet}")
    else:
        print("\n⚠️  'Defendant' NOT found in HTML")
    
    # Check if we got login page instead
    if 'login' in response.text.lower() or 'password' in response.text.lower():
        print("\n⚠️  Might be a login page!")
    
    print(f"\n✓ HTML length: {len(response.text)} characters")
    
except Exception as e:
    print(f"❌ Error: {e}")
