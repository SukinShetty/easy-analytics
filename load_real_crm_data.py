#!/usr/bin/env python3
"""
Load Real Kambaa CRM Data into PostgreSQL
Uses the collected Freshworks data for analytics
"""

import psycopg2
import json
import csv
import os
from datetime import datetime
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'tooljet_db',
    'user': 'postgres',
    'password': 'tooljet'
}

def create_tables():
    """Create tables for real CRM data"""
    
    create_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS sales_team (
            id BIGINT PRIMARY KEY,
            display_name VARCHAR(255),
            email VARCHAR(255),
            is_active BOOLEAN,
            work_number VARCHAR(50),
            mobile_number VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS contact_statuses (
            id BIGINT PRIMARY KEY,
            name VARCHAR(255),
            position INTEGER,
            is_default BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id BIGINT PRIMARY KEY,
            title TEXT,
            description TEXT,
            location TEXT,
            is_allday BOOLEAN,
            from_date TIMESTAMP,
            end_date TIMESTAMP,
            outcome_id BIGINT,
            creater_id BIGINT,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            time_zone VARCHAR(100),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS contact_filters (
            id BIGINT PRIMARY KEY,
            name VARCHAR(255),
            model_class_name VARCHAR(100),
            user_id BIGINT,
            is_default BOOLEAN,
            updated_at TIMESTAMP
        );
        """
    ]
    
    print("🗄️  Creating database tables...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for query in create_table_queries:
            cursor.execute(query)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def load_csv_data(table_name, csv_file, column_mapping=None):
    """Load data from CSV file into database table"""
    
    if not os.path.exists(csv_file):
        print(f"⚠️  File not found: {csv_file}")
        return False
    
    try:
        print(f"📊 Loading {table_name} from {csv_file}")
        
        # Read CSV data
        df = pd.read_csv(csv_file)
        
        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        print(f"   📈 Found {len(df)} records")
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute(f"DELETE FROM {table_name}")
        
        # Insert data
        for _, row in df.iterrows():
            # Build insert query dynamically
            columns = list(row.index)
            values = list(row.values)
            
            # Handle NaN values
            values = [None if pd.isna(val) else val for val in values]
            
            placeholders = ', '.join(['%s'] * len(values))
            columns_str = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"   ✅ Loaded {len(df)} records into {table_name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading {table_name}: {e}")
        return False

def load_appointments_data():
    """Special handling for appointments data"""
    
    data_dir = None
    # Find the latest data directory
    for item in os.listdir('.'):
        if item.startswith('kambaa_crm_data_'):
            data_dir = item
            break
    
    if not data_dir:
        print("❌ No CRM data directory found")
        return False
    
    appointments_file = f"{data_dir}/appointments.csv"
    
    if not os.path.exists(appointments_file):
        print(f"❌ Appointments file not found: {appointments_file}")
        return False
    
    try:
        print(f"📅 Loading appointments from {appointments_file}")
        
        # Read and process appointments data
        df = pd.read_csv(appointments_file)
        
        print(f"   📈 Found {len(df)} appointments")
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM appointments")
        
        # Insert data with proper date handling
        for _, row in df.iterrows():
            try:
                # Handle dates
                from_date = row.get('from_date')
                end_date = row.get('end_date')
                created_at = row.get('created_at')
                updated_at = row.get('updated_at')
                
                # Convert dates if they exist
                if pd.notna(from_date):
                    from_date = pd.to_datetime(from_date).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    from_date = None
                
                if pd.notna(end_date):
                    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    end_date = None
                
                if pd.notna(created_at):
                    created_at = pd.to_datetime(created_at).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_at = None
                
                if pd.notna(updated_at):
                    updated_at = pd.to_datetime(updated_at).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    updated_at = None
                
                query = """
                INSERT INTO appointments (
                    id, title, description, location, is_allday, 
                    from_date, end_date, outcome_id, creater_id,
                    latitude, longitude, time_zone, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    row.get('id'),
                    row.get('title'),
                    row.get('description'),
                    row.get('location'),
                    row.get('is_allday') if pd.notna(row.get('is_allday')) else False,
                    from_date,
                    end_date,
                    row.get('outcome_id') if pd.notna(row.get('outcome_id')) else None,
                    row.get('creater_id') if pd.notna(row.get('creater_id')) else None,
                    row.get('latitude') if pd.notna(row.get('latitude')) else None,
                    row.get('longitude') if pd.notna(row.get('longitude')) else None,
                    row.get('time_zone'),
                    created_at,
                    updated_at
                )
                
                cursor.execute(query, values)
                
            except Exception as e:
                print(f"   ⚠️  Error inserting appointment {row.get('id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"   ✅ Loaded appointments data")
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading appointments: {e}")
        return False

def main():
    print("🚀 Loading Real Kambaa CRM Data")
    print("=" * 50)
    
    # Find data directory
    data_dir = None
    for item in os.listdir('.'):
        if item.startswith('kambaa_crm_data_'):
            data_dir = item
            break
    
    if not data_dir:
        print("❌ No CRM data directory found. Run collect_all_freshworks_data.py first.")
        return
    
    print(f"📁 Using data from: {data_dir}")
    print()
    
    # Create tables
    if not create_tables():
        return
    
    print()
    
    # Load data from CSV files
    success_count = 0
    
    # Sales team
    if load_csv_data('sales_team', f'{data_dir}/sales_team.csv'):
        success_count += 1
    
    # Contact statuses
    if load_csv_data('contact_statuses', f'{data_dir}/contact_statuses.csv'):
        success_count += 1
    
    # Contact filters
    if load_csv_data('contact_filters', f'{data_dir}/contact_filters.csv'):
        success_count += 1
    
    # Appointments (special handling)
    if load_appointments_data():
        success_count += 1
    
    print()
    print("=" * 50)
    if success_count > 0:
        print(f"🎉 SUCCESS! Loaded {success_count} data types")
        print("✅ Real Kambaa CRM data is now in PostgreSQL")
        print("🚀 Ready for analytics dashboard!")
        
        # Show summary
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            print("\n📊 DATA SUMMARY:")
            
            cursor.execute("SELECT COUNT(*) FROM sales_team WHERE is_active = true")
            active_team = cursor.fetchone()[0]
            print(f"   👥 Active sales team: {active_team} members")
            
            cursor.execute("SELECT COUNT(*) FROM appointments")
            appointments = cursor.fetchone()[0]
            print(f"   📅 Total appointments: {appointments}")
            
            cursor.execute("SELECT COUNT(*) FROM contact_statuses")
            statuses = cursor.fetchone()[0]
            print(f"   📊 Contact statuses: {statuses}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Could not get summary: {e}")
            
    else:
        print("❌ No data was loaded successfully")

if __name__ == "__main__":
    main() 