# New file content
import os
import subprocess
import sys

def main():
    # Check Docker
    try:
        subprocess.run(['docker', '--version'], check=True)
    except:
        print('Install Docker first.')
        sys.exit(1)
    
    # Clone ToolJet if not present
    if not os.path.exists('ToolJet'):
        subprocess.run(['git', 'clone', 'https://github.com/ToolJet/ToolJet.git'])
    
    # Prompt for keys
    freshworks_domain = input('Enter Freshworks domain (e.g., mycompany.freshworks.com): ')
    freshworks_key = input('Enter Freshworks API key: ')
    openai_key = input('Enter OpenAI API key: ')
    
    # Write to .env
    with open('ToolJet/.env', 'w') as f:
        f.write(f'TOOLJET_HOST=http://localhost:3000\n')
        f.write(f'PG_DB=tooljet_prod\n')
        f.write(f'PG_USER=postgres\n')
        f.write(f'PG_PASS=tooljet\n')
        f.write(f'FRESHWORKS_DOMAIN={freshworks_domain}\n')
        f.write(f'FRESHWORKS_API_KEY={freshworks_key}\n')
        f.write(f'OPENAI_API_KEY={openai_key}\n')
    
    # Start Docker (assume docker-compose.yml in ToolJet/deploy/docker)
    os.chdir('ToolJet/deploy/docker')
    subprocess.run(['docker-compose', 'up', '-d'])
    print('Easy Analytics running at http://localhost:3000. Customize in ToolJet dashboard.')

if __name__ == '__main__':
    main() 