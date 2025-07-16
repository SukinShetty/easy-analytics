# Easy Analytics Quick Start Script for Windows
# This script sets up and launches the complete testing environment

Write-Host "[EASY ANALYTICS - QUICK START]" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[*] Checking prerequisites..." -ForegroundColor Yellow
$dockerRunning = $null -ne (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)

if (-not $dockerRunning) {
    Write-Host "[X] Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Docker Desktop is running" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or later from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "[*] Setting up environment..." -ForegroundColor Yellow
    
    # Check for OpenAI API key
    $openaiKey = Read-Host "Enter your OpenAI API key (required for chatbot)"
    
    if ([string]::IsNullOrWhiteSpace($openaiKey)) {
        Write-Host "[X] OpenAI API key is required!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Copy template and set key
    Copy-Item "env.template" ".env"
    (Get-Content ".env") -replace 'OPENAI_API_KEY=sk-your_openai_api_key_here', "OPENAI_API_KEY=$openaiKey" | Set-Content ".env"
    
    # Set test defaults
    $content = Get-Content ".env" -Raw
    $replacements = @{
        'your_super_secure_password_here_min_32_chars' = 'test_password_for_development_only_32chars'
        'your_secret_key_base_64_chars_minimum_here' = 'test_secret_key_base_for_development_64_chars_minimum_here_ok'
        'your_lockbox_master_key_here' = 'test_lockbox_master_key_development'
        'your_redis_password_here_min_20_chars' = 'test_redis_password_20_chars_min'
        'your_grafana_admin_password' = 'admin_password_123'
        'your-domain.com' = 'localhost'
        'admin@your-domain.com' = 'admin@localhost'
        'your-company.freshworks.com' = 'demo.freshworks.com'
        'your_freshworks_api_key_here' = 'demo_api_key'
    }
    
    foreach ($key in $replacements.Keys) {
        $content = $content -replace $key, $replacements[$key]
    }
    
    Set-Content ".env" $content
    Write-Host "[OK] Environment configured" -ForegroundColor Green
}

# Install dependencies
Write-Host ""
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements-test.txt --quiet

# Start services
Write-Host ""
Write-Host "[*] Starting Docker services..." -ForegroundColor Yellow
docker-compose down 2>$null
docker-compose up -d

# Wait for services
Write-Host ""
Write-Host "[*] Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$tooljetRunning = docker ps --format "table {{.Names}}" | Select-String "tooljet"
$postgresRunning = docker ps --format "table {{.Names}}" | Select-String "postgres"

if (-not $tooljetRunning -or -not $postgresRunning) {
    Write-Host "[X] Services failed to start!" -ForegroundColor Red
    Write-Host "Check Docker logs: docker-compose logs" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] All services are running" -ForegroundColor Green

# Run database setup
Write-Host ""
Write-Host "[*] Setting up database..." -ForegroundColor Yellow
python test_chatbot.py

# Create config files
Write-Host ""
Write-Host "[*] Creating configuration files..." -ForegroundColor Yellow
if (-not (Test-Path "tooljet_app_config.json")) {
    python setup_complete_test.py
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[OK] Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[>] ToolJet is running at: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "[i] Follow the setup guide in CLIENT_DEMO_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  - View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "  - Stop:         docker-compose down" -ForegroundColor White
Write-Host "  - Restart:      docker-compose restart" -ForegroundColor White
Write-Host ""

# Ask to open browser
$response = Read-Host "Open ToolJet in browser? (Y/n)"
if ($response -ne 'n') {
    Start-Process "http://localhost:8080"
}

Write-Host ""
Write-Host "Happy testing!" -ForegroundColor Green 