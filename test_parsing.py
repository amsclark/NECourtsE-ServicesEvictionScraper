#!/usr/bin/env python3
"""Test the new parsing logic on saved HTML"""

from bs4 import BeautifulSoup

with open('debug_raw_docket.html', 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Extract defendant information - it's in <pre> tags, not tables
defendant_info_fields = ['error', 'error  ', 'error']

# Look for "Defendant ACTIVE" in pre tags
pre_tags = soup.find_all('pre')
print(f"Found {len(pre_tags)} pre tags")

for pre in pre_tags:
    text = pre.get_text()
    if 'Defendant ACTIVE' in text or 'Defendant' in text:
        print("\n✓ Found Defendant in pre tag!")
        # Split into lines and clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find the line with "Defendant"
        for i, line in enumerate(lines):
            if 'Defendant' in line:
                print(f"  Line {i}: {line}")
                # Next few lines should be: Name, Address, City/State/Zip
                if i + 3 < len(lines):
                    name = lines[i + 1]  # Name is right after "Defendant ACTIVE"
                    address_line1 = lines[i + 2]  # First address line
                    
                    print(f"  Name: {name}")
                    print(f"  Address Line 1: {address_line1}")
                    
                    # Check if we have an apartment/unit number or go straight to city/state/zip
                    next_line = lines[i + 3]
                    print(f"  Next line: {next_line}")
                    
                    # If next line looks like city/state/zip (has state code), use it directly
                    # Otherwise, it's probably an apartment number
                    has_state = any(f' {state} ' in f' {next_line} ' or next_line.startswith(state) 
                                  for state in ['NE', 'IA', 'KS', 'MO', 'SD', 'CO', 'WY'])
                    
                    print(f"  Has state code: {has_state}")
                    
                    if has_state:
                        # No apartment line - next_line is city/state/zip
                        address = address_line1
                        city_state_zip = next_line
                    else:
                        # Apartment/unit on separate line
                        print(f"  Detected apartment line: {next_line}")
                        if i + 4 < len(lines):
                            address = address_line1 + ' ' + next_line  # Combine address lines
                            city_state_zip = lines[i + 4]
                        else:
                            address = address_line1
                            city_state_zip = next_line
                    
                    defendant_info_fields = [name, address, city_state_zip]
                    print(f"\n✓ Parsed defendant info:")
                    print(f"  Name: {defendant_info_fields[0]}")
                    print(f"  Address: {defendant_info_fields[1]}")
                    print(f"  City/State/Zip: {defendant_info_fields[2]}")
                    break
        
        if defendant_info_fields != ['error', 'error  ', 'error']:
            break

if defendant_info_fields == ['error', 'error  ', 'error']:
    print("\n❌ Failed to parse defendant info")
