import os

def main():
    print("Easy Analytics - API Key Configuration")
    print("=====================================")
    
    # Create ToolJet directory if it doesn't exist
    if not os.path.exists('ToolJet'):
        os.makedirs('ToolJet')
    
    # Prompt for keys
    freshworks_domain = input('Enter Freshworks domain (e.g., mycompany.freshworks.com): ')
    freshworks_key = input('Enter Freshworks API key: ')
    openai_key = input('Enter OpenAI API key: ')
    
    # Write to .env
    env_content = f"""# ToolJet Configuration
TOOLJET_HOST=http://localhost:3000
PG_DB=tooljet_prod
PG_USER=postgres
PG_PASS=tooljet

# API Keys for Easy Analytics
FRESHWORKS_DOMAIN={freshworks_domain}
FRESHWORKS_API_KEY={freshworks_key}
OPENAI_API_KEY={openai_key}

# Security
SECRET_KEY_BASE=your_secret_key_here
LOCKBOX_MASTER_KEY=your_lockbox_key_here
"""
    
    with open('ToolJet/.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✓ API keys saved to ToolJet/.env")
    print("\nNext steps:")
    print("1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/")
    print("2. After Docker is installed, run: python setup.py")
    print("3. Or manually start ToolJet with: cd ToolJet/deploy/docker && docker-compose up -d")

if __name__ == '__main__':
    main() 