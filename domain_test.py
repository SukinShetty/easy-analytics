import requests

API_KEY = '2IbbXJgW_QJLDOBwl7Znqw'

# Different Freshworks domain formats
domains = [
    'kambaacrm.myfreshworks.com',
    'kambaacrm.freshworks.com', 
    'kambaacrm.freshsales.io',
    'kambaacrm.freshcaller.com',
    'kambaacrm.freshservice.com'
]

headers = {'Authorization': f'Token token={API_KEY}', 'Content-Type': 'application/json'}
test_endpoint = '/crm/sales/api/deals'

print("Testing different Freshworks domain formats...")
print(f"API Key: {API_KEY[:10]}...")

for domain in domains:
    try:
        url = f'https://{domain}{test_endpoint}'
        print(f"\n=== Testing: {domain} ===")
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if 'application/json' in response.headers.get('content-type', ''):
            print("✅ JSON Response found!")
            try:
                data = response.json()
                print(f"Success! Domain: {domain}")
                print(f"Data: {type(data)} with {len(data) if isinstance(data, (list, dict)) else 'unknown'} items")
                break
            except:
                print("JSON parse error")
        elif response.status_code == 404:
            print("❌ 404 Not Found")
        elif response.status_code in [401, 403]:
            print(f"❌ {response.status_code} - Domain exists but auth issue")
        else:
            print(f"❌ {response.status_code}")
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - domain may not exist")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*50)
print("💡 Alternative approaches:")
print("1. Check your Freshworks login URL")
print("2. Look for API documentation in your Freshworks admin panel")
print("3. Contact Freshworks support for correct API endpoints") 