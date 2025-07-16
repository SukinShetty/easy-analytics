import requests

DOMAIN = 'kambaacrm.myfreshworks.com'
API_KEY = '2IbbXJgW_QJLDOBwl7Znqw'

print("Finding all available Freshworks CRM endpoints...")
headers = {'Authorization': f'Token token={API_KEY}', 'Content-Type': 'application/json'}

# Test different endpoint names that might exist
possible_endpoints = [
    # Core CRM entities
    '/crm/sales/api/deals',
    '/crm/sales/api/contacts',
    '/crm/sales/api/companies',  # Sometimes called companies instead of accounts
    '/crm/sales/api/accounts',
    '/crm/sales/api/leads',
    
    # Product related
    '/crm/sales/api/products',
    '/crm/sales/api/product_catalog',
    '/crm/sales/api/inventory',
    
    # Activities & Tasks (we know these work)
    '/crm/sales/api/sales_activities',
    '/crm/sales/api/tasks',
    '/crm/sales/api/activities',
    '/crm/sales/api/events',
    '/crm/sales/api/appointments',
    
    # Other common entities
    '/crm/sales/api/notes',
    '/crm/sales/api/calls',
    '/crm/sales/api/emails',
    '/crm/sales/api/campaigns',
    '/crm/sales/api/pipelines'
]

working_endpoints = []
permission_needed = []
not_found = []

for endpoint in possible_endpoints:
    try:
        url = f'https://{DOMAIN}{endpoint}'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {endpoint} - Working!")
            working_endpoints.append(endpoint)
            try:
                data = response.json()
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"   {key}: {len(value)} items")
            except:
                pass
                
        elif response.status_code == 403:
            print(f"🔐 {endpoint} - Needs Permission")
            permission_needed.append(endpoint)
            
        elif response.status_code == 404:
            print(f"❌ {endpoint} - Not Found")
            not_found.append(endpoint)
            
        else:
            print(f"❓ {endpoint} - Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ {endpoint} - Error: {e}")

print("\n" + "="*60)
print("📊 FINAL SUMMARY:")
print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
for endpoint in working_endpoints:
    print(f"   {endpoint}")

print(f"\n🔐 NEED PERMISSIONS ({len(permission_needed)}):")
for endpoint in permission_needed:
    print(f"   {endpoint}")

print(f"\n❌ NOT AVAILABLE ({len(not_found)}):")
for endpoint in not_found[:5]:  # Show only first 5
    print(f"   {endpoint}")

print("\n💡 NEXT STEPS:")
print("1. Enable API permissions in Freshworks Admin → Settings → API")
print("2. Grant access to: deals, contacts, leads")
print("3. For now, we can build the app with: sales_activities, tasks")
print("4. Add more endpoints once permissions are granted") 