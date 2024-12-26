# Configuration Reference

This document lists all configurable values that need to be set when deploying the encoder manager system.

## Network Configuration

### IP Addresses & Ports
- Default Network Prefix: `x.x.183.*` → Replace with your network (e.g., `192.168.*`)
  Path: `app/services/encoder_manager.py`
- API Server: Default `http://your-server` → Replace with your domain
  Path: `app/config.py`
- Database Host: Default `localhost` → Replace with your PostgreSQL server
  Path: `app/config.py`
- Prometheus Port: Default `9090`
  Path: `app/monitoring/prometheus/prometheus.yml`
- Grafana Port: Default `3000`
  Path: `app/monitoring/grafana/encoder_dashboard.json`
- Redis Port: Default `6379`
  Path: `app/config.py`
- API Port: Default `5000`
  Path: `app/api/restAPIServer.py`
- Load Balancer Port: Default `8080`
  Path: `app/services/load_balancer.py`
- WebSocket Port: Default `8765`
  Path: `app/services/socketio_service.py`

## Security

### SSL/TLS Certificates
- Certificate Path: `/etc/letsencrypt/live/your-domain/fullchain.pem`
  Path: `app/core/security/nginx/nginx.conf`
- Private Key Path: `/etc/letsencrypt/live/your-domain/privkey.pem`
  Path: `app/core/security/nginx/nginx.conf`
- Certificate Renewal: Auto-renewal via Certbot (90 days)
  Path: `app/core/security/ssl_config.py`
- Minimum TLS Version: 1.2
  Path: `app/core/security/ssl_config.py`

### Authentication
- JWT Secret Key: Must be set in `JWT_SECRET_KEY` environment variable
  Path: `app/config.py`
- Token Expiration: Default `24h` (configurable)
  Path: `app/config.py`
- API Key Length: Minimum 32 characters
  Path: `app/core/security/api_key.py`
- Rate Limiting: Default `100/minute` per IP
  Path: `app/api/restAPIServer.py`

## Database Configuration

### PostgreSQL
- Database Name: Default `encoder_manager`
  Path: `migrations/versions/001_initial.py`
- Username: Must be set in `POSTGRES_USER` environment variable
  Path: `app/config.py`
- Password: Must be set in `POSTGRES_PASSWORD` environment variable
  Path: `app/config.py`
- Port: Default `5432`
  Path: `app/config.py`
- Max Connections: Default `100`
  Path: `app/installer/bootstrap.py`
- SSL Mode: Required for production
  Path: `app/config.py`

### Redis Cache
- Host: Default `localhost`
  Path: `app/config.py`
- Password: Must be set in `REDIS_PASSWORD` environment variable
  Path: `app/config.py`
- Database Number: Default `0`
  Path: `app/config.py`
- Cache TTL: Default `300` seconds
  Path: `app/services/performance_monitor.py`
- Max Memory: `512MB`
  Path: `app/installer/bootstrap.py`

## Monitoring & Logging

### Prometheus Metrics
- Scrape Interval: Default `15s`
  Path: `app/monitoring/prometheus/prometheus.yml`
- Retention Period: Default `15d`
  Path: `app/monitoring/prometheus/prometheus.yml`
- Target Labels: Required for service discovery
  Path: `app/monitoring/prometheus/prometheus.yml`
- Alert Manager Port: Default `9093`
  Path: `app/monitoring/prometheus/prometheus.yml`

### Grafana
- Admin Password: Must be set during initial setup
  Path: `app/installer/bootstrap.py`
- Default Organization: `encoder_manager`
  Path: `app/monitoring/grafana/encoder_dashboard.json`
- Dashboard Auto-Provisioning: `/etc/grafana/provisioning/dashboards`
  Path: `app/monitoring/grafana/encoder_dashboard.json`
- Data Source Auto-Provisioning: `/etc/grafana/provisioning/datasources`
  Path: `app/monitoring/grafana/encoder_dashboard.json`

### Logging
- Log Level: Default `INFO` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  Path: `app/config.py`
- Log Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  Path: `app/config.py`
- Log Path: `/var/log/encoder_manager/`
  Path: `app/installer/bootstrap.py`
- Rotation: Daily rotation, 30 days retention
  Path: `app/installer/bootstrap.py`

## Performance Tuning

### API Server
- Workers: Default `4` (2x CPU cores recommended)
  Path: `app/services/performance_monitor.py`
- Thread Pool: Default `8`
  Path: `app/services/performance_monitor.py`
- Request Timeout: Default `30s`
  Path: `app/api/restAPIServer.py`
- Max Request Size: Default `100MB`
  Path: `app/api/restAPIServer.py`

### Load Balancer
- Connection Pool Size: Default `20`
  Path: `app/services/load_balancer.py`
- Keep-Alive: Default `75s`
  Path: `app/services/load_balancer.py`
