@echo off
echo ==========================================
echo FIXING KAMBAA CRM SETUP ISSUES
echo ==========================================
echo.

REM Check Docker services
echo [*] Checking Docker services...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [*] Checking ToolJet logs...
docker logs easy-analytics-tooljet-1 --tail 20

echo.
echo [*] If ToolJet is not running on 8080, let's check the actual port...
docker port easy-analytics-tooljet-1

echo.
echo [*] Restarting services with correct port mapping...
docker-compose down
docker-compose up -d

echo.
echo [*] Waiting for services to fully start...
timeout /t 20 /nobreak

echo.
echo [*] Services status:
docker ps

echo.
echo ==========================================
echo CHECKING SERVICES
echo ==========================================
echo.
echo Try these URLs:
echo 1. http://localhost:8080 (default)
echo 2. http://localhost:3000 (alternative port)
echo.
echo If still not working, run: docker logs easy-analytics-tooljet-1
echo.
pause 