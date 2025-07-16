#!/usr/bin/env python3
"""
Populate Database with Existing CSV Data
Load data from CSV files into PostgreSQL database
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import json
import os
from datetime import datetime

def populate_database():
    """Populate database with existing CSV data"""
    
    # Database configuration
    db_config = {
        "host": "localhost",
        "port": "5432",
        "database": "tooljet_prod", 
        "user": "postgres",
        "password": "tooljet"
    }
    
    # Find the data directory
    data_dir = None
    for item in os.listdir('.'):
        if item.startswith('kambaa_crm_data_'):
            data_dir = item
            break
    
    if not data_dir:
        print("❌ No CRM data directory found")
        return
    
    print(f"📁 Loading data from: {data_dir}")
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Load sales team data
        print("👥 Loading sales team...")
        sales_team_file = f"{data_dir}/sales_team.csv"
        if os.path.exists(sales_team_file):
            df = pd.read_csv(sales_team_file)
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO sales_team (id, display_name, email, is_active, work_number, mobile_number)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        display_name = EXCLUDED.display_name,
                        email = EXCLUDED.email,
                        is_active = EXCLUDED.is_active,
                        work_number = EXCLUDED.work_number,
                        mobile_number = EXCLUDED.mobile_number
                """, (
                    row['id'], row['display_name'], row['email'], 
                    row['is_active'], row.get('work_number'), row.get('mobile_number')
                ))
            print(f"   ✅ Loaded {len(df)} sales team records")
        
        # Load contact statuses
        print("📊 Loading contact statuses...")
        contact_statuses_file = f"{data_dir}/contact_statuses.csv"
        if os.path.exists(contact_statuses_file):
            df = pd.read_csv(contact_statuses_file)
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO contact_statuses (id, name, position, partial, forecast_type, lifecycle_stage_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        position = EXCLUDED.position,
                        partial = EXCLUDED.partial,
                        forecast_type = EXCLUDED.forecast_type,
                        lifecycle_stage_id = EXCLUDED.lifecycle_stage_id
                """, (
                    row['id'], row['name'], row['position'],
                    row['partial'], row['forecast_type'], row.get('lifecycle_stage_id')
                ))
            print(f"   ✅ Loaded {len(df)} contact status records")
        
        # Load appointments
        print("📅 Loading appointments...")
        appointments_file = f"{data_dir}/appointments.csv"
        if os.path.exists(appointments_file):
            df = pd.read_csv(appointments_file)
            for _, row in df.iterrows():
                # Convert date strings to proper datetime objects
                from_date = pd.to_datetime(row.get('from_date')) if pd.notna(row.get('from_date')) else None
                end_date = pd.to_datetime(row.get('end_date')) if pd.notna(row.get('end_date')) else None
                created_at = pd.to_datetime(row.get('created_at')) if pd.notna(row.get('created_at')) else None
                updated_at = pd.to_datetime(row.get('updated_at')) if pd.notna(row.get('updated_at')) else None
                
                # Handle large conference_id values 
                conference_id = row.get('conference_id')
                if pd.isna(conference_id):
                    conference_id = None
                else:
                    conference_id = str(conference_id)
                
                outcome_id = row.get('outcome_id')
                if pd.isna(outcome_id):
                    outcome_id = None
                
                creater_id = row.get('creater_id')
                if pd.isna(creater_id):
                    creater_id = None
                
                cur.execute("""
                    INSERT INTO appointments (id, title, description, location, from_date, end_date, 
                                            is_allday, time_zone, provider, creater_id, created_at, 
                                            updated_at, outcome_id, conference_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                """, (
                    row['id'], row.get('title', ''), row.get('description', ''),
                    row.get('location', ''), from_date, end_date, 
                    row.get('is_allday', False), row.get('time_zone', ''),
                    row.get('provider', ''), creater_id,
                    created_at, updated_at, outcome_id, conference_id
                ))
            print(f"   ✅ Loaded {len(df)} appointment records")
        
        # Check for tasks data (JSON file)
        print("📋 Loading tasks...")
        tasks_file = f"{data_dir}/tasks.json"
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks_json = json.load(f)
            tasks_data = tasks_json.get('tasks', [])
            if tasks_data and len(tasks_data) > 0:
                for task in tasks_data:
                    due_date = pd.to_datetime(task.get('due_date')) if task.get('due_date') else None
                    created_at = pd.to_datetime(task.get('created_at')) if task.get('created_at') else None
                    updated_at = pd.to_datetime(task.get('updated_at')) if task.get('updated_at') else None
                    
                    cur.execute("""
                        INSERT INTO tasks (id, title, description, due_date, is_completed, 
                                         created_at, updated_at, creater_id, task_type_id, priority)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            due_date = EXCLUDED.due_date,
                            is_completed = EXCLUDED.is_completed,
                            updated_at = EXCLUDED.updated_at,
                            creater_id = EXCLUDED.creater_id,
                            task_type_id = EXCLUDED.task_type_id,
                            priority = EXCLUDED.priority
                    """, (
                        task.get('id'), task.get('title', ''), task.get('description', ''),
                        due_date, task.get('is_completed', False),
                        created_at, updated_at, task.get('creater_id'),
                        task.get('task_type_id'), task.get('priority')
                    ))
                print(f"   ✅ Loaded {len(tasks_data)} task records")
            else:
                print("   ⚠️  No task data found")
        
        # Check for sales activities data (JSON file)
        print("📈 Loading sales activities...")
        activities_file = f"{data_dir}/sales_activities.json"
        if os.path.exists(activities_file):
            with open(activities_file, 'r') as f:
                activities_json = json.load(f)
            activities_data = activities_json.get('sales_activities', [])
            if activities_data and len(activities_data) > 0:
                for activity in activities_data:
                    start_date = pd.to_datetime(activity.get('start_date')) if activity.get('start_date') else None
                    end_date = pd.to_datetime(activity.get('end_date')) if activity.get('end_date') else None
                    created_at = pd.to_datetime(activity.get('created_at')) if activity.get('created_at') else None
                    updated_at = pd.to_datetime(activity.get('updated_at')) if activity.get('updated_at') else None
                    
                    cur.execute("""
                        INSERT INTO sales_activities (id, title, activity_type, targetable_type, targetable_id,
                                                    start_date, end_date, created_at, updated_at, creater_id, outcome)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    """, (
                        activity.get('id'), activity.get('title', ''), activity.get('activity_type', ''),
                        activity.get('targetable_type', ''), activity.get('targetable_id'),
                        start_date, end_date, created_at, updated_at,
                        activity.get('creater_id'), activity.get('outcome', '')
                    ))
                print(f"   ✅ Loaded {len(activities_data)} sales activity records")
            else:
                print("   ⚠️  No sales activities data found")
        
        # Commit all changes
        conn.commit()
        
        # Print summary
        print("\n" + "="*50)
        print("✅ DATABASE POPULATED SUCCESSFULLY!")
        print("="*50)
        
        # Show record counts
        cur.execute("SELECT COUNT(*) FROM sales_team")
        team_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM contact_statuses")
        statuses_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM appointments")
        appointments_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM tasks")
        tasks_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM sales_activities")
        activities_count = cur.fetchone()[0]
        
        print(f"\n📊 Records in database:")
        print(f"   • Sales Team: {team_count}")
        print(f"   • Contact Statuses: {statuses_count}")
        print(f"   • Appointments: {appointments_count}")
        print(f"   • Tasks: {tasks_count}")
        print(f"   • Sales Activities: {activities_count}")
        
        print(f"\n🤖 Ready to start database chatbot!")
        print(f"   Run: python database_crm_chatbot.py")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_database() 