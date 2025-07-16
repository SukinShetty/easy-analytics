import os
import time
import requests
import subprocess
import psycopg2
from datetime import datetime, timedelta
import random

def check_docker_services():
    """Check if Docker services are running"""
    print("🔍 Checking Docker services...")
    result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Docker services status:")
        print(result.stdout)
        
        # Check specific services
        services = ['tooljet', 'postgres']
        running_services = result.stdout.lower()
        
        for service in services:
            if any(service in line.lower() for line in running_services.split('\n')):
                print(f"✅ {service} is running")
            else:
                print(f"❌ {service} is NOT running")
                return False
    else:
        print("❌ Docker is not running or not installed")
        return False
    
    return True

def wait_for_tooljet(url='http://localhost:8080', timeout=60):
    """Wait for ToolJet to be ready"""
    print(f"\n⏳ Waiting for ToolJet at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ ToolJet is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(".", end="", flush=True)
        time.sleep(2)
    
    print("\n❌ ToolJet did not start within timeout")
    return False

def test_database_connection():
    """Test database connectivity and setup"""
    print("\n🔍 Testing database connection...")
    
    try:
        # Connection parameters from docker-compose
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="tooljet_prod",
            user="postgres",
            password="tooljet"
        )
        
        cur = conn.cursor()
        
        # Check if tables exist
        tables = ['deals', 'contacts', 'accounts', 'products', 'sales_activities']
        existing_tables = []
        
        for table in tables:
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            result = cur.fetchone()
            exists = result[0] if result else False
            if exists:
                existing_tables.append(table)
        
        if not existing_tables:
            print("⚠️  No tables found. Creating schema...")
            with open('db_schema.sql', 'r') as f:
                schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
            print("✅ Database schema created")
        else:
            print(f"✅ Found existing tables: {', '.join(existing_tables)}")
        
        # Check if we have test data
        cur.execute("SELECT COUNT(*) FROM deals")
        result = cur.fetchone()
        deal_count = result[0] if result else 0
        
        if deal_count == 0:
            print("⚠️  No test data found. Inserting sample data...")
            insert_test_data(cur)
            conn.commit()
            print("✅ Test data inserted")
        else:
            print(f"✅ Found {deal_count} deals in database")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def insert_test_data(cursor):
    """Insert sample test data for chatbot testing"""
    
    # Insert products
    products = [
        (1, 'CRM Pro', 299.99),
        (2, 'Analytics Suite', 499.99),
        (3, 'Marketing Automation', 399.99),
        (4, 'Support Desk', 199.99)
    ]
    for p in products:
        cursor.execute("INSERT INTO products (id, name, price) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", p)
    
    # Insert accounts
    accounts = [
        (1, 'Acme Corp', 'Technology'),
        (2, 'Global Industries', 'Manufacturing'),
        (3, 'StartupXYZ', 'Software'),
        (4, 'Retail Chain', 'Retail')
    ]
    for a in accounts:
        cursor.execute("INSERT INTO accounts (id, name, industry) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", a)
    
    # Insert contacts
    contacts = [
        (1, 'John', 'Doe', 'john.doe@acme.com'),
        (2, 'Jane', 'Smith', 'jane.smith@global.com'),
        (3, 'Bob', 'Wilson', 'bob@startupxyz.com'),
        (4, 'Alice', 'Brown', 'alice.brown@retail.com')
    ]
    for c in contacts:
        cursor.execute("INSERT INTO contacts (id, first_name, last_name, email) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", c)
    
    # Insert deals with varying dates and amounts
    base_date = datetime.now() - timedelta(days=90)
    deals = []
    for i in range(1, 21):
        deal_date = base_date + timedelta(days=random.randint(0, 90))
        amount = random.randint(1000, 50000)
        product_id = random.randint(1, 4)
        account_id = random.randint(1, 4)
        contact_id = random.randint(1, 4)
        deals.append((i, f'Deal {i}', amount, deal_date, product_id, account_id, contact_id))
    
    for d in deals:
        cursor.execute("""
            INSERT INTO deals (id, name, amount, close_date, product_id, account_id, contact_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, d)
    
    # Insert sales activities
    activity_types = ['Call', 'Email', 'Meeting', 'Demo', 'Proposal']
    outcomes = ['Successful', 'Follow-up needed', 'No response', 'Interested', 'Not interested']
    
    for i in range(1, 51):
        deal_id = random.randint(1, 20)
        activity_type = random.choice(activity_types)
        activity_date = base_date + timedelta(days=random.randint(0, 90))
        outcome = random.choice(outcomes)
        cursor.execute("""
            INSERT INTO sales_activities (id, deal_id, activity_type, date, outcome) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (i, deal_id, activity_type, activity_date, outcome))

