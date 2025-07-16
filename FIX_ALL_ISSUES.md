# Fix Guide for Kambaa CRM Setup

## Issues Found:
1. ✅ ToolJet is not accessible at localhost:8080
2. ✅ Freshworks API connection has SSL handshake failure
3. ✅ psycopg2-binary installation fails on Python 3.13

## Quick Fix Steps:

### 1. Fix ToolJet Access Issue

Run this to diagnose and fix:
```cmd
start_tooljet.bat
```

This will:
- Show current Docker status
- Display ToolJet logs
- Restart services properly

### 2. Test Freshworks Connection

Run this simple test first:
```cmd
python sync_kambaa_data_simple.py
```

This tests your Freshworks connection without database dependencies.

### 3. Install Database Driver

For Python 3.13, install the compatible version:
```cmd
pip install psycopg2-binary==2.9.5
```

If that fails, try:
```cmd
pip install psycopg-binary
```

### 4. Complete Manual Setup

If automated scripts fail:

#### A. Start Services Manually:
```cmd
docker-compose down
docker-compose up -d
```

#### B. Check Service Status:
```cmd
docker ps
```

You should see:
- easy-analytics-tooljet-1 (ports 8080->3000)
- easy-analytics-postgres-1 (ports 5432->5432)

#### C. Access ToolJet:
- Try: http://localhost:8080
- Alternative: http://localhost:3000

#### D. If ToolJet Still Not Working:
```cmd
docker logs easy-analytics-tooljet-1 -f
```

Share the error logs for specific help.

## Alternative: Docker Compose Fix

If port 8080 is not working, edit `docker-compose.yml`:

Change:
```yaml
ports:
  - '8080:3000'
```

To:
```yaml
ports:
  - '3000:3000'
```

Then restart:
```cmd
docker-compose down
docker-compose up -d
```

Access at: http://localhost:3000

## SSL Issue with Freshworks

The SSL handshake failure suggests:
1. Corporate firewall blocking the connection
2. SSL certificate issues

Workarounds:
1. Try from a different network
2. Use a VPN
3. Contact IT to whitelist kambaacrm.myfreshworks.com

## Next Steps Once Fixed:

1. When ToolJet is accessible, create an account
2. Set up data sources:
   - PostgreSQL: localhost:5432
   - OpenAI: Your API key
3. Create the chatbot UI following CLIENT_DEMO_GUIDE.md
4. Sync your Freshworks data when SSL issue is resolved 