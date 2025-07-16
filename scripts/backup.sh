#!/bin/bash

# Production Database Backup Script for Easy Analytics
# Supports multiple backup strategies with retention policies

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
LOG_FILE="/var/log/backup.log"
RETENTION_DAYS=30
RETENTION_WEEKS=12
RETENTION_MONTHS=12
MAX_BACKUP_SIZE="10G"

# Database configuration from environment
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_NAME="${POSTGRES_DB:-tooljet_prod}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASS="${PGPASSWORD}"

# Notification settings (optional)
WEBHOOK_URL="${BACKUP_WEBHOOK_URL:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"/{daily,weekly,monthly}

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    send_notification "❌ Backup Failed" "$1" "error"
    exit 1
}

# Success notification
send_notification() {
    local title="$1"
    local message="$2"
    local level="${3:-info}"
    
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"title\":\"$title\",\"message\":\"$message\",\"level\":\"$level\"}" \
            || log "Warning: Failed to send webhook notification"
    fi
    
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        local emoji="✅"
        [[ "$level" == "error" ]] && emoji="❌"
        [[ "$level" == "warning" ]] && emoji="⚠️"
        
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$emoji $title: $message\"}" \
            || log "Warning: Failed to send Slack notification"
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    if ! pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
        error_exit "Cannot connect to database $DB_NAME on $DB_HOST"
    fi
    log "Database connectivity verified"
}

# Get database size
get_db_size() {
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs
}

# Create database backup
create_backup() {
    local backup_type="$1"
    local backup_dir="$BACKUP_DIR/$backup_type"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$backup_dir/backup_${backup_type}_${timestamp}.sql.gz"
    
    log "Starting $backup_type backup..."
    log "Database size: $(get_db_size)"
    
    # Create compressed backup
    if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --no-owner --no-privileges \
        --exclude-table-data='audit_logs' \
        | gzip > "$backup_file"; then
        
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "$backup_type backup completed: $backup_file ($backup_size)"
        
        # Verify backup integrity
        if verify_backup "$backup_file"; then
            log "Backup verification successful"
            
            # Create metadata file
            cat > "$backup_file.meta" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "type": "$backup_type",
    "database": "$DB_NAME",
    "size": "$backup_size",
    "file": "$(basename "$backup_file")",
    "verified": true,
    "db_version": "$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c 'SELECT version();' | head -1 | xargs)"
}
EOF
            
            send_notification "✅ Backup Completed" "$backup_type backup: $backup_size" "info"
        else
            rm -f "$backup_file"
            error_exit "Backup verification failed for $backup_file"
        fi
    else
        error_exit "Failed to create $backup_type backup"
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    log "Verifying backup: $(basename "$backup_file")"
    
    # Check if file is readable and not corrupted
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log "ERROR: Backup file is corrupted or not a valid gzip file"
        return 1
    fi
    
    # Check if SQL content is valid (basic check)
    if ! zcat "$backup_file" | head -100 | grep -q "PostgreSQL database dump"; then
        log "ERROR: Backup file doesn't appear to be a valid PostgreSQL dump"
        return 1
    fi
    
    return 0
}

# Clean old backups based on retention policy
cleanup_backups() {
    log "Starting backup cleanup..."
    
    # Daily backups: keep for $RETENTION_DAYS days
    find "$BACKUP_DIR/daily" -name "backup_daily_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/daily" -name "backup_daily_*.sql.gz.meta" -mtime +$RETENTION_DAYS -delete
    
    # Weekly backups: keep for $RETENTION_WEEKS weeks
    find "$BACKUP_DIR/weekly" -name "backup_weekly_*.sql.gz" -mtime +$((RETENTION_WEEKS * 7)) -delete
    find "$BACKUP_DIR/weekly" -name "backup_weekly_*.sql.gz.meta" -mtime +$((RETENTION_WEEKS * 7)) -delete
    
    # Monthly backups: keep for $RETENTION_MONTHS months
    find "$BACKUP_DIR/monthly" -name "backup_monthly_*.sql.gz" -mtime +$((RETENTION_MONTHS * 30)) -delete
    find "$BACKUP_DIR/monthly" -name "backup_monthly_*.sql.gz.meta" -mtime +$((RETENTION_MONTHS * 30)) -delete
    
    log "Backup cleanup completed"
}

# Check available disk space
check_disk_space() {
    local available=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    local available_gb=$((available / 1024 / 1024))
    
    if [[ $available_gb -lt 5 ]]; then
        error_exit "Insufficient disk space: ${available_gb}GB available (minimum 5GB required)"
    fi
    
    log "Available disk space: ${available_gb}GB"
}

# Main backup function
main() {
    local backup_type="${1:-daily}"
    
    log "=== Starting Easy Analytics Backup ($backup_type) ==="
    
    # Pre-flight checks
    check_database
    check_disk_space
    
    # Create backup
    create_backup "$backup_type"
    
    # Cleanup old backups
    cleanup_backups
    
    # Summary
    local total_backups=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    
    log "=== Backup Summary ==="
    log "Total backups: $total_backups"
    log "Total backup size: $total_size"
    log "=== Backup Completed Successfully ==="
    
    send_notification "📊 Backup Summary" "Total: $total_backups backups, Size: $total_size" "info"
}

# Determine backup type based on day/time
if [[ "${1:-auto}" == "auto" ]]; then
    DOW=$(date +%u)  # Day of week (1=Monday, 7=Sunday)
    DOM=$(date +%d)  # Day of month
    
    if [[ "$DOM" == "01" ]]; then
        BACKUP_TYPE="monthly"
    elif [[ "$DOW" == "7" ]]; then
        BACKUP_TYPE="weekly"
    else
        BACKUP_TYPE="daily"
    fi
else
    BACKUP_TYPE="$1"
fi

# Run backup
main "$BACKUP_TYPE" 