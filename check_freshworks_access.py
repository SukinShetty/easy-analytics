#!/usr/bin/env python3
"""
Freshworks API Access Checker for Kambaa CRM
Helps diagnose authorization issues
"""

import requests
import json

# Your credentials
DOMAIN = "kambaacrm.myfreshworks.com"
API_KEY = "2IbbXJgW_QJLDOBwl7Znqw"

print("🔍 Freshworks API Authorization Check")
print("=" * 50)
print(f"Domain: {DOMAIN}")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")  # Show partial key for security
print()

# Test different endpoints to find what works
endpoints = [
    ("/crm/sales/api/contacts/filters", "Contact Filters"),
    ("/crm/sales/api/selector/owners", "Owners List"),
    ("/crm/sales/api/selector/contact_statuses", "Contact Statuses"),
    ("/crm/sales/api/contacts", "Contacts List"),
    ("/crm/sales/api/deals", "Deals List"),
    ("/crm/sales/api/sales_accounts", "Accounts List"),
    ("/api/contacts", "Contacts (Alternative API)"),
    ("/api/deals", "Deals (Alternative API)"),
]

headers = {
    "Authorization": f"Token token={API_KEY}",
    "Content-Type": "application/json"
}

working_endpoints = []

print("Testing different API endpoints...\n")

for endpoint, name in endpoints:
    url = f"https://{DOMAIN}{endpoint}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {name}: SUCCESS")
            working_endpoints.append((endpoint, name))
            
            # Show sample data
            data = response.json()
            if isinstance(data, dict):
                print(f"   Response keys: {list(data.keys())[:5]}")
            elif isinstance(data, list) and len(data) > 0:
                print(f"   Found {len(data)} items")
                
        elif response.status_code == 403:
            print(f"❌ {name}: FORBIDDEN (403)")
        elif response.status_code == 401:
            print(f"❌ {name}: UNAUTHORIZED (401) - Bad API key")
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:50]}")
    
    print()

print("\n" + "=" * 50)
print("DIAGNOSIS:")
print("=" * 50)

if not working_endpoints:
    print("\n❌ No endpoints are accessible with this API key.")
    print("\nPossible issues:")
    print("1. API key might be incorrect or expired")
    print("2. API access might not be enabled for your Freshworks account")
    print("3. Your user role might not have API permissions")
    print("\n📋 TO FIX THIS:")
    print("1. Log into Freshworks CRM: https://kambaacrm.myfreshworks.com")
    print("2. Go to: Settings → API → API Settings")
    print("3. Check if API access is enabled")
    print("4. Generate a new API key if needed")
    print("5. Ensure your user role has API access permissions")
    
else:
    print(f"\n✅ Found {len(working_endpoints)} working endpoints!")
    print("\nWorking endpoints:")
    for endpoint, name in working_endpoints:
        print(f"  • {name}: {endpoint}")
    
    print("\n📋 NEXT STEPS:")
    print("1. Use these working endpoints in your sync script")
    print("2. Update the sync_freshworks_data.py to use the correct endpoints")

print("\n🔐 API KEY VERIFICATION:")
print("Your current API key ends with:", API_KEY[-10:])
print("\nTo get a new API key:")
print("1. Login to: https://kambaacrm.myfreshworks.com")
print("2. Click your profile icon → Settings")
print("3. Go to API Settings → Your API Key")
print("4. Copy the full API key (should be longer than what you have)")

# Test if this is a Freshdesk key instead of Freshsales
print("\n🤔 Testing if this might be a Freshdesk API key...")
freshdesk_url = f"https://kambaa.freshdesk.com/api/v2/tickets"
freshdesk_headers = {
    "Authorization": f"Basic {API_KEY}:X"  # Freshdesk uses Basic auth
}

try:
    response = requests.get(freshdesk_url, headers=freshdesk_headers, timeout=5)
    if response.status_code == 200:
        print("✅ This appears to be a Freshdesk API key, not Freshsales/CRM!")
        print("You need a Freshsales CRM API key instead.")
except:
    pass 