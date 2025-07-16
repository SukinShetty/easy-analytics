#!/bin/bash

# Easy Analytics Production Setup Script
# "At Any Cost" Self-Hosting Deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/setup.log"
ENV_FILE="$SCRIPT_DIR/.env"
BACKUP_ENV="$SCRIPT_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "$timestamp [$level] $message" | tee -a "$LOG_FILE"
    
    case "$level" in
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    log "INFO" "Check the log file for details: $LOG_FILE"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error_exit "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check OpenSSL
    if ! command -v openssl &> /dev/null; then
        error_exit "OpenSSL is not installed. Please install OpenSSL first."
    fi
    
    # Check available disk space (minimum 10GB)
    local available_space=$(df . | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    
    if [[ $available_gb -lt 10 ]]; then
        error_exit "Insufficient disk space: ${available_gb}GB available (minimum 10GB required)"
    fi
    
    log "SUCCESS" "Prerequisites check passed"
}

# Generate secure passwords and keys
generate_secrets() {
    log "INFO" "Generating secure secrets..."
    
    # Generate database password (32 characters)
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    # Generate Redis password (24 characters)
    REDIS_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
    
    # Generate ToolJet secrets
    SECRET_KEY_BASE=$(openssl rand -hex 32)
    LOCKBOX_MASTER_KEY=$(openssl rand -base64 32)
    
    # Generate Grafana admin password
    GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
    
    log "SUCCESS" "Secure secrets generated"
}

