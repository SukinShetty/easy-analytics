#!/usr/bin/env python3
"""
Quick API Debug - Focus on permission issue
"""

import requests
import json

def test_endpoint_quick(endpoint, name):
    """Quick test of an endpoint"""
    domain = 'kambaacrm.myfreshworks.com'
    api_key = '2IbbXJgW_QJLDOBwl7Znqw'
    
    headers = {
        'Authorization': f'Token token={api_key}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://{domain}{endpoint}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"{name}: Status {response.status_code}")
        
        if response.status_code == 403:
            try:
                error = response.json()
                print(f"  Error: {error}")
            except:
                print(f"  Raw response: {response.text[:100]}")
        
        elif response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"  ✅ Success: Found keys {list(data.keys())}")
                    
                    # Count records
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"    {key}: {len(value)} records")
                            
            except:
                print(f"  ✅ Success but not JSON")
                
    except Exception as e:
        print(f"  Error: {e}")

def main():
    print("🔍 Quick API Permission Debug")
    print("=" * 50)
    
    # Test the working endpoint first
    print("\n✅ WORKING ENDPOINTS:")
    test_endpoint_quick('/crm/sales/api/appointments', 'Appointments')
    
    # Test the forbidden endpoints
    print("\n❌ FORBIDDEN ENDPOINTS:")
    test_endpoint_quick('/crm/sales/api/deals', 'Deals')
    test_endpoint_quick('/crm/sales/api/contacts', 'Contacts')
    test_endpoint_quick('/crm/sales/api/sales_accounts', 'Sales Accounts')
    
    # Check if there are other endpoints that might work
    print("\n🧪 TESTING ALTERNATIVE PATHS:")
    
    # Sometimes Freshworks has different endpoint structures
    alternative_endpoints = [
        ('/crm/sales/api/selector/deals', 'Deals Selector'),
        ('/crm/sales/api/lookup/deals', 'Deals Lookup'),
        ('/crm/sales/api/search/deals', 'Deals Search'),
        ('/crm/sales/api/selector/contacts', 'Contacts Selector'),
        ('/crm/sales/api/lookup/contacts', 'Contacts Lookup'),
        ('/crm/sales/api/search/contacts', 'Contacts Search'),
    ]
    
    for endpoint, name in alternative_endpoints:
        test_endpoint_quick(endpoint, name)
    
    print("\n" + "=" * 50)
    print("🎯 KEY FINDINGS:")
    
    # Check if it's truly a permission issue or something else
    print("\nPossible reasons for 403 Forbidden:")
    print("1. API key doesn't have 'Deals' or 'Contacts' permission scope")
    print("2. Your Freshworks plan doesn't include API access to these modules")
    print("3. The endpoints are correctly blocked by admin settings")
    print("4. You need a different type of API key (Admin vs User)")
    
    print("\n💡 NEXT STEPS:")
    print("1. Check Freshworks CRM → Settings → API Settings")
    print("2. Verify what permissions your API key actually has")
    print("3. Ask your Freshworks admin to enable Deals/Contacts API access")
    print("4. Consider if your Freshworks plan includes full API access")

if __name__ == '__main__':
    main() 