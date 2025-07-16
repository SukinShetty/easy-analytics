# Easy Analytics Production Setup Script for Windows
# "At Any Cost" Self-Hosting Deployment

param(
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Easy Analytics Production Setup for Windows

This script sets up a production-grade self-hosted analytics platform.
You'll need Docker Desktop for Windows installed and running.

Usage:
    .\setup-production.ps1

Prerequisites:
- Docker Desktop for Windows
- PowerShell 5.1 or higher
- At least 10GB free disk space
- Internet connection for SSL certificates (production)

For Linux/Mac users, use: ./setup-production.sh
"@
    exit 0
}

# Check if Docker is available
try {
    docker --version | Out-Null
} catch {
    Write-Error "❌ Docker is not installed or not running. Please install Docker Desktop for Windows first."
    Write-Host "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
} catch {
    Write-Error "❌ Docker Compose is not available. Please ensure Docker Desktop is properly installed."
    exit 1
}

Write-Host "🚀 Easy Analytics Production Setup for Windows" -ForegroundColor Green
Write-Host ""
Write-Host "This will set up a production-grade analytics platform with:" -ForegroundColor Cyan
Write-Host "✅ SSL encryption (self-signed for Windows/development)" -ForegroundColor Green
Write-Host "✅ Secure password generation" -ForegroundColor Green
Write-Host "✅ Automated backups" -ForegroundColor Green
Write-Host "✅ Monitoring and health checks" -ForegroundColor Green
Write-Host "✅ Nginx reverse proxy" -ForegroundColor Green
Write-Host ""

$continue = Read-Host "Continue with setup? (y/N)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Setup cancelled." -ForegroundColor Yellow
    exit 0
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path "logs", "backups", "nginx\ssl", "scripts", "monitoring" | Out-Null

# Generate environment file
Write-Host "🔐 Generating secure configuration..." -ForegroundColor Cyan

$env_content = @"
# Easy Analytics Production Configuration for Windows
# Generated on $(Get-Date)

# Core Application
TOOLJET_HOST=https://localhost
NODE_ENV=production

# Database Settings
PG_DB=tooljet_prod
PG_USER=postgres
PG_PASS=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_}))
PG_HOST=postgres
PG_PORT=5432

# ToolJet Database
TOOLJET_DB=tooljet_prod
TOOLJET_DB_USER=postgres
TOOLJET_DB_PASS=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_}))
TOOLJET_DB_HOST=postgres
TOOLJET_DB_PORT=5432

# Security Keys (Windows development - replace for production)
SECRET_KEY_BASE=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | % {[char]$_}))
LOCKBOX_MASTER_KEY=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_}))

# External APIs (you'll need to configure these)
FRESHWORKS_DOMAIN=your-company.freshworks.com
FRESHWORKS_API_KEY=your_freshworks_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# Cache Settings
REDIS_PASSWORD=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 24 | % {[char]$_}))

# SSL Configuration (self-signed for Windows development)
SSL_EMAIL=admin@localhost
SSL_DOMAIN=localhost

# Monitoring
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=$(-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | % {[char]$_}))
"@

$env_content | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Environment configuration created: .env" -ForegroundColor Green

Write-Host ""
Write-Host "🔧 Please edit the .env file and configure:" -ForegroundColor Yellow
Write-Host "   - FRESHWORKS_DOMAIN (your Freshworks CRM domain)" -ForegroundColor White
Write-Host "   - FRESHWORKS_API_KEY (your Freshworks API key)" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY (your OpenAI API key)" -ForegroundColor White
Write-Host ""

$ready = Read-Host "Have you configured the API keys in .env file? (y/N)"
if ($ready -ne "y" -and $ready -ne "Y") {
    Write-Host "Please edit the .env file and run this script again." -ForegroundColor Yellow
    Write-Host "You can edit it with: notepad .env" -ForegroundColor Cyan
    exit 0
}

# Start services
Write-Host "🚀 Starting Easy Analytics services..." -ForegroundColor Cyan

try {
    docker-compose -f docker-compose.prod.yml up -d
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to start services. Check Docker Desktop is running."
    exit 1
}

# Wait for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Check service status
Write-Host "🔍 Checking service health..." -ForegroundColor Cyan
$containers = docker ps --format "table {{.Names}}\t{{.Status}}"
Write-Host $containers

Write-Host ""
Write-Host "🎉 Easy Analytics Setup Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Application URL: https://localhost" -ForegroundColor White
Write-Host "📊 Monitoring URL: http://localhost:9090" -ForegroundColor White
Write-Host "🔐 Note: You'll see SSL warnings (self-signed certificate)" -ForegroundColor Yellow
Write-Host ""
Write-Host "📁 Important Files:" -ForegroundColor Cyan
Write-Host "   - Environment: .env" -ForegroundColor White
Write-Host "   - Logs: logs/" -ForegroundColor White
Write-Host "   - Backups: backups/" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "   - View logs: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host "   - Restart: docker-compose -f docker-compose.prod.yml restart" -ForegroundColor White
Write-Host "   - Stop: docker-compose -f docker-compose.prod.yml down" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Next Steps:" -ForegroundColor Yellow
Write-Host "1. Access https://localhost and complete ToolJet setup" -ForegroundColor White
Write-Host "2. Import the Easy Analytics app from easy_analytics_app.json" -ForegroundColor White
Write-Host "3. Configure your analytics workflows" -ForegroundColor White
Write-Host ""
Write-Host "For production deployment on Linux/cloud, use ./setup-production.sh" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan 