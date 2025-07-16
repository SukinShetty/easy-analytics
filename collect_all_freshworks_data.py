#!/usr/bin/env python3
"""
Comprehensive Freshworks Data Collection
Collects all available data from working endpoints
"""

import requests
import json
import os
import pandas as pd
from datetime import datetime

# Configuration
FRESHWORKS_DOMAIN = "kambaacrm.myfreshworks.com"
API_KEY = "2IbbXJgW_QJLDOBwl7Znqw"

class FreshworksDataCollector:
    def __init__(self):
        self.headers = {
            'Authorization': f'Token token={API_KEY}',
            'Content-Type': 'application/json'
        }
        self.base_url = f"https://{FRESHWORKS_DOMAIN}"
        self.results = {}
        
    def fetch_endpoint_data(self, endpoint, name, max_pages=5):
        """Fetch data from an endpoint with pagination support"""
        
        print(f"📡 Fetching: {name}")
        print(f"   URL: {self.base_url}{endpoint}")
        
        all_data = []
        page = 1
        
        while page <= max_pages:
            try:
                # Add pagination parameter
                url = f"{self.base_url}{endpoint}"
                if '?' in endpoint:
                    url += f"&page={page}"
                else:
                    url += f"?page={page}"
                
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract the main data array
                    main_key = None
                    for key in ['sales_activities', 'tasks', 'appointments', 'users', 'filters', 'contact_statuses']:
                        if key in data:
                            main_key = key
                            break
                    
                    if main_key and data[main_key]:
                        items = data[main_key]
                        all_data.extend(items)
                        print(f"   📄 Page {page}: {len(items)} items")
                        
                        # Check if there are more pages
                        meta = data.get('meta', {})
                        if page >= meta.get('total_pages', 1):
                            break
                        page += 1
                    else:
                        # No main data array, save the whole response
                        all_data = data
                        break
                        
                elif response.status_code == 403:
                    print(f"   🔒 FORBIDDEN (403)")
                    return None
                elif response.status_code == 404:
                    print(f"   ❌ NOT FOUND (404)")
                    return None
                else:
                    print(f"   ❌ ERROR ({response.status_code}): {response.text[:100]}")
                    return None
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
                return None
        
        if all_data:
            print(f"   ✅ SUCCESS: Total {len(all_data) if isinstance(all_data, list) else 1} items")
            return all_data
        else:
            print(f"   ⚠️  No data returned")
            return None

    def collect_all_data(self):
        """Collect data from all working endpoints"""
        
        print("🚀 Comprehensive Freshworks Data Collection")
        print("=" * 60)
        print(f"Domain: {FRESHWORKS_DOMAIN}")
        print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
        print()
        
        # All known working endpoints
        endpoints = {
            'sales_team': '/crm/sales/api/selector/owners',
            'contact_statuses': '/crm/sales/api/selector/contact_statuses', 
            'contact_filters': '/crm/sales/api/contacts/filters',
            'sales_activities': '/crm/sales/api/activities',
            'tasks': '/crm/sales/api/tasks',
            'appointments': '/crm/sales/api/appointments'
        }
        
        for data_type, endpoint in endpoints.items():
            data = self.fetch_endpoint_data(endpoint, data_type)
            if data:
                self.results[data_type] = data
            print()
        
        return self.results

    def save_data(self):
        """Save collected data in multiple formats"""
        
        # Create data directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = f"kambaa_crm_data_{timestamp}"
        os.makedirs(data_dir, exist_ok=True)
        
        print(f"💾 Saving data to: {data_dir}/")
        print("=" * 40)
        
        for data_type, data in self.results.items():
            # Save as JSON
            json_file = f"{data_dir}/{data_type}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   📄 {data_type}.json")
            
            # Save as CSV if it's a list of objects
            if isinstance(data, list) and data and isinstance(data[0], dict):
                try:
                    df = pd.DataFrame(data)
                    csv_file = f"{data_dir}/{data_type}.csv"
                    df.to_csv(csv_file, index=False)
                    print(f"   📊 {data_type}.csv ({len(df)} rows)")
                except Exception as e:
                    print(f"   ⚠️  Could not create CSV for {data_type}: {e}")

    def analyze_data(self):
        """Analyze the collected data"""
        
        print("\n" + "=" * 60)
        print("📊 DATA ANALYSIS")
        print("=" * 60)
        
        for data_type, data in self.results.items():
            print(f"\n🔍 {data_type.upper()}:")
            
            if data_type == 'sales_team':
                users = data.get('users', []) if isinstance(data, dict) else data
                print(f"   👥 Team members: {len(users)}")
                for user in users:
                    name = user.get('display_name', 'Unknown')
                    email = user.get('email', 'No email')
                    active = "🟢 Active" if user.get('is_active') else "🔴 Inactive"
                    print(f"      • {name} ({email}) - {active}")
                    
            elif data_type == 'sales_activities':
                print(f"   📊 Total activities: {len(data)}")
                if data:
                    # Analyze activity types
                    activity_types = {}
                    recent_activities = []
                    
                    for activity in data:
                        activity_type = activity.get('type', 'Unknown')
                        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
                        
                        # Collect recent activities
                        if len(recent_activities) < 5:
                            recent_activities.append(activity)
                    
                    print(f"   📈 Activity types:")
                    for act_type, count in activity_types.items():
                        print(f"      • {act_type}: {count}")
                    
                    print(f"   📅 Recent activities:")
                    for activity in recent_activities[:3]:
                        title = activity.get('title', 'No title')[:50]
                        date = activity.get('created_at', 'No date')[:10]
                        print(f"      • {title} ({date})")
                        
            elif data_type == 'tasks':
                print(f"   📋 Total tasks: {len(data)}")
                if data:
                    open_tasks = [t for t in data if not t.get('is_completed', True)]
                    print(f"   ⏳ Open tasks: {len(open_tasks)}")
                    
                    for task in open_tasks[:3]:
                        title = task.get('title', 'No title')[:50]
                        due_date = task.get('due_date', 'No due date')
                        print(f"      • {title} (Due: {due_date})")
                        
            elif data_type == 'appointments':
                print(f"   📅 Total appointments: {len(data)}")
                if data:
                    upcoming = []
                    for appt in data:
                        start_date = appt.get('start_date', '')
                        if start_date and start_date > datetime.now().isoformat():
                            upcoming.append(appt)
                    
                    print(f"   🔜 Upcoming appointments: {len(upcoming)}")
                    for appt in upcoming[:3]:
                        title = appt.get('title', 'No title')[:50]
                        date = appt.get('start_date', 'No date')[:16]
                        print(f"      • {title} ({date})")

def main():
    collector = FreshworksDataCollector()
    
    # Collect all data
    results = collector.collect_all_data()
    
    if results:
        # Save data
        collector.save_data()
        
        # Analyze data
        collector.analyze_data()
        
        print("\n" + "=" * 60)
        print("🎉 DATA COLLECTION COMPLETE!")
        print("=" * 60)
        print(f"✅ Successfully collected {len(results)} data types")
        print("📁 Data saved in multiple formats (JSON + CSV)")
        print("🔍 Analysis complete")
        print()
        print("🚀 READY FOR ANALYTICS DASHBOARD!")
        print("   • Sales team data available")
        print("   • Activity tracking ready") 
        print("   • Task management data loaded")
        print("   • Appointment scheduling data collected")
        
    else:
        print("\n❌ No data could be collected")

if __name__ == "__main__":
    main() 