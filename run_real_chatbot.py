#!/usr/bin/env python3
"""
Run Easy Analytics Chatbot with REAL Freshworks CRM Data
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_credentials():
    """Check if real credentials are configured"""
    print("🔍 Checking credentials...")
    
    # Check Freshworks
    freshworks_domain = os.getenv('FRESHWORKS_DOMAIN', '')
    freshworks_api = os.getenv('FRESHWORKS_API_KEY', '')
    
    if not freshworks_domain or 'your' in freshworks_domain or 'demo' in freshworks_domain:
        print("\n❌ FRESHWORKS_DOMAIN not configured!")
        print("Please edit .env and set your actual Freshworks domain")
        print("Example: FRESHWORKS_DOMAIN=mycompany.freshworks.com")
        return False
    
    if not freshworks_api or 'your' in freshworks_api or 'demo' in freshworks_api:
        print("\n❌ FRESHWORKS_API_KEY not configured!")
        print("Please edit .env and set your actual Freshworks API key")
        print("You can find this in: Freshworks Settings → API Settings")
        return False
    
    # Check OpenAI
    openai_api = os.getenv('OPENAI_API_KEY', '')
    if not openai_api or 'your' in openai_api:
        print("\n❌ OPENAI_API_KEY not configured!")
        print("Please edit .env and set your OpenAI API key")
        return False
    
    print("✅ All credentials configured!")
    return True

def main():
    print("🚀 Easy Analytics - Real Freshworks Data Setup")
    print("=" * 50)
    
    # Check credentials
    if not check_credentials():
        print("\n📝 Please edit your .env file with real credentials:")
        print("   1. Open .env in a text editor")
        print("   2. Set FRESHWORKS_DOMAIN (e.g., mycompany.freshworks.com)")
        print("   3. Set FRESHWORKS_API_KEY (from Freshworks API Settings)")
        print("   4. Set OPENAI_API_KEY (from OpenAI platform)")
        
        # Open .env file for editing
        if sys.platform == "win32":
            os.system("notepad .env")
        else:
            print("\nEdit .env file and run this script again.")
        
        sys.exit(1)
    
    # Start services if not running
    print("\n🐳 Starting services...")
    subprocess.run(["docker-compose", "up", "-d"], capture_output=True)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "psycopg2-binary", "python-dotenv"], capture_output=True)
    
    # Run sync
    print("\n🔄 Syncing your Freshworks data...")
    result = subprocess.run([sys.executable, "sync_freshworks_data.py"])
    
    if result.returncode == 0:
        print("\n✅ SUCCESS! Your real Freshworks data is now synced!")
        print("\n🌐 Open ToolJet at: http://localhost:8080")
        print("\n📖 Follow CLIENT_DEMO_GUIDE.md to set up the chatbot")
        print("\nYou can now ask questions about YOUR REAL CRM DATA!")
        
        # Open browser
        if sys.platform == "win32":
            subprocess.run(["start", "http://localhost:8080"], shell=True)
    else:
        print("\n❌ Sync failed. Check the error messages above.")

if __name__ == "__main__":
    main() 