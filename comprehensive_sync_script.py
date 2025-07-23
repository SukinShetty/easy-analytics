#!/usr/bin/env python3
"""
Comprehensive Freshworks CRM Data Sync Script
Fetches ALL fields from ALL modules and stores them in PostgreSQL
"""

import requests
import psycopg2
import psycopg2.extras
import json
import os
from datetime import datetime
import time
from typing import Dict, List, Any

class ComprehensiveCRMSync:
    def __init__(self):
        # Freshworks API configuration
        self.domain = os.getenv('FRESHWORKS_DOMAIN', 'kambaacrm.myfreshworks.com')
        self.api_key = os.getenv('FRESHWORKS_API_KEY', '2IbbXJgW_QJLDOBwl7Znqw')
        self.headers = {
            'Authorization': f'Token token={self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Database configuration
        self.db_config = {
            "host": os.getenv('DB_HOST', 'localhost'),
            "port": os.getenv('DB_PORT', '5432'),
            "database": os.getenv('DB_NAME', 'tooljet_prod'),
            "user": os.getenv('DB_USER', 'postgres'),
            "password": os.getenv('DB_PASS', 'tooljet')
        }
        
        # Define all endpoints and their configurations
        self.endpoints = {
            'deals': {
                'url': f'https://{self.domain}/crm/sales/api/deals',
                'key_field': 'deals',
                'table': 'deals',
                'include': 'sales_account,contacts,products,appointments,notes,tasks,owner,creater,updater,source,deal_stage,currency,deal_pipeline,deal_payment_status,deal_product,deal_type'
            },
            'contacts': {
                'url': f'https://{self.domain}/crm/sales/api/contacts',
                'key_field': 'contacts',
                'table': 'contacts',
                'include': 'sales_accounts,owner,creater,updater,source,appointments,notes,tasks,deals,campaigns,lifecycle_stage,contact_status'
            },
            'accounts': {
                'url': f'https://{self.domain}/crm/sales/api/sales_accounts',
                'key_field': 'sales_accounts',
                'table': 'accounts',
                'include': 'contacts,owner,creater,updater,parent_sales_account,appointments,notes,tasks,deals,industry_type,business_type'
            },
            'sales_activities': {
                'url': f'https://{self.domain}/crm/sales/api/sales_activities',
                'key_field': 'sales_activities',
                'table': 'sales_activities',
                'include': 'targetable,owner,creater,updater,outcome'
            },
            'appointments': {
                'url': f'https://{self.domain}/crm/sales/api/appointments',
                'key_field': 'appointments',
                'table': 'appointments',
                'include': 'appointment_attendees,targetable,creater,outcome'
            },
            'tasks': {
                'url': f'https://{self.domain}/crm/sales/api/tasks',
                'key_field': 'tasks',
                'table': 'tasks',
                'include': 'targetable,owner,creater,updater,outcome,task_type'
            },
            'products': {
                'url': f'https://{self.domain}/crm/sales/api/products',
                'key_field': 'products',
                'table': 'products',
                'include': 'currency,product_category,vendor,owner,creater,updater'
            },
            'leads': {
                'url': f'https://{self.domain}/crm/sales/api/leads',
                'key_field': 'leads',
                'table': 'leads',
                'include': 'lead_source,lead_status,owner,creater,updater,source,campaign,territory,industry_type,business_type'
            },
            'notes': {
                'url': f'https://{self.domain}/crm/sales/api/notes',
                'key_field': 'notes',
                'table': 'notes',
                'include': 'targetable,creater,updater'
            },
            'campaigns': {
                'url': f'https://{self.domain}/crm/sales/api/campaigns',
                'key_field': 'campaigns',
                'table': 'campaigns',
                'include': 'owner,parent_campaign'
            }
        }
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def fetch_all_data(self, module: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all data from a module with pagination"""
        all_data = []
        page = 1
        per_page = 100
        
        print(f"\n📥 Fetching {module}...")
        
        while True:
            try:
                # Build URL with parameters
                url = f"{config['url']}?page={page}&per_page={per_page}"
                if 'include' in config:
                    url += f"&include={config['include']}"
                
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 403:
                    print(f"❌ Access denied for {module}")
                    break
                elif response.status_code == 404:
                    print(f"❌ Endpoint not found for {module}")
                    break
                elif response.status_code != 200:
                    print(f"❌ Error {response.status_code} for {module}")
                    break
                
                data = response.json()
                
                # Extract records based on the key field
                records = []
                if config['key_field'] in data:
                    records = data[config['key_field']]
                elif isinstance(data, list):
                    records = data
                elif 'data' in data:
                    records = data['data']
                
                if not records:
                    print(f"✅ {module}: Total {len(all_data)} records fetched")
                    break
                
                all_data.extend(records)
                print(f"  Page {page}: {len(records)} records (Total: {len(all_data)})")
                
                # Check if there are more pages
                if 'meta' in data:
                    total_pages = data['meta'].get('total_pages', 1)
                    if page >= total_pages:
                        break
                elif len(records) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching {module}: {e}")
                break
        
        return all_data
    
    def prepare_value(self, value: Any, field_type: str = None) -> Any:
        """Prepare value for database insertion"""
        if value is None:
            return None
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # Check if it's a datetime string
            if 'T' in value and any(tz in value for tz in ['Z', '+', '-']):
                try:
                    # Parse ISO format datetime
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return value
            return value
        else:
            return str(value)
    
    def sync_module(self, module: str, config: Dict[str, Any], data: List[Dict[str, Any]]) -> int:
        """Sync data to database"""
        if not data:
            return 0
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            # Get the first record to understand structure
            sample_record = data[0]
            
            # Build dynamic INSERT query based on actual fields
            fields = list(sample_record.keys())
            
            # Filter out fields that don't exist in our schema
            # This is a safety measure - in production, you'd want all fields
            table_name = config['table']
            
            # Build the INSERT query
            placeholders = ', '.join(['%s'] * len(fields))
            columns = ', '.join([f'"{field}"' for field in fields])
            
            # Build UPDATE clause for upsert
            update_clause = ', '.join([
                f'"{field}" = EXCLUDED."{field}"' 
                for field in fields 
                if field != 'id'
            ])
            
            insert_query = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                {update_clause}
            """
            
            # Insert all records
            success_count = 0
            for record in data:
                try:
                    # Prepare values in the same order as fields
                    values = []
                    for field in fields:
                        value = record.get(field)
                        values.append(self.prepare_value(value))
                    
                    cur.execute(insert_query, values)
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️  Error inserting record {record.get('id', 'unknown')}: {e}")
                    conn.rollback()
                    continue
            
            conn.commit()
            print(f"✅ {module}: {success_count}/{len(data)} records synced")
            return success_count
            
        except Exception as e:
            print(f"❌ Error syncing {module}: {e}")
            conn.rollback()
            return 0
        finally:
            cur.close()
            conn.close()
    
    def run_full_sync(self):
        """Run complete sync for all modules"""
        print("🚀 Starting Comprehensive Freshworks CRM Sync")
        print(f"Domain: {self.domain}")
        print(f"Database: {self.db_config['database']}")
        
        total_synced = 0
        sync_summary = {}
        
        for module, config in self.endpoints.items():
            # Fetch data
            data = self.fetch_all_data(module, config)
            
            if data:
                # Save raw data for analysis
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"raw_data/{module}_{timestamp}.json"
                os.makedirs('raw_data', exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"  💾 Raw data saved to {filename}")
                
                # Sync to database
                count = self.sync_module(module, config, data)
                total_synced += count
                sync_summary[module] = {
                    'fetched': len(data),
                    'synced': count,
                    'status': '✅' if count > 0 else '⚠️'
                }
            else:
                sync_summary[module] = {
                    'fetched': 0,
                    'synced': 0,
                    'status': '❌'
                }
        
        # Print summary
        print("\n" + "="*60)
        print("📊 SYNC SUMMARY")
        print("="*60)
        for module, stats in sync_summary.items():
            print(f"{stats['status']} {module}: Fetched {stats['fetched']}, Synced {stats['synced']}")
        print(f"\n✅ Total records synced: {total_synced}")
        
        # Save sync log
        log_filename = f"sync_logs/sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('sync_logs', exist_ok=True)
        
        with open(log_filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'domain': self.domain,
                'summary': sync_summary,
                'total_synced': total_synced
            }, f, indent=2)
        
        print(f"\n📝 Sync log saved to {log_filename}")

def main():
    # First, ensure the database schema exists
    print("📋 Checking database schema...")
    print("Please ensure you've run the comprehensive_db_schema.sql file first!")
    print("Run: psql -U postgres -d tooljet_prod -f comprehensive_db_schema.sql")
    
    response = input("\nHave you created the database schema? (y/n): ")
    if response.lower() != 'y':
        print("Please create the schema first, then run this sync script.")
        return
    
    # Run the sync
    syncer = ComprehensiveCRMSync()
    syncer.run_full_sync()

if __name__ == '__main__':
    main() 