# Interactive configuration
interactive_config() {
    log "INFO" "Starting interactive configuration..."
    
    echo
    echo "=== Easy Analytics Production Setup ==="
    echo "This script will set up a production-grade self-hosted analytics platform."
    echo
    
    # Domain configuration
    while true; do
        read -p "Enter your domain name (e.g., analytics.example.com): " DOMAIN
        if [[ -n "$DOMAIN" && "$DOMAIN" != "localhost" ]]; then
            break
        fi
        echo "Please enter a valid domain name (not localhost)"
    done
    
    # Email for SSL certificates
    while true; do
        read -p "Enter email for SSL certificates: " SSL_EMAIL
        if [[ "$SSL_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            break
        fi
        echo "Please enter a valid email address"
    done
    
    # Freshworks configuration
    echo
    echo "--- Freshworks CRM Configuration ---"
    read -p "Freshworks domain (e.g., mycompany.freshworks.com): " FRESHWORKS_DOMAIN
    read -p "Freshworks API key: " FRESHWORKS_API_KEY
    
    # OpenAI configuration
    echo
    echo "--- OpenAI Configuration ---"
    read -p "OpenAI API key (sk-...): " OPENAI_API_KEY
    
    # Optional notification webhooks
    echo
    echo "--- Optional Notifications ---"
    read -p "Slack webhook URL (optional): " SLACK_WEBHOOK
    read -p "Backup notification webhook URL (optional): " BACKUP_WEBHOOK
    
    log "SUCCESS" "Interactive configuration completed"
}

# Create environment file
create_env_file() {
    log "INFO" "Creating environment configuration..."
    
    # Backup existing .env file
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$BACKUP_ENV"
        log "INFO" "Existing .env backed up to $BACKUP_ENV"
    fi
    
    # Create new .env file
    cat > "$ENV_FILE" << EOF
# Easy Analytics Production Configuration
# Generated on $(date)

# Core Application
TOOLJET_HOST=https://$DOMAIN
NODE_ENV=production

# Database Settings
PG_DB=tooljet_prod
PG_USER=postgres
PG_PASS=$DB_PASSWORD
PG_HOST=postgres
PG_PORT=5432

# ToolJet Database
TOOLJET_DB=tooljet_prod
TOOLJET_DB_USER=postgres
TOOLJET_DB_PASS=$DB_PASSWORD
TOOLJET_DB_HOST=postgres
TOOLJET_DB_PORT=5432

# Security Keys
SECRET_KEY_BASE=$SECRET_KEY_BASE
LOCKBOX_MASTER_KEY=$LOCKBOX_MASTER_KEY

# External APIs
FRESHWORKS_DOMAIN=$FRESHWORKS_DOMAIN
FRESHWORKS_API_KEY=$FRESHWORKS_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY

# Cache Settings
REDIS_PASSWORD=$REDIS_PASSWORD

# SSL Configuration
SSL_EMAIL=$SSL_EMAIL
SSL_DOMAIN=$DOMAIN
ACME_SERVER=https://acme-v02.api.letsencrypt.org/directory

# Notifications
SLACK_WEBHOOK_URL=$SLACK_WEBHOOK
BACKUP_WEBHOOK_URL=$BACKUP_WEBHOOK

# Monitoring
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD

EOF
    
    # Set secure permissions
    chmod 600 "$ENV_FILE"
    
    log "SUCCESS" "Environment file created: $ENV_FILE"
}

# Setup SSL certificates
setup_ssl() {
    log "INFO" "Setting up SSL certificates..."
    
    # Make SSL script executable
    chmod +x "$SCRIPT_DIR/scripts/ssl-setup.sh"
    
    # Generate certificates
    if ! "$SCRIPT_DIR/scripts/ssl-setup.sh" generate; then
        error_exit "Failed to generate SSL certificates"
    fi
    
    log "SUCCESS" "SSL certificates configured"
}

# Initialize database schema
init_database() {
    log "INFO" "Initializing database schema..."
    
    # Start just PostgreSQL first
    docker-compose -f docker-compose.prod.yml up -d postgres
    
    # Wait for database to be ready
    local timeout=60
    local count=0
    while ! docker exec easy_analytics_db pg_isready -U postgres > /dev/null 2>&1; do
        if [[ $count -ge $timeout ]]; then
            error_exit "Database failed to start within $timeout seconds"
        fi
        sleep 1
        ((count++))
    done
    
    log "SUCCESS" "Database initialized"
}

# Start services
start_services() {
    log "INFO" "Starting all services..."
    
    # Start all services
    if ! docker-compose -f docker-compose.prod.yml up -d; then
        error_exit "Failed to start services"
    fi
    
    # Wait for services to be healthy
    log "INFO" "Waiting for services to become healthy..."
    sleep 30
    
    # Check service health
    local unhealthy_services=$(docker-compose -f docker-compose.prod.yml ps --services --filter "health=unhealthy")
    if [[ -n "$unhealthy_services" ]]; then
        log "WARNING" "Some services are unhealthy: $unhealthy_services"
    fi
    
    log "SUCCESS" "Services started successfully"
}

# Setup monitoring and backups
setup_monitoring() {
    log "INFO" "Setting up monitoring and backups..."
    
    # Make backup script executable
    chmod +x "$SCRIPT_DIR/scripts/backup.sh"
    
    # Create initial backup
    if ! "$SCRIPT_DIR/scripts/backup.sh" daily; then
        log "WARNING" "Initial backup failed, but continuing setup"
    fi
    
    # Setup log rotation
    cat > "$SCRIPT_DIR/scripts/logrotate.conf" << 'EOF'
/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker kill -s USR1 $(docker ps -q --filter label=com.docker.compose.service=nginx) 2>/dev/null || true
    endscript
}
EOF
    
    log "SUCCESS" "Monitoring and backups configured"
}

# Display final information
show_completion_info() {
    local app_url="https://$DOMAIN"
    local monitoring_url="https://$DOMAIN:9090"
    
    echo
    echo "============================================="
    echo "🎉 Easy Analytics Production Setup Complete!"
    echo "============================================="
    echo
    echo "🌐 Application URL: $app_url"
    echo "📊 Monitoring URL: $monitoring_url"
    echo "🔐 Grafana Password: $GRAFANA_PASSWORD"
    echo
    echo "📁 Important Files:"
    echo "   - Environment: $ENV_FILE"
    echo "   - Logs: $LOG_FILE"
    echo "   - Backups: $SCRIPT_DIR/backups/"
    echo
    echo "🔧 Management Commands:"
    echo "   - View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   - Restart: docker-compose -f docker-compose.prod.yml restart"
    echo "   - Backup: ./scripts/backup.sh"
    echo "   - SSL renewal: ./scripts/ssl-setup.sh check"
    echo
    echo "⚠️  Next Steps:"
    echo "1. Access $app_url and complete ToolJet setup"
    echo "2. Import the Easy Analytics app from easy_analytics_app.json"
    echo "3. Test the backup system: ./scripts/backup.sh"
    echo "4. Set up monitoring alerts if needed"
    echo
    echo "📚 Documentation: See README.md for usage instructions"
    echo "============================================="
}

# Health check
health_check() {
    log "INFO" "Performing final health check..."
    
    local issues=0
    
    # Check if containers are running
    local expected_containers=("easy_analytics_nginx" "easy_analytics_app" "easy_analytics_db" "easy_analytics_cache")
    for container in "${expected_containers[@]}"; do
        if ! docker ps --format "table {{.Names}}" | grep -q "$container"; then
            log "ERROR" "Container $container is not running"
            ((issues++))
        fi
    done
    
    # Check if HTTPS is working
    if command -v curl &> /dev/null; then
        if ! curl -k -s "https://$DOMAIN/health" > /dev/null; then
            log "WARNING" "HTTPS health check failed (this might be normal during initial setup)"
        fi
    fi
    
    if [[ $issues -eq 0 ]]; then
        log "SUCCESS" "Health check passed"
        return 0
    else
        log "ERROR" "Health check found $issues issues"
        return 1
    fi
}

# Main setup function
main() {
    log "INFO" "Starting Easy Analytics production setup..."
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run setup steps
    check_prerequisites
    generate_secrets
    interactive_config
    create_env_file
    setup_ssl
    init_database
    start_services
    setup_monitoring
    
    # Final checks and information
    if health_check; then
        show_completion_info
        log "SUCCESS" "Easy Analytics production setup completed successfully!"
    else
        log "ERROR" "Setup completed with issues. Check the logs and container status."
        exit 1
    fi
}

# Handle script interruption
trap 'log "ERROR" "Setup interrupted by user"; exit 1' INT TERM

# Run main function
main "$@" 