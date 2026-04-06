# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Git repository set up
- SSL certificates (for HTTPS)
- Domain name (optional)
- Email SMTP credentials
- GitHub secrets configured

## Pre-Deployment Checklist

### 1. Environment Configuration
```bash
# Copy production environment template
cp .env.prod.example .env

# Edit and set production values
nano .env
```

Required environment variables:
- `SECRET_KEY`: Strong random string (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG=False`
- `ALLOWED_HOSTS`: Your domain(s)
- `DB_PASSWORD`: Strong database password
- `GRAFANA_PASSWORD`: Strong Grafana admin password
- `EMAIL_*`: SMTP credentials
- `DB_ENGINE=postgres` (for production)

### 2. Security Verification
```bash
# Check Django security settings
python manage.py check --deploy

# Verify no debug mode
grep "DEBUG = True" config/settings.py  # Should return nothing

# Check for hardcoded secrets
grep -r "SECRET_KEY\|PASSWORD\|TOKEN" --include="*.py" . --exclude-dir=venv
```

### 3. Database Preparation
```bash
# Create PostgreSQL user and database
sudo -u postgres psql

CREATE USER attendance_user WITH PASSWORD 'strong_password';
CREATE DATABASE attendance_db OWNER attendance_user;
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
```

### 4. SSL Certificates
```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

## Deployment Steps

### Option 1: Docker Compose Deployment (Recommended)

#### 1. Build and Start Services
```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py createsuperuser
```

#### 2. Verify Deployment
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Health check
curl http://localhost/health/
```

#### 3. Configure Services

**Prometheus Setup:**
```bash
# Access Prometheus at http://localhost:9090
# Verify targets are being scraped
# Navigate to: Status > Targets
```

**Grafana Setup:**
1. Access http://localhost:3000
2. Login with admin/admin (or your set password)
3. Change admin password
4. Add Prometheus data source
   - URL: http://prometheus:9090
5. Import dashboards or create custom ones

### Option 2: Manual Server Deployment

#### 1. Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python, PostgreSQL, Redis
sudo apt-get install -y python3 python3-pip postgresql postgresql-contrib redis-server nginx

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Configure PostgreSQL
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Set up database
sudo -u postgres createuser attendance_user
sudo -u postgres createdb -O attendance_user attendance_db
```

#### 3. Configure Redis
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis
redis-cli ping  # Should return PONG
```

#### 4. Setup Django Application
```bash
# Create application directory
sudo mkdir -p /var/www/attendance-app
sudo chown $USER:$USER /var/www/attendance-app

# Clone repository
cd /var/www/attendance-app
git clone <repo-url> .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.prod.example .env
nano .env

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

#### 5. Configure Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service file
sudo nano /etc/systemd/system/attendance-app.service
```

```ini
[Unit]
Description=Attendance App Gunicorn Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=your_username
WorkingDirectory=/var/www/attendance-app
Environment="PATH=/var/www/attendance-app/venv/bin"
ExecStart=/var/www/attendance-app/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind unix:/var/www/attendance-app/attendance.sock \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    config.asgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable attendance-app
sudo systemctl start attendance-app

# Verify
sudo systemctl status attendance-app
```

#### 6. Configure Nginx
```bash
# Copy nginx configuration
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Enable and start
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl reload nginx
```

#### 7. Setup Celery Worker
```bash
# Create Celery systemd service
sudo nano /etc/systemd/system/celery-worker.service
```

```ini
[Unit]
Description=Celery Worker Service
After=network.target redis.service

[Service]
Type=forking
User=your_username
WorkingDirectory=/var/www/attendance-app
Environment="PATH=/var/www/attendance-app/venv/bin"
ExecStart=/var/www/attendance-app/venv/bin/celery -A config worker \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/celery
sudo chown $USER:$USER /var/log/celery

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
```

#### 8. Setup Monitoring
```bash
# Install Prometheus
# (Follow Prometheus documentation for your system)

# Install Grafana
# (Follow Grafana documentation for your system)

# Configure to scrape: http://localhost:8000/metrics/
```

## Post-Deployment Verification

### 1. Application Health
```bash
# Check application is running
curl http://yourdomain.com/health/

# Test API endpoint
curl -X POST http://yourdomain.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test123!"}'
```

### 2. Database
```bash
# Connect to database
psql -h localhost -U attendance_user -d attendance_db

# Verify tables exist
\dt

# Check data
SELECT COUNT(*) FROM users_customuser;
```

### 3. Cache
```bash
# Test Redis connection
redis-cli ping  # Should return PONG

# Check cache
redis-cli GET "django.core.cache.default:*"
```

### 4. Monitoring
```bash
# Prometheus targets
curl http://localhost:9090/api/v1/targets

# Grafana dashboards
# Access http://localhost:3000
```

## Scaling Configuration

### Load Balancing
```nginx
upstream django {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
    }
}
```

### Database Read Replicas
```bash
# In PostgreSQL streaming replication setup
# Configure DATABASES['replica'] in settings.py
DATABASES = {
    'default': {...},
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'replica.example.com',
        ...
    }
}
```

### Redis Cluster
```python
# In settings.py for Redis Cluster
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis-node-1:6379',
            'redis-node-2:6379',
            'redis-node-3:6379',
        ],
    }
}
```

## Backup & Recovery

### Database Backup
```bash
# Daily backup
sudo -u postgres pg_dump attendance_db > backup_$(date +%Y%m%d).sql