- Client Timeout: Default `60s`
  Path: `app/services/load_balancer.py`
- Retry Attempts: Default `3`
  Path: `app/services/load_balancer.py`

### Caching
- Response Cache Duration: Default `300s`
  Path: `app/services/performance_monitor.py`
- Cache Size Limit: Default `1GB`
  Path: `app/installer/bootstrap.py`
- Cache Strategy: `LRU`
  Path: `app/services/performance_monitor.py`
- Cached Endpoints: Configurable via decorator
  Path: `app/api/restAPIServer.py`

## Docker Configuration

### Resource Limits
- CPU Limit: Default `2 cores`
  Path: `create_installer.py`
- Memory Limit: Default `2GB`
  Path: `create_installer.py`
- Swap Limit: Default `512MB`
  Path: `create_installer.py`
- Storage Driver: `overlay2`
  Path: `create_installer.py`

### Networking
- Network Mode: `bridge`
  Path: `create_installer.py`
- DNS Servers: Configurable
  Path: `create_installer.py`
- Subnet Mask: `/24`
  Path: `create_installer.py`
- MTU: Default `1500`
  Path: `create_installer.py`

## Environment Variables

### Required Variables
- `POSTGRES_USER`
  Path: `app/config.py`
- `POSTGRES_PASSWORD`
  Path: `app/config.py`
- `REDIS_PASSWORD`
  Path: `app/config.py`
- `JWT_SECRET_KEY`
  Path: `app/config.py`
- `API_KEY`
  Path: `app/config.py`
- `ENVIRONMENT` (development/staging/production)
  Path: `app/config.py`

### Optional Variables
- `LOG_LEVEL`
  Path: `app/config.py`
- `WORKER_COUNT`
  Path: `app/config.py`
- `CACHE_TTL`
  Path: `app/config.py`
- `RATE_LIMIT_PER_MINUTE`
  Path: `app/config.py`
- `DATABASE_POOL_SIZE`
  Path: `app/config.py`

## Backup Configuration

### Database Backups
- Schedule: Daily at 00:00 UTC
  Path: `app/installer/bootstrap.py`
- Retention: 7 days
  Path: `app/installer/bootstrap.py`
- Backup Path: `/var/backups/encoder_manager/`
  Path: `app/installer/bootstrap.py`
- Compression: gzip
  Path: `app/installer/bootstrap.py`

### Application State
- Config Backup Path: `/etc/encoder_manager/backup/`
  Path: `app/installer/bootstrap.py`
- State Files Location: `/var/lib/encoder_manager/`
  Path: `app/installer/bootstrap.py`
- Backup Frequency: Daily
  Path: `app/installer/bootstrap.py`

## SSL Configuration

### Certificate Paths
- SSL Certificate: `/etc/letsencrypt/live/your-domain/fullchain.pem`
  Path: `app/core/security/nginx/nginx.conf`
- Private Key: `/etc/letsencrypt/live/your-domain/privkey.pem`
  Path: `app/core/security/nginx/nginx.conf`
- Chain Certificate: `/etc/letsencrypt/live/your-domain/chain.pem`
  Path: `app/core/security/nginx/nginx.conf`

### SSL Protocol Settings
- Minimum TLS Version: TLSv1.2
  Path: `app/core/security/nginx/nginx.conf`
- Preferred Ciphers:   ```
  ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384  ```
  Path: `app/core/security/nginx/nginx.conf`
- Certificate Pinning: Enabled with backup pins
  Path: `app/core/security/ssl_config.py`
- Certificate Monitoring: Check expiry every 24h
  Path: `app/monitoring/cert_monitor.py`
- Security Event Logging: Enabled for all SSL events
  Path: `app/core/security/security_logger.py`

### SSL Session Settings
- Session Timeout: 1d
  Path: `app/core/security/nginx/nginx.conf`
- Session Cache: shared:SSL:50m
  Path: `app/core/security/nginx/nginx.conf`
- Session Tickets: Disabled
  Path: `app/core/security/nginx/nginx.conf`

### Security Headers
- HSTS Max Age: 63072000 seconds (2 years)
  Path: `app/core/security/nginx/nginx.conf`
- OCSP Stapling: Enabled
  Path: `app/core/security/nginx/nginx.conf`
- DNS Resolvers: 8.8.8.8, 8.8.4.4
  Path: `app/core/security/nginx/nginx.conf`

### Certificate Management
- Auto-renewal: Yes (via Certbot)
  Path: `app/installer/bootstrap.py`
- Renewal Frequency: Every 60 days
  Path: `app/installer/bootstrap.py`
- Pre-renewal Hook: `/etc/letsencrypt/renewal-hooks/pre/`
  Path: `app/installer/bootstrap.py`
- Post-renewal Hook: `/etc/letsencrypt/renewal-hooks/post/`
  Path: `app/installer/bootstrap.py`