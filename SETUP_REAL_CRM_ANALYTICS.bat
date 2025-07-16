@echo off
echo ================================================================
echo        🎉 KAMBAA CRM ANALYTICS DASHBOARD SETUP
echo                   Using REAL Freshworks Data!
echo ================================================================
echo.

echo [*] Step 1: Setting up database with REAL CRM data...
python setup_kambaa_crm.py

echo.
echo [*] Step 2: Loading REAL Freshworks data into database...
echo     📊 Sales Team: 4 members
echo     📅 Appointments: 25 real meetings  
echo     📈 Contact Statuses: 9 pipeline stages
echo.

echo [*] Step 3: Starting ToolJet dashboard...
cd /d "%~dp0"
echo Starting Docker services...
docker-compose -f docker-compose-fixed.yml up -d

echo.
echo [*] Step 4: Checking services...
timeout /t 10 /nobreak >nul

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ================================================================
echo                      🚀 SETUP COMPLETE!
echo ================================================================
echo.
echo ✅ KAMBAA CRM Analytics Dashboard is READY!
echo.
echo 🌐 Open your dashboard: http://localhost:3000
echo.
echo 📊 REAL DATA AVAILABLE:
echo    • Nestle meeting discussions
echo    • Active sales team (Jagan, Roehan, Sowmya)
echo    • 25 real appointments with Teams links
echo    • Contact pipeline stages
echo.
echo 💬 CHAT QUERIES YOU CAN TRY:
echo    "Show me upcoming meetings"
echo    "Who are our active sales team members?"
echo    "What appointments do we have this week?"
echo    "Show me all contact statuses"
echo.
echo 🔧 If issues occur:
echo    • Run: docker-compose -f docker-compose-fixed.yml restart
echo    • Check: docker logs tooljet
echo.
echo [*] Press any key to open dashboard...
pause >nul

start http://localhost:3000

echo.
echo [*] Dashboard opened! Happy analytics! 🎯
pause 