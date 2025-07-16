#!/usr/bin/env python3
"""
Simple Freshworks Data Sync Test for Kambaa CRM
Tests connection and shows sample data without database dependencies
"""

import os
import requests
import json
from datetime import datetime

# Your Kambaa CRM credentials
FRESHWORKS_DOMAIN = "kambaacrm.myfreshworks.com"
FRESHWORKS_API_KEY = "2IbbXJgW_QJLDOBwl7Znqw"

# API Configuration
base_url = f"https://{FRESHWORKS_DOMAIN}/crm/sales/api"
headers = {
    "Authorization": f"Token token={FRESHWORKS_API_KEY}",
    "Content-Type": "application/json"
}

def test_connection():
    """Test Freshworks API connection"""
    print("🔍 Testing Freshworks API connection...")
    print(f"   Domain: {FRESHWORKS_DOMAIN}")
    print(f"   Base URL: {base_url}")
    
    try:
        # Try to fetch contacts
        response = requests.get(
            f"{base_url}/contacts",
            headers=headers,
            params={"page": 1, "per_page": 5},
            timeout=10
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully connected to Freshworks API!")
            data = response.json()
            
            # Show sample data
            if 'contacts' in data:
                print(f"\n📊 Found {len(data['contacts'])} contacts (showing first 5)")
                for i, contact in enumerate(data['contacts'][:5], 1):
                    print(f"   {i}. {contact.get('first_name', '')} {contact.get('last_name', '')} - {contact.get('email', 'No email')}")
            
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed! Check your API key.")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.SSLError as e:
        print("❌ SSL Error - trying without SSL verification...")
        try:
            # Retry without SSL verification
            response = requests.get(
                f"{base_url}/contacts",
                headers=headers,
                params={"page": 1, "per_page": 5},
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                print("⚠️  Connected without SSL verification")
                print("   Note: This is not recommended for production")
                return True
        except Exception as e2:
            print(f"❌ Still failed: {str(e2)}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
    
    return False

def fetch_sample_data():
    """Fetch and display sample data from each entity"""
    print("\n📊 Fetching sample data from Kambaa CRM...")
    
    entities = {
        'contacts': 'contacts',
        'sales_accounts': 'accounts',
        'products': 'products', 
        'deals': 'deals',
        'sales_activities': 'activities'
    }
    
    for endpoint, display_name in entities.items():
        print(f"\n🔍 Fetching {display_name}...")
        try:
            response = requests.get(
                f"{base_url}/{endpoint}",
                headers=headers,
                params={"page": 1, "per_page": 3},
                timeout=10,
                verify=False  # Disable SSL verification due to handshake issues
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Different endpoints return data differently
                items = data.get(endpoint, data.get(display_name, []))
                if isinstance(data, list):
                    items = data
                
                print(f"   ✅ Found {len(items)} {display_name}")
                
                # Show sample item
                if items and len(items) > 0:
                    print(f"   Sample: {json.dumps(items[0], indent=2)[:200]}...")
            else:
                print(f"   ⚠️  Could not fetch {display_name}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error fetching {display_name}: {str(e)}")

def main():
    print("🚀 Kambaa CRM - Freshworks Connection Test")
    print("=" * 50)
    
    # Disable SSL warnings for this test
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test connection
    if test_connection():
        # Fetch sample data
        fetch_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ Connection test complete!")
        print("\nTo sync this data to your database:")
        print("1. Make sure Docker services are running")
        print("2. Install psycopg2-binary manually:")
        print("   pip install psycopg2-binary==2.9.5")
        print("3. Run the full sync script")
    else:
        print("\n❌ Could not connect to Freshworks")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Ensure your Freshworks account has API access enabled")
        print("3. Try accessing: https://kambaacrm.myfreshworks.com")

if __name__ == "__main__":
    main() 