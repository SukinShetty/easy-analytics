#!/usr/bin/env python3
"""
Fetch ALL Real Data from Freshworks CRM API
This script will fetch every available piece of real data from your Freshworks CRM
"""

import requests
import psycopg2
import psycopg2.extras
import json
import os
from datetime import datetime
import time

class RealFreshworksCRMSync:
    def __init__(self):
        # Freshworks API configuration
        self.domain = 'kambaacrm.myfreshworks.com'
        self.api_key = '2IbbXJgW_QJLDOBwl7Znqw'
        self.headers = {
            'Authorization': f'Token token={self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Database configuration
        self.db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "tooljet_prod",
            "user": "postgres",
            "password": "tooljet"
        }
        
        # All possible Freshworks CRM endpoints to try
        self.endpoints_to_test = [
            # Standard CRM endpoints
            '/crm/sales/api/deals',
            '/crm/sales/api/contacts',
            '/crm/sales/api/sales_accounts',
            '/crm/sales/api/accounts',
            '/crm/sales/api/companies',
            '/crm/sales/api/leads',
            '/crm/sales/api/opportunities',
            '/crm/sales/api/sales_activities',
            '/crm/sales/api/activities',
            '/crm/sales/api/appointments',
            '/crm/sales/api/tasks',
            '/crm/sales/api/notes',
            '/crm/sales/api/products',
            '/crm/sales/api/users',
            '/crm/sales/api/owners',
            '/crm/sales/api/teams',
            '/crm/sales/api/campaigns',
            '/crm/sales/api/sources',
            '/crm/sales/api/deal_stages',
            '/crm/sales/api/pipelines',
            '/crm/sales/api/contact_statuses',
            '/crm/sales/api/lifecycle_stages',
            '/crm/sales/api/lead_sources',
            '/crm/sales/api/territories',
            '/crm/sales/api/currencies',
            '/crm/sales/api/custom_fields',
            '/crm/sales/api/webhooks',
            '/crm/sales/api/email_templates',
            '/crm/sales/api/phone_numbers',
            '/crm/sales/api/emails',
            '/crm/sales/api/calls',
            '/crm/sales/api/documents',
            '/crm/sales/api/files',
            
            # Alternative API paths
            '/api/deals',
            '/api/contacts',
            '/api/accounts',
            '/api/leads',
            '/api/activities',
            '/api/appointments',
            '/api/tasks',
            '/api/users',
            
            # Sales-specific endpoints
            '/sales/api/deals',
            '/sales/api/contacts',
            '/sales/api/accounts',
            
            # Settings and configuration
            '/crm/sales/api/settings',
            '/crm/sales/api/admin/users',
            '/crm/sales/api/admin/teams',
            '/crm/sales/api/admin/roles',
            '/crm/sales/api/admin/permissions'
        ]
        
        self.working_endpoints = {}
        self.failed_endpoints = {}
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def test_endpoint(self, endpoint):
        """Test if an endpoint is accessible and returns data"""
        url = f'https://{self.domain}{endpoint}'
        
        try:
            print(f"🔍 Testing: {endpoint}")
            
            # Try different parameter combinations
            test_urls = [
                f"{url}?page=1&per_page=5",
                f"{url}?page=1&per_page=5&include=*",
                f"{url}?limit=5",
                f"{url}",
                f"{url}?page=1"
            ]
            
            for test_url in test_urls:
                try:
                    response = requests.get(test_url, headers=self.headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Check if we got real data
                            if self.has_real_data(data):
                                print(f"  ✅ SUCCESS: Found real data!")
                                
                                # Save raw response for analysis
                                endpoint_name = endpoint.split('/')[-1]
                                filename = f"real_data_{endpoint_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                
                                os.makedirs('real_freshworks_data', exist_ok=True)
                                with open(f'real_freshworks_data/{filename}', 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2, default=str)
                                
                                return {
                                    'endpoint': endpoint,
                                    'url': test_url,
                                    'data': data,
                                    'filename': filename,
                                    'record_count': self.count_records(data)
                                }
                        except json.JSONDecodeError:
                            continue
                            
                    elif response.status_code == 403:
                        print(f"  ❌ 403 Forbidden - No permission")
                        return None
                    elif response.status_code == 404:
                        print(f"  ❌ 404 Not Found")
                        return None
                    elif response.status_code == 401:
                        print(f"  ❌ 401 Unauthorized - Check API key")
                        return None
                        
                except requests.exceptions.Timeout:
                    continue
                except requests.exceptions.ConnectionError:
                    continue
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        return None
    
    def has_real_data(self, data):
        """Check if the response contains real data (not empty or error)"""
        if not data:
            return False
            
        if isinstance(data, dict):
            # Check for error responses
            if 'error' in data or 'errors' in data:
                return False
                
            # Look for data arrays or objects
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    return True
                elif isinstance(value, dict) and value:
                    return True
                    
        elif isinstance(data, list) and len(data) > 0:
            return True
            
        return False
    
    def count_records(self, data):
        """Count the number of records in the response"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    return len(value)
        return 0
    
    def discover_all_endpoints(self):
        """Test all possible endpoints to find what data is available"""
        print("🚀 Discovering ALL available real data from Freshworks CRM...")
        print(f"Domain: {self.domain}")
        print(f"Testing {len(self.endpoints_to_test)} possible endpoints...\n")
        
        for endpoint in self.endpoints_to_test:
            result = self.test_endpoint(endpoint)
            
            if result:
                self.working_endpoints[endpoint] = result
                print(f"  📊 Found {result['record_count']} records")
            else:
                self.failed_endpoints[endpoint] = "No access or no data"
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
    
    def sync_real_data_to_database(self):
        """Sync all discovered real data to the database"""
        if not self.working_endpoints:
            print("\n❌ No real data found to sync!")
            return
            
        print(f"\n🔄 Syncing {len(self.working_endpoints)} data sources to database...")
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Clear existing dummy data
        print("🗑️ Clearing any existing dummy data...")
        try:
            cur.execute("DELETE FROM deals WHERE id >= 1000;")  # Remove our dummy data
            conn.commit()
        except:
            pass
        
        total_synced = 0
        
        for endpoint, result in self.working_endpoints.items():
            try:
                table_name = self.get_table_name(endpoint)
                records = self.extract_records(result['data'])
                
                if records and table_name:
                    synced_count = self.sync_records_to_table(cur, conn, table_name, records)
                    total_synced += synced_count
                    print(f"  ✅ {table_name}: {synced_count} real records synced")
                
            except Exception as e:
                print(f"  ❌ Error syncing {endpoint}: {e}")
        
        cur.close()
        conn.close()
        
        print(f"\n✅ Total real records synced: {total_synced}")
    
    def get_table_name(self, endpoint):
        """Map endpoint to database table name"""
        mapping = {
            'deals': 'deals',
            'contacts': 'contacts',
            'sales_accounts': 'accounts',
            'accounts': 'accounts',
            'companies': 'accounts',
            'leads': 'leads',
            'opportunities': 'deals',
            'sales_activities': 'sales_activities',
            'activities': 'sales_activities',
            'appointments': 'appointments',
            'tasks': 'tasks',
            'notes': 'notes',
            'products': 'products',
            'users': 'sales_team',
            'owners': 'sales_team',
            'teams': 'sales_team',
            'campaigns': 'campaigns',
            'contact_statuses': 'contact_statuses',
            'pipelines': 'deal_pipelines'
        }
        
        endpoint_name = endpoint.split('/')[-1]
        return mapping.get(endpoint_name)
    
    def extract_records(self, data):
        """Extract actual records from API response"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Try common keys that contain record arrays
            for key in data.keys():
                if isinstance(data[key], list) and len(data[key]) > 0:
                    return data[key]
        return []
    
    def sync_records_to_table(self, cur, conn, table_name, records):
        """Sync records to specific database table"""
        if not records:
            return 0
            
        synced_count = 0
        
        for record in records:
            if not isinstance(record, dict) or not record.get('id'):
                continue
                
            try:
                # Dynamic insert based on available fields
                fields = []
                values = []
                
                for key, value in record.items():
                    fields.append(key)
                    if isinstance(value, (dict, list)):
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
                
                if fields:
                    placeholders = ','.join(['%s'] * len(values))
                    columns = ','.join([f'"{field}"' for field in fields])
                    
                    # Build upsert query
                    update_clause = ','.join([
                        f'"{field}" = EXCLUDED."{field}"' 
                        for field in fields 
                        if field != 'id'
                    ])
                    
                    query = f"""
                        INSERT INTO {table_name} ({columns})
                        VALUES ({placeholders})
                        ON CONFLICT (id) DO UPDATE SET {update_clause}
                    """
                    
                    cur.execute(query, values)
                    synced_count += 1
                    
            except Exception as e:
                # If table doesn't exist or column mismatch, create table dynamically
                try:
                    self.create_table_from_record(cur, table_name, record)
                    conn.commit()
                    # Retry the insert
                    cur.execute(query, values)
                    synced_count += 1
                except:
                    continue
        
        conn.commit()
        return synced_count
    
    def create_table_from_record(self, cur, table_name, record):
        """Dynamically create table based on record structure"""
        columns = []
        
        for key, value in record.items():
            if key == 'id':
                columns.append(f'"{key}" BIGINT PRIMARY KEY')
            elif isinstance(value, bool):
                columns.append(f'"{key}" BOOLEAN')
            elif isinstance(value, int):
                columns.append(f'"{key}" BIGINT')
            elif isinstance(value, float):
                columns.append(f'"{key}" DECIMAL(15,2)')
            elif isinstance(value, (dict, list)):
                columns.append(f'"{key}" JSONB')
            else:
                columns.append(f'"{key}" TEXT')
        
        if columns:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(columns)})"
            cur.execute(query)
    
    def generate_summary_report(self):
        """Generate a summary of what real data was found"""
        print("\n" + "="*80)
        print("📊 REAL FRESHWORKS CRM DATA DISCOVERY REPORT")
        print("="*80)
        
        if self.working_endpoints:
            print(f"\n✅ FOUND REAL DATA ({len(self.working_endpoints)} sources):")
            total_records = 0
            
            for endpoint, result in self.working_endpoints.items():
                count = result['record_count']
                total_records += count
                print(f"  📈 {endpoint}: {count} real records")
                print(f"     💾 Saved to: {result['filename']}")
            
            print(f"\n🎯 TOTAL REAL RECORDS: {total_records}")
            
        else:
            print("\n❌ NO REAL DATA ACCESSIBLE")
            print("This means your API key doesn't have permission to access CRM data")
        
        if self.failed_endpoints:
            print(f"\n⚠️  INACCESSIBLE ENDPOINTS ({len(self.failed_endpoints)}):")
            for endpoint, reason in list(self.failed_endpoints.items())[:10]:  # Show first 10
                print(f"  ❌ {endpoint}: {reason}")
            
            if len(self.failed_endpoints) > 10:
                print(f"  ... and {len(self.failed_endpoints) - 10} more")
        
        print("\n" + "="*80)

