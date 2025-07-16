#!/usr/bin/env python3
"""
Freshworks Data Sync - Using Working Endpoints Only
Based on successful API endpoint testing
"""

import requests
import json
import os
from datetime import datetime

# Configuration
FRESHWORKS_DOMAIN = "kambaacrm.myfreshworks.com"
API_KEY = "2IbbXJgW_QJLDOBwl7Znqw"

def test_working_endpoints():
    """Test and fetch data from endpoints that we know work"""
    
    headers = {
        'Authorization': f'Token token={API_KEY}',
        'Content-Type': 'application/json'
    }
    
    base_url = f"https://{FRESHWORKS_DOMAIN}"
    
    # Working endpoints from our test
    working_endpoints = {
        'contact_filters': '/crm/sales/api/contacts/filters',
        'owners': '/crm/sales/api/selector/owners', 
        'contact_statuses': '/crm/sales/api/selector/contact_statuses',
        'contacts_alt': '/api/contacts',  # Alternative API
        'deals_alt': '/api/deals'         # Alternative API
    }
    
    results = {}
    
    print("🔄 Fetching data from working endpoints...")
    print("=" * 50)
    
    for endpoint_name, endpoint_path in working_endpoints.items():
        try:
            url = f"{base_url}{endpoint_path}"
            print(f"📡 Testing: {endpoint_name}")
            print(f"   URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint_name] = data
                    print(f"   ✅ SUCCESS - Got {len(str(data))} characters of data")
                    
                    # Show sample of what we got
                    if isinstance(data, dict):
                        print(f"   📋 Keys: {list(data.keys())}")
                        if 'users' in data and data['users']:
                            print(f"      👥 Found {len(data['users'])} users")
                        elif 'filters' in data and data['filters']:
                            print(f"      🔍 Found {len(data['filters'])} filters")
                        elif 'contact_statuses' in data and data['contact_statuses']:
                            print(f"      📊 Found {len(data['contact_statuses'])} statuses")
                    elif isinstance(data, list):
                        print(f"   📝 Found {len(data)} items")
                        
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  JSON Error: {e}")
                    print(f"   📄 Raw response: {response.text[:200]}...")
                    results[endpoint_name] = response.text
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
        
        print()
    
    return results

def save_results(results):
    """Save results to JSON files for analysis"""
    
    # Create results directory
    os.makedirs('freshworks_data', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for endpoint_name, data in results.items():
        filename = f"freshworks_data/{endpoint_name}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(data, str):
                    f.write(data)
                else:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {endpoint_name} data to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save {endpoint_name}: {e}")

def analyze_available_data(results):
    """Analyze what data we can actually access"""
    
    print("\n" + "=" * 50)
    print("📊 DATA ANALYSIS")
    print("=" * 50)
    
    # Analyze owners data
    if 'owners' in results and 'users' in results['owners']:
        users = results['owners']['users']
        print(f"👥 SALES TEAM ({len(users)} members):")
        for user in users[:5]:  # Show first 5
            name = user.get('display_name', user.get('name', 'Unknown'))
            email = user.get('email', 'No email')
            print(f"   • {name} ({email})")
        if len(users) > 5:
            print(f"   ... and {len(users) - 5} more")
        print()
    
    # Analyze contact statuses
    if 'contact_statuses' in results and 'contact_statuses' in results['contact_statuses']:
        statuses = results['contact_statuses']['contact_statuses']
        print(f"📊 CONTACT STATUSES ({len(statuses)} statuses):")
        for status in statuses:
            name = status.get('name', 'Unknown')
            print(f"   • {name}")
        print()
    
    # Analyze filters
    if 'contact_filters' in results and 'filters' in results['contact_filters']:
        filters = results['contact_filters']['filters']
        print(f"🔍 AVAILABLE FILTERS ({len(filters)} filters):")
        for filter_item in filters[:10]:  # Show first 10
            name = filter_item.get('name', 'Unknown')
            print(f"   • {name}")
        if len(filters) > 10:
            print(f"   ... and {len(filters) - 10} more")
        print()

def main():
    print("🚀 Freshworks Working Endpoints Test")
    print("=" * 50)
    print(f"Domain: {FRESHWORKS_DOMAIN}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    print()
    
    # Test working endpoints
    results = test_working_endpoints()
    
    # Save results
    if results:
        save_results(results)
        analyze_available_data(results)
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS! We can access some Freshworks data")
        print("=" * 50)
        print("📁 Data saved to 'freshworks_data/' folder")
        print("📋 Check the JSON files for detailed data structure")
        print()
        print("🎯 NEXT STEPS:")
        print("1. Review the saved data files")
        print("2. Use this data to build your analytics dashboard")
        print("3. Contact Freshworks admin for access to more endpoints")
        
    else:
        print("\n❌ No data could be retrieved from any endpoint")

if __name__ == "__main__":
    main() 