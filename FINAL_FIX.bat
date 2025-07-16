@echo off
echo ==========================================
echo KAMBAA CRM - COMPLETE FIX
echo ==========================================
echo.

REM Stop everything first
echo [*] Stopping all Docker containers...
docker-compose down
docker stop tooljet postgres 2>nul
docker rm tooljet postgres 2>nul

echo.
echo [*] Using fixed Docker configuration...
copy docker-compose-fixed.yml docker-compose.yml /Y

echo.
echo [*] Starting services with correct configuration...
docker-compose up -d

echo.
echo [*] Waiting for services to start (40 seconds)...
echo Progress: 
for /L %%i in (1,1,40) do (
    <nul set /p =.
    timeout /t 1 /nobreak >nul
)
echo.

echo.
echo [*] Checking service status...
docker ps

echo.
echo ==========================================
echo TOOLJET ACCESS
echo ==========================================
echo.
echo ToolJet should now be accessible at:
echo.
echo    http://localhost:3000
echo.
echo Default setup:
echo 1. Open http://localhost:3000 in your browser
echo 2. Click "Sign up" to create an account
echo 3. Use any email/password (e.g., admin@kambaa.com)
echo.
echo ==========================================
echo FRESHWORKS DATA SYNC
echo ==========================================
echo.
echo To test Freshworks connection:
echo    python sync_kambaa_data_simple.py
echo.
echo Note: SSL handshake error may require:
echo - VPN connection
echo - Different network
echo - IT whitelist for kambaacrm.myfreshworks.com
echo.
echo ==========================================
echo NEXT STEPS
echo ==========================================
echo.
echo 1. Access ToolJet at http://localhost:3000
echo 2. Follow CLIENT_DEMO_GUIDE.md to set up chatbot
echo 3. Configure data sources with your credentials
echo.
start http://localhost:3000
pause 