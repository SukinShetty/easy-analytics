@echo off
echo ==========================================
echo Easy Analytics - Real Freshworks Data Sync
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Check for placeholder values in .env
findstr /C:"your_freshworks_api_key_here" .env >nul
if not errorlevel 1 (
    echo [ERROR] You need to configure your REAL Freshworks credentials!
    echo.
    echo Opening .env file...
    echo Please update these values:
    echo   - FRESHWORKS_DOMAIN: Your actual Freshworks domain
    echo   - FRESHWORKS_API_KEY: Your actual API key
    echo   - OPENAI_API_KEY: Your OpenAI API key
    echo.
    notepad .env
    echo.
    echo After updating, run this script again.
    pause
    exit /b 1
)

echo [*] Starting Docker services...
docker-compose up -d

echo.
echo [*] Installing Python dependencies...
python -m pip install requests psycopg2-binary python-dotenv

echo.
echo [*] Syncing your real Freshworks data...
echo This may take a few minutes depending on your data size...
echo.
python sync_freshworks_data.py

if errorlevel 1 (
    echo.
    echo [ERROR] Sync failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] SUCCESS! Your real data is synced!
echo ==========================================
echo.
echo Next steps:
echo 1. Open ToolJet at: http://localhost:8080
echo 2. Follow CLIENT_DEMO_GUIDE.md to set up the chatbot
echo 3. Ask questions about YOUR REAL CRM DATA!
echo.
echo Example questions:
echo - "What are my top deals this month?"
echo - "Show me all contacts from [your actual company]"
echo - "Which of my products are selling the most?"
echo.
start http://localhost:8080
pause 