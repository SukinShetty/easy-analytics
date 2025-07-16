@echo off
echo ========================================
echo Easy Analytics - Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [OK] Docker is running

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python from python.org
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check for .env file
if not exist .env (
    echo.
    echo [*] Creating environment file...
    copy env.template .env >nul
    echo.
    echo [!] IMPORTANT: Edit .env file and add your OpenAI API key
    echo [!] Look for: OPENAI_API_KEY=sk-your_openai_api_key_here
    echo.
    notepad .env
    pause
)

REM Install dependencies
echo.
echo [*] Installing Python dependencies...
python -m pip install -r requirements-test.txt

REM Start services
echo.
echo [*] Starting Docker services...
docker-compose down >nul 2>&1
docker-compose up -d

REM Wait for services
echo [*] Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Setup database
echo.
echo [*] Setting up database...
python test_chatbot.py

echo.
echo ========================================
echo [OK] Setup Complete!
echo ========================================
echo.
echo ToolJet is running at: http://localhost:8080
echo.
echo Follow the guide in CLIENT_DEMO_GUIDE.md
echo.
echo Commands:
echo   - View logs: docker-compose logs -f
echo   - Stop: docker-compose down
echo.
start http://localhost:8080
pause 