# Or using docker-compose
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U attendance_user attendance_db > backup.sql

# Restore from backup
docker-compose -f docker-compose.prod.yml exec db \
  psql -U attendance_user attendance_db < backup.sql
```

### Automated Backup with Cron
```bash
# Add to crontab
0 2 * * * /home/user/backup_database.sh
```

```bash
#!/bin/bash
# backup_database.sh
BACKUP_DIR="/var/backups/attendance"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
sudo -u postgres pg_dump attendance_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

## Monitoring & Alerts

### Setup Email Alerts
```python
# In config/settings.py
ADMINS = [('Admin', 'admin@example.com')]
SERVER_EMAIL = 'alerts@example.com'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
        },
    },
}
```

### Prometheus Alerts
```yaml
# prometheus_rules.yml
groups:
- name: django
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
  
  - alert: SlowRequests
    expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
    for: 5m
    annotations:
      summary: "Slow requests detected"
```

## Troubleshooting

### Application Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs web

# Run migrations
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py migrate

# Check settings
python manage.py check --deploy
```

### Database Connection Issues
```bash
# Test connection
psql -h db_host -U attendance_user -d attendance_db -c "SELECT 1"

# Check environment variables
env | grep DB_
```

### High Memory Usage
```bash
# Check container memory
docker-compose -f docker-compose.prod.yml stats

# Restart services
docker-compose -f docker-compose.prod.yml restart web
```

### Cache Issues
```bash
# Clear Redis cache
redis-cli FLUSHDB

# Or
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli FLUSHDB
```

## Maintenance

### Regular Tasks
- Daily: Monitor application logs
- Weekly: Review backup integrity
- Monthly: Update dependencies, patching
- Quarterly: Performance review, optimization
- Annually: Capacity planning, disaster recovery drill

### Dependency Updates
```bash
# Check for updates
pip list --outdated

# Update safe dependencies
pip install -U package_name

# Run tests after updates
python -m pytest

# Restart services
docker-compose -f docker-compose.prod.yml restart web
```

## Support & Resources

- Django Documentation: https://docs.djangoproject.com
- PostgreSQL Documentation: https://www.postgresql.org/docs
- Docker Documentation: https://docs.docker.com
- Nginx Documentation: https://nginx.org/en/docs
- Prometheus Documentation: https://prometheus.io/docs