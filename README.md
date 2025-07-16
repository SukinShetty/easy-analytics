# Easy Analytics

Enterprise-grade self-hosted analytics tool for Freshworks CRM using ToolJet.

🚀 **Production-Ready Self-Hosting** with SSL, monitoring, automated backups, and enterprise security.

## Quick Start (Production)

### Linux/Mac
```bash
# Clone and setup
git clone <your-repo>
cd easy-analytics

# Run production setup (interactive)
chmod +x setup-production.sh
./setup-production.sh
```

### Windows
```powershell
# Clone and setup
git clone <your-repo>
cd easy-analytics

# Run production setup (interactive)
.\setup-production.ps1
```

The setup script will:
- ✅ Generate secure passwords and SSL certificates
- ✅ Configure Nginx reverse proxy with HTTPS
- ✅ Set up PostgreSQL with automated backups
- ✅ Deploy monitoring stack (Prometheus)
- ✅ Configure log rotation and health checks

## Features

### 🔒 Security
- **SSL/TLS encryption** with Let's Encrypt auto-renewal
- **Rate limiting** and DDoS protection
- **Secure password generation** for all services
- **Environment isolation** with Docker networks

### 📊 Monitoring & Reliability
- **Prometheus monitoring** with health checks
- **Automated daily/weekly/monthly backups**
- **Log rotation** and centralized logging
- **Container health monitoring**

### 🚀 Performance
- **Nginx reverse proxy** with caching
- **Redis caching layer**
- **Optimized PostgreSQL** configuration
- **Gzip compression** enabled

### 💾 Backup Strategy
- **Daily backups** (retained 30 days)
- **Weekly backups** (retained 12 weeks)  
- **Monthly backups** (retained 12 months)
- **Backup verification** and notifications

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production Docker configuration |
| `nginx/nginx.conf` | Reverse proxy with SSL |
| `scripts/backup.sh` | Automated backup system |
| `scripts/ssl-setup.sh` | SSL certificate management |
| `env.template` | Environment configuration template |

## Management Commands

```bash
# View service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Manual backup
./scripts/backup.sh daily

# Check SSL certificate
./scripts/ssl-setup.sh check

# Renew SSL certificate
./scripts/ssl-setup.sh renew
```

## Monitoring

- **Application**: https://your-domain.com
- **Prometheus**: https://your-domain.com:9090
- **Health Check**: https://your-domain.com/health

## Development Setup

For development/testing with self-signed certificates:

```bash
# Use simple Docker Compose
docker-compose up -d

# Access at http://localhost:8080
```

## Troubleshooting

### SSL Issues
```bash
# Check certificate status
./scripts/ssl-setup.sh check

# Regenerate certificates
./scripts/ssl-setup.sh generate
```

### Database Issues
```bash
# Check database health
docker exec easy_analytics_db pg_isready -U postgres

# View database logs
docker logs easy_analytics_db
```

### Backup Issues
```bash
# Test backup manually
./scripts/backup.sh daily

# Check backup logs
tail -f logs/backup.log
```

## Environment Variables

Key environment variables (see `env.template`):

| Variable | Description | Required |
|----------|-------------|----------|
| `TOOLJET_HOST` | Your domain (https://...) | Yes |
| `PG_PASS` | Database password | Yes |
| `SECRET_KEY_BASE` | ToolJet secret key | Yes |
| `FRESHWORKS_DOMAIN` | Freshworks CRM domain | Yes |
| `FRESHWORKS_API_KEY` | Freshworks API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `SSL_EMAIL` | Email for SSL certificates | Yes |

## Security Best Practices

1. **Change default passwords** - All passwords are auto-generated
2. **Use strong API keys** - Keep API keys secure and rotate regularly
3. **Monitor access logs** - Check nginx logs for suspicious activity
4. **Update regularly** - Keep Docker images updated
5. **Backup encryption** - Consider encrypting backup files

## Scaling Considerations

For high-traffic deployments:

1. **Load Balancing**: Add multiple ToolJet instances
2. **Database Scaling**: Consider read replicas
3. **Cache Optimization**: Tune Redis configuration
4. **Resource Limits**: Adjust container resource limits

## Migration from Simple Setup

If upgrading from the basic setup:

```bash
# Backup existing data
docker exec <old_db_container> pg_dump -U postgres tooljet_prod > backup.sql

# Run production setup
./setup-production.sh

# Restore data
docker exec -i easy_analytics_db psql -U postgres tooljet_prod < backup.sql
```

## Support

- Check logs in `logs/` directory
- Review Docker container status
- Verify environment configuration
- Test network connectivity

## License

AGPL-3.0 (based on ToolJet) 