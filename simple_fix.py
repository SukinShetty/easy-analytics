import psycopg2

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    database='tooljet_prod', 
    user='postgres',
    password='tooljet'
)
cur = conn.cursor()

print("Adding demo deals data...")

# Clear existing deals
cur.execute("DELETE FROM deals;")

# Insert demo deals (only using columns that definitely exist)
deals = [
    (1001, 'Nestle CRM Implementation Deal', 75000.00),
    (1002, 'Super MN Auto Demo Deal', 35000.00), 
    (1003, 'Manufacturing Solutions Deal', 45000.00),
    (1004, 'Enterprise Software License Deal', 25000.00),
    (1005, 'Cloud Migration Project Deal', 60000.00)
]

for deal_id, name, amount in deals:
    cur.execute(
        "INSERT INTO deals (id, name, amount) VALUES (%s, %s, %s)",
        (deal_id, name, amount)
    )

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM deals")
count = cur.fetchone()[0]
print(f"✅ Inserted {count} demo deals")

# Show the deals
cur.execute("SELECT id, name, amount FROM deals ORDER BY id")
for row in cur.fetchall():
    print(f"  ID: {row[0]}, Name: {row[1]}, Amount: ${row[2]:,.2f}")

cur.close()
conn.close()

print("\n🎉 Database is now ready!")
print("Try asking the chatbot: 'How many deals do we have?'") 