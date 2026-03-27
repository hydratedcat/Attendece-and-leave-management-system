# Attendance & Leave Automation

Django backend for attendance tracking, leave management, and monitoring with Prometheus + Grafana.

## Features

- **User Management**: Custom user model with role-based access (Employee, Manager, HR Admin)
- **Attendance Tracking**: Mark attendance with duplicate prevention and team reporting
- **Leave Management**: FSM-based leave requests with approval workflow and audit logging
- **Real-time Notifications**: WebSocket support for live updates on leave status changes
- **Email Notifications**: Asynchronous email notifications via Celery
- **Monitoring**: Prometheus metrics collection and Grafana dashboards
- **Performance Optimization**: Redis caching, database indexes, and query optimization
- **CI/CD Pipeline**: GitHub Actions with testing, linting, security scanning, and Docker builds
- **Production Ready**: Docker Compose setup with Nginx, security hardening, and health checks
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Quickstart

1. copy `.env.example` to `.env` and update values.
2. start the stack: `docker-compose up --build`
3. welcome URLs:
   - http://localhost:8000/admin/
   - http://localhost:8000/api/docs/
   - http://localhost:9090 (Prometheus)
   - http://localhost:3000 (Grafana)

## WebSocket Endpoints

- `ws://localhost:8000/ws/leaves/{user_id}/` - Leave status updates for employees
- `ws://localhost:8000/ws/notifications/` - General notifications for managers

## Metrics
- /metrics (Prometheus scrape)
- /health/ (Health check endpoint)

## API endpoints
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/
- POST /api/attendance/mark/
- GET /api/attendance/my/
- GET /api/attendance/team/
- POST /api/leaves/apply/
- PATCH /api/leaves/<id>/approve/
- PATCH /api/leaves/<id>/reject/
- GET /api/leaves/my/
- GET /api/leaves/pending/

## Development

### Running Tests
```bash
python -m pytest
```

### Code Quality
```bash
# Linting
flake8 .

# Formatting
black .
isort .

# Security scanning
safety check
bandit -r .
```

### Performance Monitoring
- Debug toolbar available at `http://localhost:8000/__debug__/`
- Cached report endpoints (15min for daily, 1hr for monthly)
- Database indexes on frequently queried fields

## Production Deployment

### Environment Setup
1. Copy `.env.prod.example` to `.env`
2. Update production values (database, Redis, secrets)
3. Run `docker-compose -f docker-compose.prod.yml up -d`

### Security Features
- HTTPS enforcement in production
- Secure session and CSRF cookies
- Content Security Policy headers
- SQL injection protection via Django ORM
- XSS protection and input validation

### Monitoring
- Prometheus metrics collection
- Health check endpoints
- Structured logging
- Performance monitoring with debug toolbar

## Notes
- Default DB engine is SQLite for local dev. Set `DB_ENGINE=postgres` to use postgres in docker.
- WebSocket connections require authentication
- Email notifications are sent asynchronously via Celery
- Report endpoints are cached for performance