def test_chatbot_queries():
    """Test various chatbot query scenarios"""
    print("\n🤖 Testing chatbot query patterns...")
    
    test_queries = [
        "What is the total revenue this month?",
        "Show me the top 5 deals by amount",
        "Which product is selling the most?",
        "How many deals are closing this week?",
        "List all contacts from technology companies",
        "What's the average deal size by industry?",
        "Show me all activities for Deal 1",
        "Which sales rep has the most activities?",
        "What's the conversion rate by product?",
        "Show deals without any activities"
    ]
    
    print("\n📝 Sample queries the chatbot should handle:")
    for i, query in enumerate(test_queries, 1):
        print(f"   {i}. {query}")
    
    # Generate expected SQL for some queries
    print("\n🔍 Expected SQL patterns:")
    
    sql_examples = {
        "Total revenue": """
            SELECT SUM(amount) as total_revenue 
            FROM deals 
            WHERE close_date >= DATE_TRUNC('month', CURRENT_DATE)
        """,
        "Top deals": """
            SELECT name, amount 
            FROM deals 
            ORDER BY amount DESC 
            LIMIT 5
        """,
        "Product sales": """
            SELECT p.name, COUNT(d.id) as deal_count, SUM(d.amount) as total_sales
            FROM products p
            JOIN deals d ON p.id = d.product_id
            GROUP BY p.name
            ORDER BY total_sales DESC
        """
    }
    
    for title, sql in sql_examples.items():
        print(f"\n{title}:")
        print(f"```sql{sql}```")

def check_api_keys():
    """Check if required API keys are configured"""
    print("\n🔑 Checking API keys configuration...")
    
    required_keys = {
        'OPENAI_API_KEY': 'OpenAI API (for natural language processing)',
        'FRESHWORKS_API_KEY': 'Freshworks API (for CRM integration)',
        'FRESHWORKS_DOMAIN': 'Freshworks domain'
    }
    
    # Check .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        for key, description in required_keys.items():
            if key in env_content and f'{key}=' in env_content:
                # Check if it has a non-template value
                if 'your_' in env_content or 'test_' in env_content:
                    print(f"⚠️  {key} ({description}) - Found but appears to be a template value")
                else:
                    print(f"✅ {key} ({description}) - Configured")
            else:
                print(f"❌ {key} ({description}) - Not found")
    else:
        print("❌ .env file not found. Copy env.template to .env and configure your API keys")
        return False
    
    return True

def main():
    """Main test execution"""
    print("🚀 Easy Analytics Chatbot Test Suite")
    print("====================================\n")
    
    # Step 1: Check Docker services
    if not check_docker_services():
        print("\n⚠️  Please start Docker services first:")
        print("   docker-compose up -d")
        return
    
    # Step 2: Wait for ToolJet
    if not wait_for_tooljet():
        print("\n⚠️  ToolJet is not responding. Check logs:")
        print("   docker-compose logs tooljet")
        return
    
    # Step 3: Test database
    if not test_database_connection():
        print("\n⚠️  Database issues detected. Check PostgreSQL logs:")
        print("   docker-compose logs postgres")
        return
    
    # Step 4: Check API keys
    check_api_keys()
    
    # Step 5: Show test queries
    test_chatbot_queries()
    
    print("\n✅ Test suite completed!")
    print("\n📋 Next steps to test the chatbot:")
    print("1. Open ToolJet at http://localhost:8080")
    print("2. Import or create your Easy Analytics app")
    print("3. Configure the chatbot queries:")
    print("   - generateSQL: OpenAI query for SQL generation")
    print("   - executeSQL: PostgreSQL query to run the generated SQL")
    print("   - summarizeResults: OpenAI query to summarize results")
    print("4. Test with the sample queries listed above")
    print("\n💡 Tip: Monitor the browser console for any JavaScript errors")

if __name__ == "__main__":
    main() 