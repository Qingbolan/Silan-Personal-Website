# Silan Deployment Guide

Complete guide for deploying and configuring the Silan Content Management System in different environments.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Production Configuration](#production-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Overview

The Silan system can be deployed in various environments, from local development to production servers. This guide covers all deployment scenarios and configuration options.

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Silan CLI     │    │   Database      │
│   (React/Next)  │◄──►│   Backend       │◄──►│   (PostgreSQL)  │
│                 │    │   (FastAPI)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │              ┌─────────────────┐              │
        └─────────────►│   File System   │◄─────────────┘
                       │   (Content)     │
                       └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Node.js 16+ (for frontend)
- PostgreSQL 12+ (for database)
- Git

### Quick Installation

```bash
# Clone the repository
git clone <repository-url>
cd silan-personal-website

# Install Python package
pip install -e .

# Verify installation
silan --version
```

### Development Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Docker Installation

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["silan", "backend", "start", "--host", "0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  silan-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SILAN_DB_HOST=postgres
      - SILAN_DB_PORT=5432
      - SILAN_DB_NAME=silan_db
    depends_on:
      - postgres
    volumes:
      - ./content:/app/content

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=silan_db
      - POSTGRES_USER=silan
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Environment Configuration

### Configuration Files

Create configuration files for different environments:

#### Development Configuration (`silan.dev.yaml`)

```yaml
environment: development

database:
  host: localhost
  port: 5432
  name: silan_dev
  user: silan_dev
  password: dev_password
  ssl_mode: disable

backend:
  host: localhost
  port: 8000
  debug: true
  auto_reload: true

content:
  base_path: ./content
  default_language: en
  supported_languages: ["en", "zh"]
  auto_sync: true
  watch_files: true

logging:
  level: DEBUG
  file: logs/silan-dev.log
  console: true

cache:
  enabled: false
  ttl: 300
```

#### Production Configuration (`silan.prod.yaml`)

```yaml
environment: production

database:
  host: ${SILAN_DB_HOST}
  port: ${SILAN_DB_PORT}
  name: ${SILAN_DB_NAME}
  user: ${SILAN_DB_USER}
  password: ${SILAN_DB_PASSWORD}
  ssl_mode: require
  pool_size: 20
  max_overflow: 30

backend:
  host: 0.0.0.0
  port: ${SILAN_BACKEND_PORT:8000}
  debug: false
  workers: 4
  timeout: 60

content:
  base_path: /app/content
  default_language: en
  supported_languages: ["en", "zh"]
  auto_sync: false
  validation_strict: true

logging:
  level: INFO
  file: /var/log/silan/silan.log
  format: json
  max_size: 100MB
  backup_count: 5

security:
  cors_origins: ["https://yourdomain.com"]
  api_key_required: true
  rate_limiting: true

cache:
  enabled: true
  backend: redis
  host: ${REDIS_HOST}
  port: ${REDIS_PORT}
  ttl: 3600
```

#### Testing Configuration (`silan.test.yaml`)

```yaml
environment: testing

database:
  host: localhost
  port: 5432
  name: silan_test
  user: silan_test
  password: test_password

content:
  base_path: ./tests/fixtures/content
  auto_sync: false

logging:
  level: WARNING
  console: false
```

### Environment Variables

```bash
# .env file
SILAN_ENV=production
SILAN_CONFIG_PATH=/app/config/silan.prod.yaml

# Database
SILAN_DB_HOST=db.example.com
SILAN_DB_PORT=5432
SILAN_DB_NAME=silan_prod
SILAN_DB_USER=silan_user
SILAN_DB_PASSWORD=secure_password

# Backend
SILAN_BACKEND_PORT=8000
SILAN_BACKEND_WORKERS=4

# Redis (for caching)
REDIS_HOST=redis.example.com
REDIS_PORT=6379

# Logging
SILAN_LOG_LEVEL=INFO
```

## Database Setup

### PostgreSQL Setup

#### Local Development

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (using Homebrew)
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database and user
sudo -u postgres psql
CREATE DATABASE silan_dev;
CREATE USER silan_dev WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE silan_dev TO silan_dev;
\q
```

#### Production Setup

```sql
-- Create production database
CREATE DATABASE silan_prod;
CREATE USER silan_prod WITH PASSWORD 'secure_production_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE silan_prod TO silan_prod;

-- Configure connection limits and security
ALTER USER silan_prod SET default_transaction_isolation TO 'read committed';
ALTER USER silan_prod SET timezone TO 'UTC';
```

### Database Migration

```bash
# Initialize database schema
silan db-config --set host localhost --set port 5432
silan db-sync --initialize

# Test connection
silan db-config --test-connection

# Run migrations
silan db-migrate --up
```

### Database Backup

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups/silan"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h $SILAN_DB_HOST -U $SILAN_DB_USER $SILAN_DB_NAME > "$BACKUP_DIR/silan_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/silan_backup_$DATE.sql"

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

## Backend Deployment

### Systemd Service (Linux)

Create a systemd service file:

```ini
# /etc/systemd/system/silan-backend.service
[Unit]
Description=Silan Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=silan
Group=silan
WorkingDirectory=/app/silan
Environment=SILAN_CONFIG_PATH=/app/silan/silan.prod.yaml
ExecStart=/app/silan/venv/bin/silan backend start --daemon=false
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=silan-backend

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable silan-backend
sudo systemctl start silan-backend

# Check status
sudo systemctl status silan-backend

# View logs
journalctl -u silan-backend -f
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/silan
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend (if serving static files)
    location / {
        root /var/www/silan-frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Content files
    location /content/ {
        alias /app/silan/content/;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker Deployment

```bash
# Build and deploy with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs silan-backend

# Scale backend
docker-compose up -d --scale silan-backend=3
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: silan-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: silan-backend
  template:
    metadata:
      labels:
        app: silan-backend
    spec:
      containers:
      - name: silan-backend
        image: silan-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SILAN_CONFIG_PATH
          value: "/config/silan.prod.yaml"
        - name: SILAN_DB_HOST
          valueFrom:
            secretKeyRef:
              name: silan-secrets
              key: db-host
        volumeMounts:
        - name: config
          mountPath: /config
        - name: content
          mountPath: /app/content
      volumes:
      - name: config
        configMap:
          name: silan-config
      - name: content
        persistentVolumeClaim:
          claimName: silan-content-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: silan-backend-service
spec:
  selector:
    app: silan-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Production Configuration

### Performance Optimization

```yaml
# Production optimizations
backend:
  workers: 4  # CPU cores × 2
  worker_class: uvicorn.workers.UvicornWorker
  timeout: 60
  keepalive: 2
  max_requests: 1000
  max_requests_jitter: 100

database:
  pool_size: 20
  max_overflow: 30
  pool_recycle: 3600
  pool_timeout: 30

cache:
  enabled: true
  backend: redis
  ttl: 3600
  max_size: "1GB"
```

### Security Configuration

```yaml
security:
  # CORS settings
  cors_origins:
    - "https://yourdomain.com"
    - "https://www.yourdomain.com"

  # API security
  api_key_required: true
  rate_limiting:
    enabled: true
    per_minute: 100
    per_hour: 1000

  # File upload limits
  max_file_size: "10MB"
  allowed_extensions: [".md", ".yaml", ".json", ".jpg", ".png"]

  # Database security
  db_ssl_required: true
  db_query_timeout: 30
```

### Monitoring Configuration

```yaml
monitoring:
  metrics:
    enabled: true
    port: 9090
    path: /metrics

  health_check:
    enabled: true
    path: /health
    interval: 30

  logging:
    structured: true
    format: json
    fields:
      - timestamp
      - level
      - message
      - request_id
      - user_id
```

## Monitoring and Maintenance

### Health Checks

```python
# Health check endpoint
from silan.utils.health_check import HealthChecker

health_checker = HealthChecker()

@app.get("/health")
async def health_check():
    return health_checker.get_health_status()

# Returns:
# {
#   "status": "healthy",
#   "timestamp": "2024-12-21T10:00:00Z",
#   "checks": {
#     "database": "healthy",
#     "file_system": "healthy",
#     "cache": "healthy"
#   },
#   "version": "1.0.0"
# }
```

### Monitoring Scripts

```bash
#!/bin/bash
# monitoring.sh - Basic monitoring script

# Check service status
if ! systemctl is-active --quiet silan-backend; then
    echo "ALERT: Silan backend is not running"
    systemctl restart silan-backend
fi

# Check database connection
if ! silan db-config --test-connection > /dev/null 2>&1; then
    echo "ALERT: Database connection failed"
fi

# Check disk space
USAGE=$(df /app | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt 85 ]; then
    echo "ALERT: Disk usage is at ${USAGE}%"
fi

# Check log file size
LOG_SIZE=$(stat -c%s /var/log/silan/silan.log)
if [ $LOG_SIZE -gt 1073741824 ]; then  # 1GB
    echo "ALERT: Log file is larger than 1GB"
fi
```

### Backup Scripts

```bash
#!/bin/bash
# backup.sh - Complete backup script

BACKUP_DIR="/backups/silan/$(date +%Y/%m/%d)"
mkdir -p $BACKUP_DIR

# Database backup
echo "Backing up database..."
pg_dump -h $SILAN_DB_HOST -U $SILAN_DB_USER $SILAN_DB_NAME | gzip > "$BACKUP_DIR/database.sql.gz"

# Content backup
echo "Backing up content files..."
tar -czf "$BACKUP_DIR/content.tar.gz" /app/silan/content/

# Configuration backup
echo "Backing up configuration..."
cp /app/silan/silan.prod.yaml "$BACKUP_DIR/"

# Upload to cloud storage (optional)
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/silan/

echo "Backup completed: $BACKUP_DIR"
```

### Log Rotation

```bash
# /etc/logrotate.d/silan
/var/log/silan/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 silan silan
    postrotate
        systemctl reload silan-backend
    endscript
}
```

## Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check configuration
silan validate-config --strict

# Check database connection
silan db-config --test-connection

# Check logs
journalctl -u silan-backend -n 50

# Check file permissions
ls -la /app/silan/
```

#### Database Connection Issues

```bash
# Test connection manually
psql -h $SILAN_DB_HOST -U $SILAN_DB_USER -d $SILAN_DB_NAME

# Check firewall
sudo ufw status
sudo iptables -L

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-13-main.log
```

#### Content Not Loading

```bash
# Validate content structure
silan validate-config
silan check-files

# Resync content
silan db-sync --force

# Check file permissions
find /app/silan/content -name "*.md" -exec ls -la {} \;
```

#### Performance Issues

```bash
# Check resource usage
htop
iostat -x 1
free -h

# Check database performance
psql -d $SILAN_DB_NAME -c "SELECT * FROM pg_stat_activity;"

# Analyze slow queries
tail -f /var/log/postgresql/postgresql.log | grep "slow query"
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug environment
export SILAN_DEBUG=1
export SILAN_LOG_LEVEL=DEBUG

# Start with debug logging
silan backend start --debug --verbose

# Run with profiling
python -m cProfile -o profile.out silan backend start
```

### Recovery Procedures

#### Database Recovery

```bash
# Restore from backup
gunzip < /backups/silan/database.sql.gz | psql -h $SILAN_DB_HOST -U $SILAN_DB_USER -d $SILAN_DB_NAME

# Reset and resync
silan db-sync --reset --force
```

#### Content Recovery

```bash
# Restore content files
cd /app/silan
tar -xzf /backups/silan/content.tar.gz

# Validate and resync
silan validate-config --fix
silan db-sync --force
```

---

**Last Updated**: 2025-09-21
**Version**: 1.0.0