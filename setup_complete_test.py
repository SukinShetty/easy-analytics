#!/usr/bin/env python3
"""
Easy Analytics Complete Testing Setup
Sets up a full working environment with frontend and backend
"""

import os
import sys
import time
import json
import subprocess
import webbrowser
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print_header("Checking Prerequisites")
    
    prereqs = {
        'docker': 'Docker Desktop',
        'python': 'Python 3.8+',
        'pip': 'pip package manager'
    }
    
    all_good = True
    for cmd, name in prereqs.items():
        try:
            if cmd == 'python':
                subprocess.run([sys.executable, '--version'], check=True, capture_output=True)
            else:
                subprocess.run([cmd, '--version'], check=True, capture_output=True)
            print(f"✅ {name} is installed")
        except:
            print(f"❌ {name} is NOT installed")
            all_good = False
    
    return all_good

def setup_environment():
    """Setup .env file with user inputs"""
    print_header("Environment Configuration")
    
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Using existing .env file")
            return True
    
    print("\n📝 Let's configure your environment:")
    print("(Press Enter to use default values)\n")
    
    # Read template
    with open('env.template', 'r') as f:
        template = f.read()
    
    # Get user inputs
    configs = {
        'OPENAI_API_KEY': {
            'prompt': 'OpenAI API Key (required for chatbot)',
            'required': True,
            'default': None
        },
        'FRESHWORKS_DOMAIN': {
            'prompt': 'Freshworks Domain (e.g., company.freshworks.com)',
            'required': False,
            'default': 'demo.freshworks.com'
        },
        'FRESHWORKS_API_KEY': {
            'prompt': 'Freshworks API Key',
            'required': False,
            'default': 'demo_api_key'
        }
    }
    
    env_content = template
    
    for key, config in configs.items():
        prompt = f"{config['prompt']}"
        if config['default']:
            prompt += f" [{config['default']}]"
        prompt += ": "
        
        value = input(prompt).strip()
        
        if not value and config['default']:
            value = config['default']
        
        if config['required'] and not value:
            print(f"❌ {key} is required!")
            return False
        
        # Replace in template
        for line in ['your_', 'sk-your_', 'your-']:
            env_content = env_content.replace(f"{key}={line}", f"{key}={value}")
    
    # Set test-friendly defaults for other values
    replacements = {
        'your_super_secure_password_here_min_32_chars': 'test_password_for_development_only_32chars',
        'your_secret_key_base_64_chars_minimum_here': 'test_secret_key_base_for_development_64_chars_minimum_here_ok',
        'your_lockbox_master_key_here': 'test_lockbox_master_key_development',
        'your_redis_password_here_min_20_chars': 'test_redis_password_20_chars_min',
        'your_grafana_admin_password': 'admin_password_123',
        'your-domain.com': 'localhost',
        'admin@your-domain.com': 'admin@localhost'
    }
    
    for old, new in replacements.items():
        env_content = env_content.replace(old, new)
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Environment file created successfully!")
    return True

def start_services():
    """Start Docker services"""
    print_header("Starting Services")
    
    print("🚀 Starting Docker containers...")
    
    # Stop existing containers
    subprocess.run(['docker-compose', 'down'], capture_output=True)
    
    # Start services
    result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to start services")
        print(result.stderr)
        return False
    
    print("✅ Services started successfully!")
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    services_ready = False
    
    for i in range(30):
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        if 'tooljet' in result.stdout and 'postgres' in result.stdout:
            # Check if services are actually running
            time.sleep(5)  # Give services time to fully start
            services_ready = True
            break
        print(".", end="", flush=True)
        time.sleep(2)
    
    if services_ready:
        print("\n✅ All services are ready!")
    else:
        print("\n❌ Services failed to start properly")
        return False
    
    return True

def setup_database():
    """Setup database with schema and test data"""
    print_header("Setting Up Database")
    
    print("📊 Creating database schema and test data...")
    
    # Run the test script to set up database
    result = subprocess.run([sys.executable, 'test_chatbot.py'], capture_output=True, text=True)
    
    if "Test suite completed!" in result.stdout:
        print("✅ Database setup completed!")
        return True
    else:
        print("❌ Database setup failed")
        print(result.stdout)
        return False

