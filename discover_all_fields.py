import requests
import json
import os
from datetime import datetime

# Load environment variables
DOMAIN = os.getenv('FRESHWORKS_DOMAIN', 'kambaacrm.myfreshworks.com')
API_KEY = os.getenv('FRESHWORKS_API_KEY', '2IbbXJgW_QJLDOBwl7Znqw')

headers = {
    'Authorization': f'Token token={API_KEY}',
    'Content-Type': 'application/json'
}

def discover_fields(endpoint_name, endpoint_url):
    """Fetch sample data and discover all fields"""
    print(f"\n{'='*60}")
    print(f"Discovering fields for: {endpoint_name}")
    print(f"URL: {endpoint_url}")
    
    try:
        # Fetch with include parameter to get all associations
        url = f"{endpoint_url}?include=*&per_page=5"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
        data = response.json()
        
        # Extract the actual records
        records = []
        if isinstance(data, dict):
            # Handle paginated response
            if endpoint_name in data:
                records = data[endpoint_name]
            elif 'data' in data:
                records = data['data']
            else:
                # Try to find the data array
                for key, value in data.items():
                    if isinstance(value, list):
                        records = value
                        break
        elif isinstance(data, list):
            records = data
            
        if not records:
            print("⚠️  No records found")
            return None
            
        print(f"✅ Found {len(records)} sample records")
        
        # Analyze fields from all records
        all_fields = {}
        for record in records:
            if isinstance(record, dict):
                analyze_fields(record, all_fields)
                
        return all_fields
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def analyze_fields(obj, field_dict, prefix=''):
    """Recursively analyze fields and their types"""
    for key, value in obj.items():
        field_name = f"{prefix}{key}" if prefix else key
        
        if value is None:
            field_dict[field_name] = {'type': 'null', 'sample': None}
        elif isinstance(value, bool):
            field_dict[field_name] = {'type': 'boolean', 'sample': value}
        elif isinstance(value, int):
            field_dict[field_name] = {'type': 'integer', 'sample': value}
        elif isinstance(value, float):
            field_dict[field_name] = {'type': 'decimal', 'sample': value}
        elif isinstance(value, str):
            # Check if it's a datetime
            if any(pattern in value for pattern in ['T', 'Z', '-']):
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                    field_dict[field_name] = {'type': 'timestamp', 'sample': value}
                except:
                    field_dict[field_name] = {'type': 'string', 'sample': value[:100]}
            else:
                field_dict[field_name] = {'type': 'string', 'sample': value[:100]}
        elif isinstance(value, list):
            field_dict[field_name] = {'type': 'array', 'sample': f'Array with {len(value)} items'}
            if value and isinstance(value[0], dict):
                # Analyze nested object structure
                analyze_fields(value[0], field_dict, f"{field_name}[0].")
        elif isinstance(value, dict):
            field_dict[field_name] = {'type': 'object', 'sample': 'Nested object'}
            # Analyze nested structure
            analyze_fields(value, field_dict, f"{field_name}.")

def generate_sql_schema(module_name, fields):
    """Generate SQL CREATE TABLE statement based on discovered fields"""
    sql = f"-- Table for {module_name}\n"
    sql += f"CREATE TABLE IF NOT EXISTS {module_name} (\n"
    
    columns = []
    for field_name, field_info in sorted(fields.items()):
        # Skip nested fields for main table
        if '.' in field_name or '[' in field_name:
            continue
            
        # Map field types to SQL types
        sql_type = {
            'integer': 'BIGINT',
            'decimal': 'DECIMAL(15,2)',
            'string': 'TEXT',
            'boolean': 'BOOLEAN',
            'timestamp': 'TIMESTAMP WITH TIME ZONE',
            'array': 'JSONB',
            'object': 'JSONB',
            'null': 'TEXT'
        }.get(field_info['type'], 'TEXT')
        
        # Make id the primary key
        if field_name == 'id':
            columns.append(f"  {field_name} {sql_type} PRIMARY KEY")
        else:
            columns.append(f"  {field_name} {sql_type}")
    
    sql += ",\n".join(columns)
    sql += "\n);\n"
    
    return sql