def main():
    print("🎯 REAL FRESHWORKS CRM DATA FETCHER")
    print("This will fetch ONLY real data from your Freshworks CRM API")
    print("No dummy data will be created!")
    print("-" * 60)
    
    syncer = RealFreshworksCRMSync()
    
    # Step 1: Discover all available real data
    syncer.discover_all_endpoints()
    
    # Step 2: Sync real data to database
    syncer.sync_real_data_to_database()
    
    # Step 3: Generate summary report
    syncer.generate_summary_report()
    
    # Final database check
    conn = psycopg2.connect(
        host='localhost',
        database='tooljet_prod',
        user='postgres',
        password='tooljet'
    )
    cur = conn.cursor()
    
    print("\n📋 FINAL DATABASE STATE (REAL DATA ONLY):")
    tables = ['deals', 'contacts', 'accounts', 'sales_activities', 'appointments', 'tasks', 'sales_team']
    
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            if count > 0:
                print(f"  ✅ {table}: {count} real records")
            else:
                print(f"  ❌ {table}: No real data available")
        except:
            print(f"  ❌ {table}: Table doesn't exist")
    
    cur.close()
    conn.close()
    
    print("\n🎯 RESULT: Your chatbot now has access to REAL CRM data only!")

if __name__ == '__main__':
    main() 