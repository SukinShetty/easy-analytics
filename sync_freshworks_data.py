#!/usr/bin/env python3
"""
Sync real data from Freshworks CRM to local PostgreSQL database
This allows the chatbot to query your actual CRM data
"""

import os
import sys
import time
import requests
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class FreshworksSyncer:
    def __init__(self):
        # Freshworks API configuration
        self.freshworks_domain = os.getenv('FRESHWORKS_DOMAIN', '').strip()
        self.freshworks_api_key = os.getenv('FRESHWORKS_API_KEY', '').strip()
        
        # Validate credentials
        if not self.freshworks_domain or 'your' in self.freshworks_domain:
            print("❌ ERROR: Please set your actual FRESHWORKS_DOMAIN in .env file")
            print("   Example: FRESHWORKS_DOMAIN=mycompany.freshworks.com")
            sys.exit(1)
            
        if not self.freshworks_api_key or 'your' in self.freshworks_api_key:
            print("❌ ERROR: Please set your actual FRESHWORKS_API_KEY in .env file")
            print("   You can find this in Freshworks Settings > API Settings")
            sys.exit(1)
        
        # Clean up domain if needed
        if self.freshworks_domain.endswith('.myfreshworks.com'):
            # Domain already includes full URL, use as is
            self.base_url = f"https://{self.freshworks_domain}/crm/sales/api"
        elif self.freshworks_domain.endswith('.freshworks.com'):
            # Domain already includes .freshworks.com
            self.base_url = f"https://{self.freshworks_domain}/crm/sales/api"
        else:
            # Domain needs .freshworks.com appended
            self.base_url = f"https://{self.freshworks_domain}.freshworks.com/crm/sales/api"
        self.headers = {
            "Authorization": f"Token token={self.freshworks_api_key}",
            "Content-Type": "application/json"
        }
        
        # Database configuration
        self.db_config = {
            "host": os.getenv('PG_HOST', 'localhost'),
            "port": os.getenv('PG_PORT', '5432'),
            "database": os.getenv('PG_DB', 'tooljet_prod'),
            "user": os.getenv('PG_USER', 'postgres'),
            "password": os.getenv('PG_PASS', 'tooljet')
        }
        
        print(f"✅ Configured to sync from: {self.freshworks_domain}.freshworks.com")
    
    def test_connection(self):
        """Test Freshworks API connection"""
        print("\n🔍 Testing Freshworks API connection...")
        
        try:
            # Try to fetch a small amount of data
            response = requests.get(
                f"{self.base_url}/contacts/view/1",  # Get default view
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Successfully connected to Freshworks API!")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed! Check your API key.")
                return False
            else:
                print(f"❌ API returned status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def setup_database(self):
        """Ensure database tables exist"""
        print("\n📊 Setting up database tables...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Read and execute schema
            with open('db_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            cur.execute(schema_sql)
            conn.commit()
            
            print("✅ Database tables ready!")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            return False
    
    def fetch_all_pages(self, endpoint, entity_name):
        """Fetch all pages of data from an endpoint"""
        all_data = []
        page = 1
        
        while True:
            url = f"{self.base_url}/{endpoint}"
            params = {"page": page, "per_page": 100}
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"⚠️  API error for {entity_name}: {response.status_code}")
                    break
                
                data = response.json()
                
                # Different endpoints return data in different formats
                if entity_name in data:
                    items = data[entity_name]
                elif 'contacts' in data:  # Some endpoints nest differently
                    items = data['contacts']
                elif 'deals' in data:
                    items = data['deals']
                else:
                    items = data if isinstance(data, list) else []
                
                if not items:
                    break
                
                all_data.extend(items)
                print(f"   Fetched page {page} ({len(items)} items)")
                
                # Check if there are more pages
                if 'meta' in data and data['meta'].get('total_pages', 1) <= page:
                    break
                elif len(items) < 100:  # Less than full page means we're done
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️  Error fetching {entity_name} page {page}: {str(e)}")
                break
        
        return all_data
    
    def sync_contacts(self):
        """Sync contacts from Freshworks"""
        print("\n👥 Syncing contacts...")
        
        contacts = self.fetch_all_pages("contacts", "contacts")
        
        if not contacts:
            print("   No contacts found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for contact in contacts:
            transformed.append({
                'id': contact.get('id'),
                'first_name': contact.get('first_name', ''),
                'last_name': contact.get('last_name', ''),
                'email': contact.get('email', '')
            })
        
        # Insert into database
        return self.upsert_data('contacts', transformed)
    
    def sync_accounts(self):
        """Sync accounts/companies from Freshworks"""
        print("\n🏢 Syncing accounts...")
        
        accounts = self.fetch_all_pages("sales_accounts", "sales_accounts")
        
        if not accounts:
            print("   No accounts found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for account in accounts:
            transformed.append({
                'id': account.get('id'),
                'name': account.get('name', ''),
                'industry': account.get('industry_type', {}).get('name', '') if account.get('industry_type') else ''
            })
        
        return self.upsert_data('accounts', transformed)
    
    def sync_products(self):
        """Sync products from Freshworks"""
        print("\n📦 Syncing products...")
        
        products = self.fetch_all_pages("products", "products")
        
        if not products:
            print("   No products found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for product in products:
            # Handle different price field names
            price = product.get('unit_price') or product.get('price') or 0
            
            transformed.append({
                'id': product.get('id'),
                'name': product.get('name', ''),
                'price': float(price) if price else 0.0
            })
        
        return self.upsert_data('products', transformed)
    
    def sync_deals(self):
        """Sync deals from Freshworks"""
        print("\n💰 Syncing deals...")
        
        deals = self.fetch_all_pages("deals", "deals")
        
        if not deals:
            print("   No deals found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for deal in deals:
            # Extract IDs from nested objects
            product_id = None
            if deal.get('products') and len(deal['products']) > 0:
                product_id = deal['products'][0].get('id')
            
            account_id = deal.get('sales_account', {}).get('id')
            
            contact_id = None
            if deal.get('contacts') and len(deal['contacts']) > 0:
                contact_id = deal['contacts'][0].get('id')
            
            # Parse amount
            amount = deal.get('amount') or 0
            if isinstance(amount, str):
                amount = float(amount.replace(',', ''))
            
            transformed.append({
                'id': deal.get('id'),
                'name': deal.get('name', ''),
                'amount': float(amount),
                'close_date': deal.get('expected_close_date') or deal.get('closed_date'),
                'product_id': product_id,
                'account_id': account_id,
                'contact_id': contact_id
            })
        
        return self.upsert_data('deals', transformed)
    
    def sync_sales_team(self):
        """Sync sales team/owners from Freshworks"""
        print("\n👥 Syncing sales team...")
        
        # Use the selector endpoint for owners/users
        try:
            response = requests.get(
                f"{self.base_url}/selector/owners",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   ⚠️  API error: {response.status_code}")
                return 0
            
            data = response.json()
            users = data.get('users', [])
            
            if not users:
                print("   No sales team data found")
                return 0
            
            # Transform data
            transformed = []
            for user in users:
                transformed.append({
                    'id': user.get('id'),
                    'display_name': user.get('display_name', ''),
                    'email': user.get('email', ''),
                    'is_active': user.get('is_active', False),
                    'work_number': user.get('work_number'),
                    'mobile_number': user.get('mobile_number')
                })
            
            return self.upsert_data('sales_team', transformed)
            
        except Exception as e:
            print(f"   ❌ Error fetching sales team: {str(e)}")
            return 0

    def sync_contact_statuses(self):
        """Sync contact statuses/pipeline stages from Freshworks"""
        print("\n📊 Syncing contact statuses...")
        
        try:
            response = requests.get(
                f"{self.base_url}/selector/contact_statuses",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   ⚠️  API error: {response.status_code}")
                return 0
            
            data = response.json()
            statuses = data.get('contact_statuses', [])
            
            if not statuses:
                print("   No contact statuses found")
                return 0
            
            # Transform data
            transformed = []
            for status in statuses:
                transformed.append({
                    'id': status.get('id'),
                    'name': status.get('name', ''),
                    'position': status.get('position', 0),
                    'partial': status.get('partial', False),
                    'forecast_type': status.get('forecast_type', ''),
                    'lifecycle_stage_id': status.get('lifecycle_stage_id')
                })
            
            return self.upsert_data('contact_statuses', transformed)
            
        except Exception as e:
            print(f"   ❌ Error fetching contact statuses: {str(e)}")
            return 0

    def sync_appointments(self):
        """Sync appointments/meetings from Freshworks"""
        print("\n📅 Syncing appointments...")
        
        appointments = self.fetch_all_pages("appointments", "appointments")
        
        if not appointments:
            print("   No appointments found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for appointment in appointments:
            transformed.append({
                'id': appointment.get('id'),
                'title': appointment.get('title', ''),
                'description': appointment.get('description', ''),
                'location': appointment.get('location', ''),
                'from_date': appointment.get('from_date'),
                'end_date': appointment.get('end_date'),
                'is_allday': appointment.get('is_allday', False),
                'time_zone': appointment.get('time_zone', ''),
                'provider': appointment.get('provider', ''),
                'creater_id': appointment.get('creater_id'),
                'created_at': appointment.get('created_at'),
                'updated_at': appointment.get('updated_at'),
                'outcome_id': appointment.get('outcome_id'),
                'conference_id': appointment.get('conference_id')
            })
        
        return self.upsert_data('appointments', transformed)

    def sync_tasks(self):
        """Sync tasks from Freshworks"""
        print("\n📋 Syncing tasks...")
        
        tasks = self.fetch_all_pages("tasks", "tasks")
        
        if not tasks:
            print("   No tasks found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for task in tasks:
            transformed.append({
                'id': task.get('id'),
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'due_date': task.get('due_date'),
                'is_completed': task.get('is_completed', False),
                'created_at': task.get('created_at'),
                'updated_at': task.get('updated_at'),
                'creater_id': task.get('creater_id'),
                'task_type_id': task.get('task_type_id'),
                'priority': task.get('priority')
            })
        
        return self.upsert_data('tasks', transformed)

    def sync_activities(self):
        """Sync sales activities from Freshworks"""
        print("\n📋 Syncing sales activities...")
        
        activities = self.fetch_all_pages("sales_activities", "sales_activities")
        
        if not activities:
            print("   No activities found or error occurred")
            return 0
        
        # Transform data
        transformed = []
        for activity in activities:
            transformed.append({
                'id': activity.get('id'),
                'title': activity.get('title', ''),
                'activity_type': activity.get('type', ''),
                'targetable_type': activity.get('targetable_type', ''),
                'targetable_id': activity.get('targetable_id'),
                'start_date': activity.get('start_date'),
                'end_date': activity.get('end_date'),
                'created_at': activity.get('created_at'),
                'updated_at': activity.get('updated_at'),
                'creater_id': activity.get('creater_id'),
                'outcome': activity.get('outcome', {}).get('name', '') if activity.get('outcome') else ''
            })
        
        return self.upsert_data('sales_activities', transformed)
    
    def upsert_data(self, table_name, data):
        """Insert or update data in the database"""
        if not data:
            return 0
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Build the INSERT ... ON CONFLICT query
            columns = list(data[0].keys())
            
            # Create the query based on table
            if table_name == 'sales_team':
                query = """
                    INSERT INTO sales_team (id, display_name, email, is_active, work_number, mobile_number)
                    VALUES (%(id)s, %(display_name)s, %(email)s, %(is_active)s, %(work_number)s, %(mobile_number)s)
                    ON CONFLICT (id) DO UPDATE SET
                        display_name = EXCLUDED.display_name,
                        email = EXCLUDED.email,
                        is_active = EXCLUDED.is_active,
                        work_number = EXCLUDED.work_number,
                        mobile_number = EXCLUDED.mobile_number
                """
            elif table_name == 'contact_statuses':
                query = """
                    INSERT INTO contact_statuses (id, name, position, partial, forecast_type, lifecycle_stage_id)
                    VALUES (%(id)s, %(name)s, %(position)s, %(partial)s, %(forecast_type)s, %(lifecycle_stage_id)s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        position = EXCLUDED.position,
                        partial = EXCLUDED.partial,
                        forecast_type = EXCLUDED.forecast_type,
                        lifecycle_stage_id = EXCLUDED.lifecycle_stage_id
                """
            elif table_name == 'appointments':
                query = """
                    INSERT INTO appointments (id, title, description, location, from_date, end_date, is_allday, 
                                            time_zone, provider, creater_id, created_at, updated_at, outcome_id, conference_id)
                    VALUES (%(id)s, %(title)s, %(description)s, %(location)s, %(from_date)s, %(end_date)s, 
                           %(is_allday)s, %(time_zone)s, %(provider)s, %(creater_id)s, %(created_at)s, 
                           %(updated_at)s, %(outcome_id)s, %(conference_id)s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        location = EXCLUDED.location,
                        from_date = EXCLUDED.from_date,
                        end_date = EXCLUDED.end_date,
                        is_allday = EXCLUDED.is_allday,
                        time_zone = EXCLUDED.time_zone,
                        provider = EXCLUDED.provider,
                        creater_id = EXCLUDED.creater_id,
                        updated_at = EXCLUDED.updated_at,
                        outcome_id = EXCLUDED.outcome_id,
                        conference_id = EXCLUDED.conference_id
                """
            elif table_name == 'tasks':
                query = """
                    INSERT INTO tasks (id, title, description, due_date, is_completed, created_at, updated_at, 
                                     creater_id, task_type_id, priority)
                    VALUES (%(id)s, %(title)s, %(description)s, %(due_date)s, %(is_completed)s, %(created_at)s, 
                           %(updated_at)s, %(creater_id)s, %(task_type_id)s, %(priority)s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        due_date = EXCLUDED.due_date,
                        is_completed = EXCLUDED.is_completed,
                        updated_at = EXCLUDED.updated_at,
                        creater_id = EXCLUDED.creater_id,
                        task_type_id = EXCLUDED.task_type_id,
                        priority = EXCLUDED.priority
                """
            elif table_name == 'contacts':
                query = """
                    INSERT INTO contacts (id, first_name, last_name, email)
                    VALUES (%(id)s, %(first_name)s, %(last_name)s, %(email)s)
                    ON CONFLICT (id) DO UPDATE SET
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email
                """
            elif table_name == 'accounts':
                query = """
                    INSERT INTO accounts (id, name, industry)
                    VALUES (%(id)s, %(name)s, %(industry)s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        industry = EXCLUDED.industry
                """
            elif table_name == 'products':
                query = """
                    INSERT INTO products (id, name, price)
                    VALUES (%(id)s, %(name)s, %(price)s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price
                """
            elif table_name == 'deals':
                query = """
                    INSERT INTO deals (id, name, amount, close_date, product_id, account_id, contact_id)
                    VALUES (%(id)s, %(name)s, %(amount)s, %(close_date)s, %(product_id)s, %(account_id)s, %(contact_id)s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        amount = EXCLUDED.amount,
                        close_date = EXCLUDED.close_date,
                        product_id = EXCLUDED.product_id,
                        account_id = EXCLUDED.account_id,
                        contact_id = EXCLUDED.contact_id
                """
            elif table_name == 'sales_activities':
                query = """
                    INSERT INTO sales_activities (id, title, activity_type, targetable_type, targetable_id, 
                                                start_date, end_date, created_at, updated_at, creater_id, outcome)
                    VALUES (%(id)s, %(title)s, %(activity_type)s, %(targetable_type)s, %(targetable_id)s, 
                           %(start_date)s, %(end_date)s, %(created_at)s, %(updated_at)s, %(creater_id)s, %(outcome)s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        activity_type = EXCLUDED.activity_type,
                        targetable_type = EXCLUDED.targetable_type,
                        targetable_id = EXCLUDED.targetable_id,
                        start_date = EXCLUDED.start_date,
                        end_date = EXCLUDED.end_date,
                        updated_at = EXCLUDED.updated_at,
                        creater_id = EXCLUDED.creater_id,
                        outcome = EXCLUDED.outcome
                """
            
            # Execute batch insert
            execute_batch(cur, query, data)
            conn.commit()
            
            print(f"   ✅ Synced {len(data)} {table_name}")
            
            cur.close()
            conn.close()
            return len(data)
            
        except Exception as e:
            print(f"   ❌ Error syncing {table_name}: {str(e)}")
            return 0
    
    def run_full_sync(self):
        """Run complete sync of all data"""
        print("\n🚀 Starting Freshworks data sync...")
        print("="*50)
        
        # Test connection first
        if not self.test_connection():
            print("\n❌ Cannot proceed without valid Freshworks connection")
            return
        
        # Setup database
        if not self.setup_database():
            print("\n❌ Cannot proceed without database setup")
            return
        
        # Sync all entities
        start_time = time.time()
        
        totals = {
            'sales_team': self.sync_sales_team(),
            'contact_statuses': self.sync_contact_statuses(),
            'contacts': self.sync_contacts(),
            'accounts': self.sync_accounts(),
            'products': self.sync_products(),
            'deals': self.sync_deals(),
            'appointments': self.sync_appointments(),
            'tasks': self.sync_tasks(),
            'activities': self.sync_activities()
        }
        
        end_time = time.time()
        
        # Summary
        print("\n" + "="*50)
        print("✅ SYNC COMPLETE!")
        print("="*50)
        print(f"\nSynced in {end_time - start_time:.1f} seconds:")
        for entity, count in totals.items():
            print(f"  • {entity}: {count} records")
        
        print("\n🤖 Your chatbot can now query this comprehensive real data!")
        print("Try questions like:")
        print("  - 'Who are our active sales team members?'")
        print("  - 'What appointments do we have this week?'")
        print("  - 'Show me meetings with [company name]'")
        print("  - 'What are my top deals this month?'")
        print("  - 'List recent sales activities'")
        print("  - 'Show me pending tasks'")
        print("  - 'What's our sales pipeline status?'")
        print("  - 'Which products are selling the most?'")

def main():
    """Main execution"""
    syncer = FreshworksSyncer()
    syncer.run_full_sync()

if __name__ == "__main__":
    main() 