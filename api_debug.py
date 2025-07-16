import requests

DOMAIN = 'kambaacrm.myfreshworks.com'
API_KEY = '2IbbXJgW_QJLDOBwl7Znqw'

print("Testing Freshworks CRM API endpoints...")
print(f"Base URL: {DOMAIN}/crm/sales")
headers = {'Authorization': f'Token token={API_KEY}', 'Content-Type': 'application/json'}

# Correct Freshworks CRM API patterns based on user's domain
api_endpoints = [
    '/crm/sales/api/deals',
    '/crm/sales/api/contacts', 
    '/crm/sales/api/accounts',
    '/crm/sales/api/products',
    '/crm/sales/api/sales_activities',
    '/crm/sales/api/leads',
    '/crm/sales/api/tasks'
]

print(f"Domain: {DOMAIN}")
print(f"API Key: {API_KEY[:10]}...")

working_endpoints = []

for endpoint in api_endpoints:
    try:
        url = f'https://{DOMAIN}{endpoint}'
        print(f"\n=== Testing: {endpoint} ===")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('content-type', ''):
                print("✅ JSON Response!")
                working_endpoints.append(endpoint)
                try:
                    data = response.json()
                    print(f"Data structure: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  {key}: Array with {len(value)} items")
                            else:
                                print(f"  {key}: {type(value)}")
                    elif isinstance(data, list):
                        print(f"Array length: {len(data)}")
                        if data and isinstance(data[0], dict):
                            print(f"First item keys: {list(data[0].keys())}")
                except Exception as e:
                    print(f"JSON parse error: {e}")
            else:
                print("❌ HTML Response (not API endpoint)")
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Check API key permissions")
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API access may not be enabled")
        elif response.status_code == 404:
            print("❌ 404 Not Found - Endpoint doesn't exist")
        else:
            print(f"❌ Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

print("\n" + "="*60)
print("SUMMARY:")
if working_endpoints:
    print("✅ Working API endpoints found:")
    for endpoint in working_endpoints:
        print(f"   {endpoint}")
    print(f"✅ Domain: {DOMAIN}")
    print(f"✅ Auth: Token token={{API_KEY}}")
else:
    print("❌ No working JSON API endpoints found")
    print("💡 Next steps:")
    print("1. Check Freshworks Admin → Settings → API Settings")
    print("2. Verify API key has proper CRM permissions")
    print("3. Enable API access for your account") 