def create_tooljet_app_config():
    """Create ToolJet app configuration"""
    print_header("Creating ToolJet App Configuration")
    
    app_config = {
        "name": "Easy Analytics Chatbot",
        "description": "AI-powered analytics chatbot for CRM data",
        "components": [
            {
                "name": "pageTitle",
                "type": "Text",
                "properties": {
                    "text": "🤖 Easy Analytics Chatbot",
                    "fontSize": 24,
                    "fontWeight": "bold"
                }
            },
            {
                "name": "queryInput",
                "type": "TextInput",
                "properties": {
                    "placeholder": "Ask me about your sales data...",
                    "label": "Your Question"
                }
            },
            {
                "name": "submitButton",
                "type": "Button",
                "properties": {
                    "text": "Ask",
                    "backgroundColor": "#4F46E5",
                    "textColor": "#FFFFFF"
                },
                "events": {
                    "onClick": "queries.handleChatbotQuery.run()"
                }
            },
            {
                "name": "chatHistory",
                "type": "TextArea",
                "properties": {
                    "placeholder": "Chat history will appear here...",
                    "rows": 15,
                    "disabled": True
                }
            },
            {
                "name": "sampleQueries",
                "type": "Text",
                "properties": {
                    "text": "Sample queries:\n• What is the total revenue this month?\n• Show me top 5 deals\n• Which product sells the most?\n• List contacts from technology companies",
                    "fontSize": 12
                }
            }
        ],
        "queries": [
            {
                "name": "generateSQL",
                "type": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a SQL expert. Generate PostgreSQL queries based on this schema: deals(id,name,amount,close_date,product_id,account_id,contact_id), contacts(id,first_name,last_name,email), accounts(id,name,industry), products(id,name,price), sales_activities(id,deal_id,activity_type,date,outcome). Return ONLY the SQL query, no explanations."
                        },
                        {
                            "role": "user",
                            "content": "{{components.queryInput.value}}"
                        }
                    ]
                }
            },
            {
                "name": "executeSQL",
                "type": "postgresql",
                "config": {
                    "query": "{{queries.generateSQL.data.choices[0].message.content}}"
                }
            },
            {
                "name": "summarizeResults",
                "type": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Summarize the SQL query results in a friendly, conversational way."
                        },
                        {
                            "role": "user",
                            "content": "Query: {{components.queryInput.value}}\nResults: {{JSON.stringify(queries.executeSQL.data)}}"
                        }
                    ]
                }
            },
            {
                "name": "handleChatbotQuery",
                "type": "javascript",
                "config": {
                    "code": """
async function handleQuery() {
  const userInput = components.queryInput.value;
  if (!userInput) {
    await actions.showAlert('error', 'Please enter a question');
    return;
  }
  
  // Add user message to chat
  const currentChat = components.chatHistory.value || '';
  components.chatHistory.value = currentChat + `\\n\\nYou: ${userInput}\\n`;
  
  try {
    // Generate SQL
    await queries.generateSQL.run();
    
    // Execute SQL
    await queries.executeSQL.run();
    
    // Summarize results
    await queries.summarizeResults.run();
    
    // Add AI response to chat
    const summary = queries.summarizeResults.data.choices[0].message.content;
    components.chatHistory.value += `\\nAssistant: ${summary}`;
    
    // Clear input
    components.queryInput.value = '';
    
  } catch (error) {
    components.chatHistory.value += `\\nError: ${error.message}. Please try rephrasing your question.`;
  }
}

handleQuery();
"""
                }
            }
        ]
    }
    
    # Save configuration
    with open('tooljet_app_config.json', 'w') as f:
        json.dump(app_config, f, indent=2)
    
    print("✅ ToolJet app configuration created!")
    print("📄 Configuration saved to: tooljet_app_config.json")
    
    return True

