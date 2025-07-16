@echo off
echo ==========================================
echo SYSTEM STATUS CHECK
echo ==========================================
echo.

echo [1] Docker Status:
docker --version
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [2] Network Test:
echo Testing localhost:8080...
curl -I http://localhost:8080 2>nul
if errorlevel 1 (
    echo Port 8080: NOT RESPONDING
) else (
    echo Port 8080: OK
)

echo.
echo Testing localhost:3000...
curl -I http://localhost:3000 2>nul
if errorlevel 1 (
    echo Port 3000: NOT RESPONDING
) else (
    echo Port 3000: OK
)

echo.
echo [3] Container Logs (last 10 lines):
echo.
echo ToolJet logs:
docker logs easy-analytics-tooljet-1 --tail 10 2>&1

echo.
echo [4] Port Bindings:
docker port easy-analytics-tooljet-1 2>&1

echo.
echo ==========================================
echo QUICK FIXES:
echo ==========================================
echo.
echo If ToolJet not accessible:
echo 1. Run: docker-compose restart tooljet
echo 2. Wait 30 seconds
echo 3. Try: http://localhost:3000
echo.
pause 