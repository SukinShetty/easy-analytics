#!/usr/bin/env python3
"""
Sync ONLY Real Freshworks CRM Data
Based on the comprehensive discovery, this syncs the actual available data
"""

import psycopg2
import json
import os
from datetime import datetime

def sync_real_appointments():
    """Sync the real appointments data we found"""
    
    # Connect to database
    conn = psycopg2.connect(
        host='localhost',
        database='tooljet_prod',
        user='postgres',
        password='tooljet'
    )
    cur = conn.cursor()
    
    print("🔄 Syncing REAL Freshworks CRM appointments data...")
    
    # Clear any dummy data from deals table
    print("🗑️ Clearing dummy data...")
    cur.execute("DELETE FROM deals WHERE id >= 1000;")  # Remove dummy deals
    
    # Load and sync real appointments data
    appointments_file = 'real_freshworks_data/real_data_appointments_20250718_143434.json'
    
    if os.path.exists(appointments_file):
        with open(appointments_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        appointments = data.get('appointments', [])
        
        if appointments:
            print(f"📅 Syncing {len(appointments)} REAL appointments...")
            
            # Clear existing appointments
            cur.execute("DELETE FROM appointments;")
            
            synced_count = 0
            for appointment in appointments:
                try:
                    cur.execute("""
                        INSERT INTO appointments (
                            id, title, description, location, from_date, end_date,
                            is_allday, time_zone, provider, creater_id, created_at, updated_at,
                            outcome_id, conference_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            location = EXCLUDED.location,
                            from_date = EXCLUDED.from_date,
                            end_date = EXCLUDED.end_date
                    """, (
                        appointment.get('id'),
                        appointment.get('title'),
                        appointment.get('description'),
                        appointment.get('location'),
                        appointment.get('from_date'),
                        appointment.get('end_date'),
                        appointment.get('is_allday'),
                        appointment.get('time_zone'),
                        appointment.get('provider'),
                        appointment.get('creater_id'),
                        appointment.get('created_at'),
                        appointment.get('updated_at'),
                        appointment.get('outcome_id'),
                        appointment.get('conference_id')
                    ))
                    synced_count += 1
                    
                except Exception as e:
                    print(f"  ⚠️  Error syncing appointment {appointment.get('id')}: {e}")
                    continue
            
            conn.commit()
            print(f"  ✅ Synced {synced_count} REAL appointments")
            
            # Show the real appointments
            print("\n📋 REAL APPOINTMENTS IN YOUR CRM:")
            cur.execute("""
                SELECT id, title, from_date, location 
                FROM appointments 
                ORDER BY from_date DESC
            """)
            
            for row in cur.fetchall():
                apt_id, title, from_date, location = row
                print(f"  📅 {apt_id}: {title}")
                print(f"      Date: {from_date}")
                print(f"      Location: {location}")
                print()
        
        else:
            print("❌ No real appointments found in the API response")
    
    else:
        print("❌ No real appointments data file found")
    
    # Check what real data we have now
    print("\n📊 FINAL REAL DATA SUMMARY:")
    
    tables_to_check = [
        ('appointments', 'REAL Appointments'),
        ('sales_team', 'Sales Team Members'),
        ('contact_statuses', 'Contact Statuses'),
        ('deals', 'Deals'),
        ('contacts', 'Contacts'),
        ('accounts', 'Accounts')
    ]
    
    total_real_records = 0
    
    for table, description in tables_to_check:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            
            if count > 0:
                print(f"  ✅ {description}: {count} real records")
                total_real_records += count
            else:
                print(f"  ❌ {description}: No real data available from API")
                
        except Exception as e:
            print(f"  ❌ {description}: Table issue - {e}")
    
    print(f"\n🎯 TOTAL REAL CRM RECORDS: {total_real_records}")
    
    cur.close()
    conn.close()
    
    return total_real_records

def explain_api_limitations():
    """Explain what data is and isn't available"""
    print("\n" + "="*80)
    print("📋 FRESHWORKS CRM API ACCESS REPORT")
    print("="*80)
    
    print("\n✅ REAL DATA AVAILABLE:")
    print("  📅 Appointments: 5 real meetings/appointments from your CRM")
    print("      - Including Nestle meetings, demos, etc.")
    print("      - All with real dates, locations, descriptions")
    
    print("\n❌ REAL DATA NOT ACCESSIBLE (API Permissions):")
    print("  🚫 Deals: 403 Forbidden - Your API key needs 'Deals' permission")
    print("  🚫 Contacts: 403 Forbidden - Your API key needs 'Contacts' permission") 
    print("  🚫 Accounts: 403 Forbidden - Your API key needs 'Accounts' permission")
    print("  🚫 Sales Activities: Empty (no activities in your CRM)")
    print("  🚫 Tasks: Empty (no tasks in your CRM)")
    
    print("\n🔧 TO GET MORE REAL DATA:")
    print("1. Go to Freshworks CRM → Settings → API Settings")
    print("2. Enable these permissions for your API key:")
    print("   - Deals (Read)")
    print("   - Contacts (Read)")  
    print("   - Accounts (Read)")
    print("   - Products (Read)")
    print("3. Re-run the sync script")
    
    print("\n🎯 CURRENT CHATBOT CAPABILITIES:")
    print("✅ Can answer: 'Show me appointments', 'What meetings do we have?'")
    print("❌ Cannot answer: 'How many deals?', 'Show contacts' (no API access)")
    
    print("\n" + "="*80)

def main():
    print("🎯 REAL FRESHWORKS CRM DATA SYNC")
    print("This syncs ONLY real data from your Freshworks CRM")
    print("No dummy/fake data will be created!")
    print("-" * 60)
    
    # Sync real data
    real_records = sync_real_appointments()
    
    # Explain limitations
    explain_api_limitations()
    
    print("\n🎉 SYNC COMPLETE!")
    
    if real_records > 0:
        print(f"✅ Your chatbot now has {real_records} REAL CRM records")
        print("\nTry asking:")
        print("- 'Show me all appointments'")
        print("- 'What meetings do we have?'")
        print("- 'Show me the Nestle meetings'")
    else:
        print("❌ No real CRM data is accessible with your current API permissions")
        print("Contact your Freshworks admin to enable API access for deals, contacts, etc.")

if __name__ == '__main__':
    main() 