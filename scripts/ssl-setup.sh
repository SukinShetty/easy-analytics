#!/bin/bash

# SSL Certificate Management for Easy Analytics
# Supports Let's Encrypt with automatic renewal

set -euo pipefail

# Configuration
NGINX_DIR="./nginx"
SSL_DIR="$NGINX_DIR/ssl"
DOMAIN="${SSL_DOMAIN:-localhost}"
EMAIL="${SSL_EMAIL:-admin@localhost}"
ACME_SERVER="${ACME_SERVER:-https://acme-v02.api.letsencrypt.org/directory}"
LOG_FILE="./logs/ssl.log"

# Create directories
mkdir -p "$SSL_DIR" "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if running on localhost/development
is_development() {
    [[ "$DOMAIN" == "localhost" || "$DOMAIN" == "127.0.0.1" || "$DOMAIN" == *.local ]]
}

# Generate self-signed certificate for development
generate_self_signed() {
    log "Generating self-signed certificate for development ($DOMAIN)..."
    
    # Create private key
    openssl genrsa -out "$SSL_DIR/privkey.pem" 2048
    
    # Create certificate signing request
    openssl req -new -key "$SSL_DIR/privkey.pem" -out "$SSL_DIR/cert.csr" -subj "/C=US/ST=Development/L=Development/O=Easy Analytics/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -in "$SSL_DIR/cert.csr" -signkey "$SSL_DIR/privkey.pem" -out "$SSL_DIR/fullchain.pem" -days 365 \
        -extensions v3_req -extfile <(
            echo '[v3_req]'
            echo 'keyUsage = keyEncipherment, dataEncipherment'
            echo 'extendedKeyUsage = serverAuth'
            echo "subjectAltName = DNS:$DOMAIN,DNS:*.localhost,IP:127.0.0.1"
        )
    
    # Clean up CSR
    rm -f "$SSL_DIR/cert.csr"
    
    # Set proper permissions
    chmod 600 "$SSL_DIR/privkey.pem"
    chmod 644 "$SSL_DIR/fullchain.pem"
    
    log "Self-signed certificate generated successfully"
    log "⚠️  WARNING: This is a self-signed certificate. Browsers will show security warnings."
    log "   For production, use a real domain and Let's Encrypt certificates."
}

# Check if certbot is available
check_certbot() {
    if ! command -v certbot &> /dev/null; then
        log "Installing certbot..."
        
        # Try different package managers
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        elif command -v brew &> /dev/null; then
            brew install certbot
        else
            error_exit "Could not install certbot. Please install it manually."
        fi
    fi
}

# Validate domain and prerequisites for Let's Encrypt
validate_letsencrypt_prereqs() {
    log "Validating Let's Encrypt prerequisites..."
    
    # Check if domain is accessible
    if ! dig +short "$DOMAIN" > /dev/null; then
        error_exit "Domain $DOMAIN is not resolvable. Make sure DNS is configured correctly."
    fi
    
    # Check if port 80 is accessible (required for Let's Encrypt validation)
    if ! nc -z "$DOMAIN" 80 2>/dev/null; then
        log "WARNING: Port 80 may not be accessible. Let's Encrypt validation might fail."
    fi
    
    # Validate email format
    if [[ ! "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        error_exit "Invalid email format: $EMAIL"
    fi
    
    log "Prerequisites validation passed"
}

# Generate Let's Encrypt certificate
generate_letsencrypt() {
    log "Generating Let's Encrypt certificate for $DOMAIN..."
    
    validate_letsencrypt_prereqs
    check_certbot
    
    # Stop nginx if running (certbot needs port 80)
    if docker ps | grep -q easy_analytics_nginx; then
        log "Stopping nginx for certificate generation..."
        docker stop easy_analytics_nginx || true
    fi
    
    # Generate certificate
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --server "$ACME_SERVER" \
        --cert-path "$SSL_DIR/fullchain.pem" \
        --key-path "$SSL_DIR/privkey.pem" || error_exit "Failed to generate Let's Encrypt certificate"
    
    # Copy certificates to our SSL directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/"
    
    # Set proper ownership and permissions
    sudo chown "$(id -u):$(id -g)" "$SSL_DIR/fullchain.pem" "$SSL_DIR/privkey.pem"
    chmod 644 "$SSL_DIR/fullchain.pem"
    chmod 600 "$SSL_DIR/privkey.pem"
    
    log "Let's Encrypt certificate generated successfully"
}

# Setup automatic renewal
setup_renewal() {
    if is_development; then
        log "Skipping renewal setup for development environment"
        return
    fi
    
    log "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > "./scripts/renew-ssl.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

LOG_FILE="./logs/ssl-renewal.log"
DOMAIN="${SSL_DOMAIN}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting certificate renewal check for $DOMAIN..."

# Try to renew certificate
if certbot renew --quiet --deploy-hook "docker restart easy_analytics_nginx"; then
    log "Certificate renewal completed successfully"
    
    # Copy renewed certificates
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "./nginx/ssl/"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "./nginx/ssl/"
    
    # Set permissions
    chmod 644 "./nginx/ssl/fullchain.pem"
    chmod 600 "./nginx/ssl/privkey.pem"
    
    log "Certificates updated and nginx restarted"
else
    log "No renewal needed or renewal failed"
fi
EOF
    
    chmod +x "./scripts/renew-ssl.sh"
    
    # Add to crontab (run twice daily as recommended by Let's Encrypt)
    (crontab -l 2>/dev/null; echo "0 */12 * * * cd $(pwd) && ./scripts/renew-ssl.sh") | crontab -
    
    log "Automatic renewal configured (runs twice daily)"
}

# Check certificate expiry
check_certificate() {
    if [[ ! -f "$SSL_DIR/fullchain.pem" ]]; then
        log "No certificate found"
        return 1
    fi
    
    local expiry_date=$(openssl x509 -enddate -noout -in "$SSL_DIR/fullchain.pem" | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    log "Certificate expires in $days_until_expiry days ($expiry_date)"
    
    if [[ $days_until_expiry -lt 30 ]]; then
        log "⚠️  WARNING: Certificate expires in less than 30 days!"
        return 1
    fi
    
    return 0
}

# Main function
main() {
    local action="${1:-generate}"
    
    log "=== SSL Certificate Management ==="
    log "Domain: $DOMAIN"
    log "Email: $EMAIL"
    log "Action: $action"
    
    case "$action" in
        "generate")
            if is_development; then
                generate_self_signed
            else
                generate_letsencrypt
                setup_renewal
            fi
            ;;
        "renew")
            if is_development; then
                log "Skipping renewal for development environment"
            else
                generate_letsencrypt
            fi
            ;;
        "check")
            check_certificate
            ;;
        "setup-renewal")
            setup_renewal
            ;;
        *)
            echo "Usage: $0 [generate|renew|check|setup-renewal]"
            echo "  generate      - Generate new certificate"
            echo "  renew         - Renew existing certificate"
            echo "  check         - Check certificate expiry"
            echo "  setup-renewal - Setup automatic renewal"
            exit 1
            ;;
    esac
    
    log "=== SSL Certificate Management Completed ==="
}

# Run main function
main "$@" 