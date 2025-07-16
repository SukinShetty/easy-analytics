@echo off
echo ==========================================
echo STARTING TOOLJET FOR KAMBAA CRM
echo ==========================================
echo.

REM Stop all services first
echo [*] Stopping existing services...
docker-compose down

REM Check docker-compose.yml for correct port mapping
echo.
echo [*] Current port configuration:
findstr "ports:" docker-compose.yml
findstr "8080" docker-compose.yml
findstr "3000" docker-compose.yml

echo.
echo [*] Starting fresh...
docker-compose up -d

echo.
echo [*] Waiting for ToolJet to start (30 seconds)...
timeout /t 30 /nobreak

echo.
echo [*] Current running services:
docker ps

echo.
echo [*] ToolJet container logs:
docker logs easy-analytics-tooljet-1 --tail 50

echo.
echo ==========================================
echo TOOLJET ACCESS INFORMATION
echo ==========================================
echo.
echo ToolJet should now be available at:
echo   - http://localhost:8080
echo   - http://localhost:3000 (if port was changed)
echo.
echo If you see any errors above, please share them.
echo.
echo To manually check ToolJet status:
echo   docker logs easy-analytics-tooljet-1 -f
echo.
pause 