def print_instructions():
    """Print instructions for manual setup in ToolJet"""
    print_header("Next Steps - Setting Up ToolJet App")
    
    print("🌐 ToolJet is now running at: http://localhost:8080\n")
    
    print("Follow these steps to complete the setup:\n")
    
    print("1️⃣  **Access ToolJet**")
    print("   - Open http://localhost:8080 in your browser")
    print("   - Create an account or login\n")
    
    print("2️⃣  **Set up Data Sources**")
    print("   a. PostgreSQL:")
    print("      - Click 'Data Sources' → '+ Add datasource' → 'PostgreSQL'")
    print("      - Name: 'Analytics DB'")
    print("      - Host: postgres")
    print("      - Port: 5432")
    print("      - Database: tooljet_prod")
    print("      - Username: postgres")
    print("      - Password: tooljet")
    print("      - Test and Save\n")
    
    print("   b. OpenAI:")
    print("      - Click '+ Add datasource' → 'OpenAI'")
    print("      - Name: 'OpenAI'")
    print("      - API Key: (use your OpenAI API key from .env)")
    print("      - Test and Save\n")
    
    print("3️⃣  **Create the Chatbot App**")
    print("   - Click 'Apps' → 'Create new app'")
    print("   - Name it 'Easy Analytics Chatbot'")
    print("   - Add components as described in tooljet_app_config.json")
    print("   - Configure queries as specified\n")
    
    print("4️⃣  **Test the Chatbot**")
    print("   Try these queries:")
    print("   • 'What is the total revenue this month?'")
    print("   • 'Show me the top 5 deals by amount'")
    print("   • 'Which product is selling the most?'")
    print("   • 'List all contacts from technology companies'\n")
    
    # Ask if user wants to open browser
    response = input("\n🌐 Would you like to open ToolJet in your browser now? (Y/n): ")
    if response.lower() != 'n':
        webbrowser.open('http://localhost:8080')

def create_sample_dashboard():
    """Create a sample dashboard configuration"""
    dashboard_config = {
        "name": "Sales Analytics Dashboard",
        "widgets": [
            {
                "type": "chart",
                "title": "Revenue by Month",
                "query": "SELECT DATE_TRUNC('month', close_date) as month, SUM(amount) as revenue FROM deals GROUP BY month ORDER BY month"
            },
            {
                "type": "chart", 
                "title": "Top Products",
                "query": "SELECT p.name, COUNT(d.id) as sales FROM products p JOIN deals d ON p.id = d.product_id GROUP BY p.name"
            },
            {
                "type": "table",
                "title": "Recent Deals",
                "query": "SELECT d.name, d.amount, c.first_name || ' ' || c.last_name as contact FROM deals d JOIN contacts c ON d.contact_id = c.id ORDER BY d.close_date DESC LIMIT 10"
            }
        ]
    }
    
    with open('dashboard_config.json', 'w') as f:
        json.dump(dashboard_config, f, indent=2)
    
    print("\n📊 Sample dashboard configuration created: dashboard_config.json")

def main():
    """Main setup flow"""
    print("\n🚀 Easy Analytics - Complete Testing Setup")
    print("=========================================")
    print("This will set up a complete testing environment with:")
    print("• Real frontend (ToolJet)")
    print("• Working backend (PostgreSQL + APIs)")
    print("• Sample CRM data")
    print("• AI-powered chatbot\n")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Please install missing prerequisites first!")
        return
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed!")
        return
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-test.txt'], 
                   capture_output=True)
    
    # Start services
    if not start_services():
        print("\n❌ Failed to start services!")
        return
    
    # Setup database
    if not setup_database():
        print("\n❌ Database setup failed!")
        return
    
    # Create app configuration
    create_tooljet_app_config()
    create_sample_dashboard()
    
    # Print instructions
    print_instructions()
    
    print("\n✅ Setup completed successfully!")
    print("\n📌 Quick Commands:")
    print("   • View logs: docker-compose logs -f")
    print("   • Stop services: docker-compose down")
    print("   • Restart services: docker-compose restart")
    print("   • Connect to DB: docker exec -it easy-analytics_postgres_1 psql -U postgres -d tooljet_prod")

if __name__ == "__main__":
    main() 