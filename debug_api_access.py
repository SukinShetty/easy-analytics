#!/usr/bin/env python3
"""
Debug API Access Issues
Investigate why some endpoints work while others don't
"""

import requests
import json
from datetime import datetime

def test_api_endpoint_detailed(endpoint, description):
    """Test an endpoint with detailed debugging"""
    domain = 'kambaacrm.myfreshworks.com'
    api_key = '2IbbXJgW_QJLDOBwl7Znqw'
    
    headers = {
        'Authorization': f'Token token={api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n{'='*60}")
    print(f"🔍 TESTING: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    url = f'https://{domain}{endpoint}'
    
    try:
        # Test different parameter combinations
        test_variations = [
            ('Basic', url),
            ('With pagination', f'{url}?page=1&per_page=10'),
            ('With include all', f'{url}?include=*'),
            ('With view all', f'{url}?view=all'),
            ('With filters', f'{url}?filter=all'),
            ('Different format', f'{url}.json'),
        ]
        
        for variation_name, test_url in test_variations:
            print(f"\n🧪 Testing {variation_name}: {test_url}")
            
            response = requests.get(test_url, headers=headers, timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Not specified')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Valid JSON response")
                    
                    # Analyze the response structure
                    if isinstance(data, dict):
                        print(f"   📊 Response type: Dictionary with {len(data)} keys")
                        print(f"   🔑 Keys: {list(data.keys())}")
                        
                        # Look for data arrays
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"   📋 {key}: Array with {len(value)} items")
                                if len(value) > 0 and isinstance(value[0], dict):
                                    print(f"      Sample fields: {list(value[0].keys())[:5]}")
                            elif isinstance(value, dict):
                                print(f"   📦 {key}: Object")
                        
                        # Save successful response
                        filename = f"debug_responses/{endpoint.replace('/', '_')}_{variation_name.replace(' ', '_')}.json"
                        import os
                        os.makedirs('debug_responses', exist_ok=True)
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, default=str)
                        print(f"   💾 Saved to: {filename}")
                        
                        return True
                        
                    elif isinstance(data, list):
                        print(f"   📊 Response type: Array with {len(data)} items")
                        if len(data) > 0:
                            print(f"   Sample item: {type(data[0])}")
                        return True
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
                    print(f"   First 200 chars: {response.text[:200]}")
                    
            elif response.status_code == 403:
                print(f"   🚫 403 FORBIDDEN")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                    
            elif response.status_code == 404:
                print(f"   ❌ 404 NOT FOUND")
                
            elif response.status_code == 401:
                print(f"   🔐 401 UNAUTHORIZED")
                try:
                    error_data = response.json()
                    print(f"   Auth error: {error_data}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
                    
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    return False

def check_api_permissions():
    """Check what the API key actually has permission to access"""
    print("🔐 CHECKING API KEY PERMISSIONS")
    print("=" * 60)
    
    # Test endpoints we know work
    print("\n✅ KNOWN WORKING ENDPOINTS:")
    test_api_endpoint_detailed('/crm/sales/api/appointments', 'Appointments (Known Working)')
    
    # Test problematic endpoints with different approaches
    print("\n❌ PROBLEMATIC ENDPOINTS - DETAILED TESTING:")
    
    # Try different paths for deals
    deals_endpoints = [
        '/crm/sales/api/deals',
        '/crm/sales/api/deal', 
        '/api/deals',
        '/sales/api/deals',
        '/crm/api/deals',
        '/crm/sales/deals',
        '/deals'
    ]
    
    print(f"\n🎯 TESTING DEALS ACCESS ({len(deals_endpoints)} variations):")
    for endpoint in deals_endpoints:
        success = test_api_endpoint_detailed(endpoint, f'Deals via {endpoint}')
        if success:
            print(f"   🎉 FOUND WORKING DEALS ENDPOINT: {endpoint}")
            break
    
    # Try different paths for contacts
    contacts_endpoints = [
        '/crm/sales/api/contacts',
        '/crm/sales/api/contact',
        '/api/contacts', 
        '/sales/api/contacts',
        '/crm/api/contacts',
        '/crm/sales/contacts',
        '/contacts'
    ]
    
    print(f"\n👥 TESTING CONTACTS ACCESS ({len(contacts_endpoints)} variations):")
    for endpoint in contacts_endpoints:
        success = test_api_endpoint_detailed(endpoint, f'Contacts via {endpoint}')
        if success:
            print(f"   🎉 FOUND WORKING CONTACTS ENDPOINT: {endpoint}")
            break
    
    # Try accounts/companies
    accounts_endpoints = [
        '/crm/sales/api/sales_accounts',
        '/crm/sales/api/accounts',
        '/crm/sales/api/companies',
        '/api/accounts',
        '/api/companies',
        '/sales/api/accounts',
        '/accounts',
        '/companies'
    ]
    
    print(f"\n🏢 TESTING ACCOUNTS ACCESS ({len(accounts_endpoints)} variations):")
    for endpoint in accounts_endpoints:
        success = test_api_endpoint_detailed(endpoint, f'Accounts via {endpoint}')
        if success:
            print(f"   🎉 FOUND WORKING ACCOUNTS ENDPOINT: {endpoint}")
            break

def test_api_key_validity():
    """Test if the API key itself is valid"""
    print("\n🔑 TESTING API KEY VALIDITY")
    print("=" * 60)
    
    domain = 'kambaacrm.myfreshworks.com'
    api_key = '2IbbXJgW_QJLDOBwl7Znqw'
    
    # Test with a simple endpoint
    headers = {
        'Authorization': f'Token token={api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test different auth formats
    auth_formats = [
        ('Standard Format', {'Authorization': f'Token token={api_key}'}),
        ('Basic Auth Format', {'Authorization': f'Basic {api_key}'}),
        ('Bearer Format', {'Authorization': f'Bearer {api_key}'}),
        ('API Key Header', {'X-API-Key': api_key}),
        ('Freshworks Format', {'Authorization': f'Token {api_key}'}),
    ]
    
    test_url = f'https://{domain}/crm/sales/api/appointments'
    
    for format_name, headers in auth_formats:
        print(f"\n🧪 Testing {format_name}")
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS with {format_name}")
                break
            elif response.status_code == 401:
                print(f"   🔐 Unauthorized with {format_name}")
            elif response.status_code == 403:
                print(f"   🚫 Forbidden with {format_name}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

def main():
    print("🕵️ FRESHWORKS CRM API ACCESS DEBUGGER")
    print("Investigating why some data is accessible and others aren't")
    print("=" * 80)
    
    # Test API key validity
    test_api_key_validity()
    
    # Check detailed permissions
    check_api_permissions()
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print("Check the debug_responses/ folder for successful API responses")
    print("This will help us understand:")
    print("1. If the API key format is correct")
    print("2. If there are alternative endpoints for deals/contacts")
    print("3. What the actual permission restrictions are")

if __name__ == '__main__':
    main() 