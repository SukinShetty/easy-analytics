#!/usr/bin/env python3
"""
Demo Mode Setup - Use Sample Data Instead of Freshworks
Allows testing the chatbot while fixing API access
"""

import psycopg2
import os
from datetime import datetime, timedelta
import random

print("🎯 DEMO MODE SETUP - Easy Analytics")
print("=" * 50)
print("This will load sample data so you can test the chatbot")
print("while you fix the Freshworks API access issue.\n")

# Database configuration
db_config = {
    "host": "localhost",
    "port": "5432",
    "database": "tooljet_prod",
    "user": "postgres",
    "password": "tooljet"
}

def setup_demo_data():
    """Load sample CRM data for demo"""
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("📊 Setting up database schema...")
        # Create tables
        with open('db_schema.sql', 'r') as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema created")
        
        # Clear existing data
        print("\n🧹 Clearing existing data...")
        tables = ['sales_activities', 'deals', 'contacts', 'accounts', 'products']
        for table in tables:
            cur.execute(f"DELETE FROM {table}")
        conn.commit()
        
        print("\n📦 Loading demo data...")
        
        # Insert demo products
        products = [
            (1, 'CRM Professional', 299.00),
            (2, 'Analytics Suite', 499.00),
            (3, 'Marketing Automation', 399.00),
            (4, 'Support Desk Pro', 199.00),
            (5, 'Sales Intelligence', 599.00)
        ]
        cur.executemany(
            "INSERT INTO products (id, name, price) VALUES (%s, %s, %s)",
            products
        )
        print(f"  ✅ Loaded {len(products)} products")
        
        # Insert demo accounts
        accounts = [
            (1, 'TechCorp Solutions', 'Technology'),
            (2, 'Global Retail Inc', 'Retail'),
            (3, 'Finance Masters', 'Financial Services'),
            (4, 'Healthcare Plus', 'Healthcare'),
            (5, 'Manufacturing Co', 'Manufacturing'),
            (6, 'StartupXYZ', 'Technology'),
            (7, 'Consulting Group', 'Professional Services'),
            (8, 'Real Estate Ltd', 'Real Estate')
        ]
        cur.executemany(
            "INSERT INTO accounts (id, name, industry) VALUES (%s, %s, %s)",
            accounts
        )
        print(f"  ✅ Loaded {len(accounts)} accounts")
        
        # Insert demo contacts
        contacts = [
            (1, 'Rajesh', 'Kumar', 'rajesh.kumar@techcorp.com'),
            (2, 'Priya', 'Sharma', 'priya.sharma@globalretail.com'),
            (3, 'Amit', 'Patel', 'amit.patel@finance.com'),
            (4, 'Sneha', 'Reddy', 'sneha.reddy@healthcare.com'),
            (5, 'Vikram', 'Singh', 'vikram.singh@manufacturing.com'),
            (6, 'Anita', 'Gupta', 'anita@startupxyz.com'),
            (7, 'Suresh', 'Nair', 'suresh.nair@consulting.com'),
            (8, 'Kavita', 'Mehta', 'kavita.mehta@realestate.com'),
            (9, 'Ravi', 'Verma', 'ravi.verma@techcorp.com'),
            (10, 'Deepa', 'Shah', 'deepa.shah@globalretail.com')
        ]
        cur.executemany(
            "INSERT INTO contacts (id, first_name, last_name, email) VALUES (%s, %s, %s, %s)",
            contacts
        )
        print(f"  ✅ Loaded {len(contacts)} contacts")
        
        # Insert demo deals with varying amounts and dates
        deals = []
        base_date = datetime.now() - timedelta(days=90)
        
        deal_names = [
            'Enterprise CRM Implementation',
            'Analytics Platform Upgrade',
            'Marketing Automation Setup',
            'Support System Migration',
            'Sales Intelligence Pilot',
            'CRM Training Package',
            'Custom Analytics Dashboard',
            'Full Suite Implementation',
            'Quarterly Support Contract',
            'Data Migration Project',
            'API Integration Package',
            'Mobile App Development',
            'Security Audit Service',
            'Performance Optimization',
            'Cloud Migration'
        ]
        
        for i in range(1, 16):
            deal_date = base_date + timedelta(days=random.randint(0, 90))
            amount = random.randint(10000, 150000)
            product_id = random.randint(1, 5)
            account_id = random.randint(1, 8)
            contact_id = random.randint(1, 10)
            
            deals.append((
                i,
                deal_names[i-1],
                amount,
                deal_date.date(),
                product_id,
                account_id,
                contact_id
            ))
        
        cur.executemany(
            """INSERT INTO deals (id, name, amount, close_date, product_id, account_id, contact_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            deals
        )
        print(f"  ✅ Loaded {len(deals)} deals")
        
        # Insert demo activities
        activities = []
        activity_types = ['Call', 'Email', 'Meeting', 'Demo', 'Proposal', 'Follow-up']
        outcomes = ['Successful', 'Scheduled next step', 'No response', 'Very interested', 'Needs more info']
        
        activity_id = 1
        for deal_id in range(1, 16):
            # 2-5 activities per deal
            num_activities = random.randint(2, 5)
            for _ in range(num_activities):
                activity_date = base_date + timedelta(days=random.randint(0, 90))
                activities.append((
                    activity_id,
                    deal_id,
                    random.choice(activity_types),
                    activity_date.date(),
                    random.choice(outcomes)
                ))
                activity_id += 1
        
        cur.executemany(
            """INSERT INTO sales_activities (id, deal_id, activity_type, date, outcome) 
               VALUES (%s, %s, %s, %s, %s)""",
            activities
        )
        print(f"  ✅ Loaded {len(activities)} sales activities")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ DEMO DATA LOADED SUCCESSFULLY!")
        print("=" * 50)
        
        print("\n📊 Sample Questions You Can Ask:")
        print("  • 'What is the total revenue this month?'")
        print("  • 'Show me the top 5 deals'")
        print("  • 'Which product is selling the most?'")
        print("  • 'List all contacts from Technology companies'")
        print("  • 'What activities happened this week?'")
        print("  • 'Show deals above 100000'")
        print("  • 'What is the average deal size?'")
        
        print("\n🌐 Next Steps:")
        print("1. Open ToolJet at http://localhost:3000")
        print("2. Follow CLIENT_DEMO_GUIDE.md to set up the chatbot")
        print("3. Start asking questions about the demo data!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("  • Docker services are running (run FINAL_FIX.bat)")
        print("  • PostgreSQL is accessible on localhost:5432")
        return False

if __name__ == "__main__":
    if setup_demo_data():
        print("\n✨ You can now test the chatbot with demo data!")
        print("   Meanwhile, follow GET_CORRECT_API_KEY.md to fix Freshworks access.") 