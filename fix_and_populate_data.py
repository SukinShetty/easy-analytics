#!/usr/bin/env python3
"""
Quick fix to populate deals data for testing the chatbot
"""

import psycopg2
from datetime import datetime, timedelta
import random

def populate_demo_data():
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        database='tooljet_prod',
        user='postgres',
        password='tooljet'
    )
    cur = conn.cursor()
    
    print("🔧 Fixing database and populating demo data...")
    
    # Clear existing deals
    cur.execute("DELETE FROM deals;")
    
    # Create demo deals data
    demo_deals = [
        {
            'id': 1001,
            'name': 'Nestle CRM Implementation Deal',
            'amount': 75000.00,
            'is_won': True,
            'is_lost': False,
            'deal_stage': 'Won',
            'owner_id': 402000332019,
            'closed_on': datetime(2024, 12, 15),
            'expected_close_on': datetime(2024, 12, 15).date()
        },
        {
            'id': 1002,
            'name': 'Super MN Auto Demo Deal',
            'amount': 35000.00,
            'is_won': False,
            'is_lost': False,
            'deal_stage': 'Negotiation',
            'owner_id': 402000332019,
            'expected_close_on': datetime(2025, 1, 15).date()
        },
        {
            'id': 1003,
            'name': 'Manufacturing Solutions Deal',
            'amount': 45000.00,
            'is_won': True,
            'is_lost': False,
            'deal_stage': 'Won',
            'owner_id': 402000332019,
            'closed_on': datetime(2024, 11, 20),
            'expected_close_on': datetime(2024, 11, 20).date()
        },
        {
            'id': 1004,
            'name': 'Enterprise Software License',
            'amount': 25000.00,
            'is_won': False,
            'is_lost': True,
            'deal_stage': 'Lost',
            'owner_id': 402000332019,
            'closed_on': datetime(2024, 10, 30),
            'expected_close_on': datetime(2024, 10, 30).date()
        },
        {
            'id': 1005,
            'name': 'Cloud Migration Project',
            'amount': 60000.00,
            'is_won': False,
            'is_lost': False,
            'deal_stage': 'Proposal',
            'owner_id': 402000332019,
            'expected_close_on': datetime(2025, 2, 1).date()
        }
    ]
    
    # Insert demo deals
    for deal in demo_deals:
        cur.execute("""
            INSERT INTO deals (
                id, name, amount, is_won, is_lost, deal_stage, owner_id,
                closed_on, expected_close_on, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                amount = EXCLUDED.amount,
                is_won = EXCLUDED.is_won,
                is_lost = EXCLUDED.is_lost,
                deal_stage = EXCLUDED.deal_stage
        """, (
            deal['id'],
            deal['name'],
            deal['amount'],
            deal['is_won'],
            deal['is_lost'],
            deal['deal_stage'],
            deal['owner_id'],
            deal.get('closed_on'),
            deal['expected_close_on'],
            datetime.now(),
            datetime.now()
        ))
    
    conn.commit()
    
    # Show results
    cur.execute("SELECT deal_stage, COUNT(*), SUM(amount) FROM deals GROUP BY deal_stage ORDER BY deal_stage")
    results = cur.fetchall()
    
    print("\n📊 Demo Deals Created:")
    total_deals = 0
    total_amount = 0
    
    for stage, count, amount in results:
        print(f"  {stage}: {count} deals, ${amount:,.2f}")
        total_deals += count
        total_amount += amount
    
    print(f"\n✅ Total: {total_deals} deals, ${total_amount:,.2f}")
    
    # Test some queries
    print("\n🧪 Testing queries:")
    
    # Closed deals
    cur.execute("SELECT COUNT(*) FROM deals WHERE is_won = true OR is_lost = true")
    closed_result = cur.fetchone()
    if closed_result:
        closed_count = closed_result[0]
        print(f"  Closed deals: {closed_count}")
    
    # Won deals
    cur.execute("SELECT COUNT(*), SUM(amount) FROM deals WHERE is_won = true")
    won_result = cur.fetchone()
    if won_result:
        won_count, won_amount = won_result
        print(f"  Won deals: {won_count} worth ${won_amount or 0:,.2f}")
    
    # Lost deals
    cur.execute("SELECT COUNT(*) FROM deals WHERE is_lost = true")
    lost_result = cur.fetchone()
    if lost_result:
        lost_count = lost_result[0]
        print(f"  Lost deals: {lost_count}")
    
    # Open deals
    cur.execute("SELECT COUNT(*), SUM(amount) FROM deals WHERE is_won = false AND is_lost = false")
    open_result = cur.fetchone()
    if open_result:
        open_count, open_amount = open_result
        print(f"  Open deals: {open_count} worth ${open_amount or 0:,.2f}")
    
    cur.close()
    conn.close()
    
    print("\n✅ Database populated successfully!")
    print("\nNow try these chatbot queries:")
    print("- 'How many deals are closed?'")
    print("- 'Show me won deals'") 
    print("- 'What is the total value of won deals?'")
    print("- 'How many deals are still open?'")
    print("- 'Show me deals in negotiation stage'")

if __name__ == '__main__':
    populate_demo_data() 