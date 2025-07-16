#!/usr/bin/env python3
"""
Quick setup for Kambaa CRM - Easy Analytics
Automatically configures environment and syncs real Freshworks data
"""

import os
import shutil
import subprocess
import sys

def setup_environment():
    """Set up the .env file with provided credentials"""
    print("🔧 Setting up your Kambaa CRM environment...")
    
    # Your provided credentials
    env_content = """# Easy Analytics Production Environment Configuration
# Configured for Kambaa CRM

# =================
# Core Application
# =================
TOOLJET_HOST=http://localhost:8080
NODE_ENV=production

# =================
# Database Settings
# =================
PG_DB=tooljet_prod
PG_USER=postgres
PG_PASS=test_password_for_development_only_32chars
PG_HOST=postgres
PG_PORT=5432

# ToolJet Database (can be same as above)
TOOLJET_DB=tooljet_prod
TOOLJET_DB_USER=postgres
TOOLJET_DB_PASS=test_password_for_development_only_32chars
TOOLJET_DB_HOST=postgres
TOOLJET_DB_PORT=5432

# =================
# Security Keys (TEST ENVIRONMENT)
# =================
SECRET_KEY_BASE=test_secret_key_base_for_development_64_chars_minimum_here_ok
LOCKBOX_MASTER_KEY=test_lockbox_master_key_development

# =================
# External APIs - YOUR REAL CREDENTIALS
# =================
FRESHWORKS_DOMAIN=kambaacrm.myfreshworks.com
FRESHWORKS_API_KEY=2IbbXJgW_QJLDOBwl7Znqw
OPENAI_API_KEY=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

# =================
# Cache Settings
# =================
REDIS_PASSWORD=test_redis_password_20_chars_min

# =================
# SSL Configuration (Local Testing)
# =================
SSL_EMAIL=admin@localhost
SSL_DOMAIN=localhost
ACME_SERVER=https://acme-v02.api.letsencrypt.org/directory

# =================
# Other Settings
# =================
BACKUP_WEBHOOK_URL=https://localhost/backup
SLACK_WEBHOOK_URL=https://localhost/slack
PROMETHEUS_RETENTION=7d
GRAFANA_ADMIN_PASSWORD=admin_password_123
"""
    
    # Backup existing .env if it exists
    if os.path.exists('.env'):
        shutil.copy('.env', '.env.backup')
        print("✅ Backed up existing .env to .env.backup")
    
    # Write new .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment configured with your Kambaa CRM credentials!")

def main():
    print("🚀 Kambaa CRM - Easy Analytics Setup")
    print("=" * 50)
    
    # Set up environment
    setup_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt", "--quiet"])
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "psycopg2-binary", "python-dotenv", "--quiet"])
    
    # Start Docker services
    print("\n🐳 Starting Docker services...")
    subprocess.run(["docker-compose", "down"], capture_output=True)
    result = subprocess.run(["docker-compose", "up", "-d"])
    
    if result.returncode != 0:
        print("❌ Failed to start Docker services. Make sure Docker Desktop is running!")
        sys.exit(1)
    
    print("⏳ Waiting for services to start...")
    import time
    time.sleep(15)
    
    # Run the sync
    print("\n🔄 Syncing your Kambaa CRM data from Freshworks...")
    print("This will fetch:")
    print("  • Contacts")
    print("  • Accounts/Companies") 
    print("  • Products")
    print("  • Deals")
    print("  • Sales Activities")
    print("\nThis may take a few minutes depending on your data volume...\n")
    
    result = subprocess.run([sys.executable, "sync_freshworks_data.py"])
    
    if result.returncode == 0:
        print("\n✅ SUCCESS! Your Kambaa CRM data is now synced!")
        print("\n📊 You can now ask questions like:")
        print("  • 'What are my top deals this month?'")
        print("  • 'Show me all contacts from [company name]'")
        print("  • 'Which products are selling the most?'")
        print("  • 'What's my total pipeline value?'")
        print("  • 'Show recent sales activities'")
        print("\n🌐 Open ToolJet at: http://localhost:8080")
        print("📖 Follow CLIENT_DEMO_GUIDE.md to set up the chatbot UI")
        
        # Open browser
        if sys.platform == "win32":
            subprocess.run(["start", "http://localhost:8080"], shell=True)
    else:
        print("\n❌ Data sync failed. Check the error messages above.")
        print("Common issues:")
        print("  • Check if Docker is running")
        print("  • Verify your internet connection")
        print("  • Ensure Freshworks API access is enabled for your account")

if __name__ == "__main__":
    main() 