@echo off
echo [*] Testing Freshworks Working Endpoints
echo ==========================================

echo [*] Running working endpoints test...
python sync_working_endpoints.py

echo.
echo [*] Test completed!
echo [*] Check the 'freshworks_data' folder for results
echo.

if exist "freshworks_data" (
    echo [*] Data files created:
    dir "freshworks_data" /b
) else (
    echo [X] No data folder created - check for errors above
)

echo.
echo [*] Press any key to exit...
pause >nul 