def main():
    print("🔍 Freshworks CRM Field Discovery Tool")
    print(f"Domain: {DOMAIN}")
    print(f"API Key: {API_KEY[:10]}...")
    
    # Define endpoints to analyze
    endpoints = {
        'deals': f'https://{DOMAIN}/crm/sales/api/deals',
        'contacts': f'https://{DOMAIN}/crm/sales/api/contacts',
        'accounts': f'https://{DOMAIN}/crm/sales/api/accounts',
        'sales_activities': f'https://{DOMAIN}/crm/sales/api/sales_activities',
        'appointments': f'https://{DOMAIN}/crm/sales/api/appointments',
        'tasks': f'https://{DOMAIN}/crm/sales/api/tasks',
        'products': f'https://{DOMAIN}/crm/sales/api/products',
        'leads': f'https://{DOMAIN}/crm/sales/api/leads',
        'notes': f'https://{DOMAIN}/crm/sales/api/notes'
    }
    
    discovered_schemas = {}
    sql_statements = []
    
    for module_name, endpoint_url in endpoints.items():
        fields = discover_fields(module_name, endpoint_url)
        if fields:
            discovered_schemas[module_name] = fields
            
            # Generate SQL schema
            sql = generate_sql_schema(module_name, fields)
            sql_statements.append(sql)
            
            # Print field summary
            print(f"\n📊 {module_name.upper()} - Found {len(fields)} fields:")
            for field_name, field_info in sorted(fields.items()):
                if '.' not in field_name and '[' not in field_name:  # Only show top-level fields
                    print(f"  - {field_name}: {field_info['type']}")
    
    # Save discovered schemas
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save field mappings
    with open(f'discovered_fields_{timestamp}.json', 'w') as f:
        json.dump(discovered_schemas, f, indent=2)
    print(f"\n✅ Field mappings saved to: discovered_fields_{timestamp}.json")
    
    # Save SQL schema
    with open(f'complete_db_schema_{timestamp}.sql', 'w') as f:
        f.write("-- Complete Freshworks CRM Database Schema\n")
        f.write("-- Auto-generated from API discovery\n\n")
        f.write("\n\n".join(sql_statements))
    print(f"✅ SQL schema saved to: complete_db_schema_{timestamp}.sql")
    
    # Generate enhanced sync script
    generate_sync_script(discovered_schemas, timestamp)
    
    print("\n🎉 Discovery complete! Next steps:")
    print("1. Review the generated SQL schema")
    print("2. Run the SQL to create all tables")
    print("3. Use the generated sync script to fetch all data")

def generate_sync_script(schemas, timestamp):
    """Generate a complete sync script based on discovered fields"""
    script = '''import requests
import psycopg2
import json
import os
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'crm_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASS', 'postgres')
)
cur = conn.cursor()

# Freshworks API setup
DOMAIN = os.getenv('FRESHWORKS_DOMAIN', 'kambaacrm.myfreshworks.com')
API_KEY = os.getenv('FRESHWORKS_API_KEY')
headers = {'Authorization': f'Token token={API_KEY}', 'Content-Type': 'application/json'}

def sync_module(module_name, endpoint_url, field_mapping):
    """Sync all data from a module"""
    print(f"\\nSyncing {module_name}...")
    
    page = 1
    total_synced = 0
    
    while True:
        try:
            url = f"{endpoint_url}?page={page}&per_page=100&include=*"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
                
            data = response.json()
            
            # Extract records
            records = []
            if module_name in data:
                records = data[module_name]
            elif 'data' in data:
                records = data['data']
            elif isinstance(data, list):
                records = data
                
            if not records:
                break
                
            # Insert records
            for record in records:
                insert_record(module_name, record, field_mapping)
                
            total_synced += len(records)
            print(f"  Page {page}: {len(records)} records")
            
            # Check for more pages
            if 'meta' in data and 'total_pages' in data['meta']:
                if page >= data['meta']['total_pages']:
                    break
            elif len(records) < 100:
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error syncing {module_name}: {e}")
            break
    
    conn.commit()
    print(f"✅ {module_name}: {total_synced} records synced")
    return total_synced

def insert_record(table_name, record, field_mapping):
    """Insert a single record into the database"""
    columns = []
    values = []
    
    for field_name, field_info in field_mapping.items():
        # Skip nested fields
        if '.' in field_name or '[' in field_name:
            continue
            
        value = record.get(field_name)
        
        # Handle different data types
        if field_info['type'] in ['array', 'object'] and value is not None:
            value = json.dumps(value)
            
        columns.append(field_name)
        values.append(value)
    
    # Build INSERT query with ON CONFLICT UPDATE
    placeholders = ','.join(['%s'] * len(values))
    update_clause = ','.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])
    
    query = f"""
        INSERT INTO {table_name} ({','.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
    """
    
    try:
        cur.execute(query, values)
    except Exception as e:
        print(f"Error inserting record: {e}")
        conn.rollback()

# Main sync process
'''
    
    script += f"\nfield_mappings = {json.dumps(schemas, indent=2)}\n\n"
    
    script += '''
endpoints = {
    'deals': f'https://{DOMAIN}/crm/sales/api/deals',
    'contacts': f'https://{DOMAIN}/crm/sales/api/contacts',
    'accounts': f'https://{DOMAIN}/crm/sales/api/accounts',
    'sales_activities': f'https://{DOMAIN}/crm/sales/api/sales_activities',
    'appointments': f'https://{DOMAIN}/crm/sales/api/appointments',
    'tasks': f'https://{DOMAIN}/crm/sales/api/tasks',
    'products': f'https://{DOMAIN}/crm/sales/api/products',
    'leads': f'https://{DOMAIN}/crm/sales/api/leads',
    'notes': f'https://{DOMAIN}/crm/sales/api/notes'
}

print("🔄 Starting Freshworks CRM Full Sync")
print(f"Domain: {DOMAIN}")

total_records = 0
for module_name, endpoint_url in endpoints.items():
    if module_name in field_mappings:
        count = sync_module(module_name, endpoint_url, field_mappings[module_name])
        total_records += count

print(f"\\n✅ Sync complete! Total records: {total_records}")

# Close database connection
cur.close()
conn.close()
'''
    
    with open(f'complete_sync_script_{timestamp}.py', 'w') as f:
        f.write(script)
    print(f"✅ Sync script saved to: complete_sync_script_{timestamp}.py")

if __name__ == '__main__':
    main() 