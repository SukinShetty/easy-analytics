#!/usr/bin/env python3
"""
Test accessing contact data using working filter IDs
"""

import requests
import json

# Configuration
FRESHWORKS_DOMAIN = "kambaacrm.myfreshworks.com"
API_KEY = "2IbbXJgW_QJLDOBwl7Znqw"

def test_filtered_contacts():
    """Test accessing contacts using filter IDs"""
    
    headers = {
        'Authorization': f'Token token={API_KEY}',
        'Content-Type': 'application/json'
    }
    
    base_url = f"https://{FRESHWORKS_DOMAIN}"
    
    # Known working filter IDs from our previous test
    filter_tests = [
        (402005390281, "All Contacts"),
        (402005390280, "New Contacts"), 
        (402005390282, "Recently Modified"),
        (402005390283, "Recently Imported"),
    ]
    
    print("🔍 Testing Filtered Contact Access")
    print("=" * 50)
    
    results = {}
    
    for filter_id, filter_name in filter_tests:
        print(f"📊 Testing: {filter_name} (ID: {filter_id})")
        
        # Try different endpoint patterns
        endpoints_to_try = [
            f"/crm/sales/api/contacts?filter_id={filter_id}",
            f"/crm/sales/api/contacts?filter={filter_id}",
            f"/crm/sales/api/contacts/filter/{filter_id}",
            f"/crm/sales/api/contacts/views/{filter_id}",
            f"/crm/sales/api/filters/{filter_id}/contacts",
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{base_url}{endpoint}"
                print(f"   🔗 Trying: {endpoint}")
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ SUCCESS!")
                        
                        if 'contacts' in data:
                            contacts = data['contacts']
                            print(f"   📋 Found {len(contacts)} contacts")
                            if contacts:
                                # Show sample contact
                                sample = contacts[0]
                                name = sample.get('display_name', sample.get('name', 'Unknown'))
                                email = sample.get('email', 'No email')
                                print(f"   👤 Sample: {name} ({email})")
                        else:
                            print(f"   📄 Response keys: {list(data.keys())}")
                        
                        results[filter_name] = data
                        break  # Success, no need to try other endpoints
                        
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Non-JSON response")
                        
                elif response.status_code == 403:
                    print(f"   🔒 FORBIDDEN (403)")
                elif response.status_code == 404:
                    print(f"   ❌ NOT FOUND (404)")
                else:
                    print(f"   ❌ ERROR ({response.status_code})")
                    
            except Exception as e:
                print(f"   💥 Exception: {e}")
        
        print()
    
    return results

def test_other_endpoints():
    """Test other possible data endpoints"""
    
    headers = {
        'Authorization': f'Token token={API_KEY}',
        'Content-Type': 'application/json'
    }
    
    base_url = f"https://{FRESHWORKS_DOMAIN}"
    
    print("🔍 Testing Other Possible Endpoints")
    print("=" * 50)
    
    # Other endpoints to try
    other_endpoints = [
        "/crm/sales/api/leads",
        "/crm/sales/api/activities", 
        "/crm/sales/api/tasks",
        "/crm/sales/api/notes",
        "/crm/sales/api/appointments",
        "/crm/sales/api/products",
        "/crm/sales/api/deal_sources",
        "/crm/sales/api/deal_types",
        "/crm/sales/api/deal_stages",
        "/crm/sales/api/currencies",
        "/crm/sales/api/territories",
    ]
    
    working_endpoints = []
    
    for endpoint in other_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📡 Testing: {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! Keys: {list(data.keys())}")
                    working_endpoints.append(endpoint)
                except:
                    print(f"   ✅ SUCCESS! (Non-JSON response)")
                    working_endpoints.append(endpoint)
            elif response.status_code == 403:
                print(f"   🔒 FORBIDDEN")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
            else:
                print(f"   ❌ ERROR ({response.status_code})")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 WORKING ENDPOINTS FOUND: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"   ✅ {endpoint}")
    
    return working_endpoints

def main():
    print("🚀 Advanced Freshworks API Test")
    print("=" * 50)
    print(f"Domain: {FRESHWORKS_DOMAIN}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    print()
    
    # Test filtered contacts
    contact_results = test_filtered_contacts()
    
    # Test other endpoints
    working_endpoints = test_other_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if contact_results:
        print(f"✅ Contact filters working: {len(contact_results)}")
    else:
        print("❌ No contact data accessible via filters")
    
    if working_endpoints:
        print(f"✅ Additional working endpoints: {len(working_endpoints)}")
    else:
        print("❌ No additional endpoints found")

if __name__ == "__main__":
    main() 