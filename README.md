<div align="center">

# 🏢 Attendance & Leave Management System

**A production-grade REST API for enterprise attendance tracking and leave automation**

[![CI/CD Pipeline](https://github.com/hydratedcat/Attendece-and-leave-management-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hydratedcat/Attendece-and-leave-management-system/actions/workflows/ci-cd.yml)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green?logo=django&logoColor=white)](https://djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.4-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**📖 API Docs**](#api-docs) • [**🚀 Quick Start**](#quick-start) • [**🏗️ Architecture**](#architecture) • [**🔐 Security**](#security)

</div>

---

## ✨ What This Does

A complete backend system for managing employee attendance and leave requests — built with real-world enterprise patterns:

| Feature | Details |
|---------|---------|
| 🔐 **Role-Based Access Control** | Employee → Manager → HR Admin permission hierarchy |
| 📋 **Attendance Tracking** | Mark attendance with duplicate prevention, team & monthly reports |
| 🌴 **Leave Workflow** | FSM-based approval pipeline (PENDING → APPROVED/REJECTED) with audit trail |
| 🔔 **Real-time Notifications** | WebSocket push notifications for live leave status updates |
| 📧 **Email Alerts** | Async email notifications via Celery task queue |
| 📊 **Monitoring** | Prometheus metrics + Grafana dashboards + health checks |
| ⚡ **Performance** | Redis caching (15-min daily, 1-hr monthly reports), DB indexes |
| 🛡️ **Security Hardened** | JWT auth with rotation/blacklist, rate limiting, all 13 security issues patched |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Clients                          │
│              (Web / Mobile / Postman)                │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────┐
│                    Nginx (Reverse Proxy)              │
│              Rate limiting + SSL termination          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Django + Daphne (ASGI)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Users   │ │Attendance│ │  Leaves  │ │Notifs  │ │
│  │   App    │ │   App    │ │   App    │ │  App   │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────┬───────────────────────────────┬──────────┘
           │                               │ WebSocket
┌──────────▼─────────┐        ┌────────────▼──────────┐
│   PostgreSQL 15     │        │      Redis 7.4         │
│   (Primary DB)      │        │  Cache + Celery Broker │
└─────────────────────┘        │  + Channel Layers      │
                               └───────────────────────┘
```

**Tech Stack:**

| Layer | Technology |
|-------|-----------|
| Framework | Django 6.0 + Django REST Framework |
| ASGI Server | Daphne (WebSocket support) |
| Database | PostgreSQL 15 |
| Cache / Queue | Redis 7.4 |
| Task Queue | Celery |
| Auth | JWT (SimpleJWT) with refresh rotation + blacklisting |
| Real-time | Django Channels (WebSockets) |
| API Docs | drf-spectacular (OpenAPI 3.0 / Swagger) |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions (test → lint → security → docker → deploy) |
| Deployment | Railway |

---

## 🚀 Quick Start

### Option A — Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/hydratedcat/Attendece-and-leave-management-system.git
cd Attendece-and-leave-management-system

# Set up environment
cp .env.example .env   # edit .env with your values

# Start the full stack
docker-compose up --build

# Run migrations (first time)
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Available at:
| URL | Service |
|-----|---------|
| http://localhost:8000/api/docs/ | 📖 Swagger UI (try all endpoints here) |
| http://localhost:8000/admin/ | 🔧 Django Admin |
| http://localhost:9090 | 📊 Prometheus |
| http://localhost:3000 | 📈 Grafana |

### Option B — Local Python

```bash
pip install -r requirements.txt
cp .env.example .env      # set DEBUG=True, DB uses SQLite by default
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📖 API Docs

Interactive Swagger UI: `http://localhost:8000/api/docs/`  
ReDoc: `http://localhost:8000/api/redoc/`

### Authentication Flow

```bash
# 1. Register
POST /api/auth/register/
{"username": "john", "email": "john@co.com", "password": "Pass@1234", "password2": "Pass@1234"}

# 2. Login → get JWT token
POST /api/auth/login/
{"username": "john", "password": "Pass@1234"}
# → {"access": "eyJ...", "refresh": "eyJ..."}

# 3. Use token in all requests
GET /api/attendance/my/
Authorization: Bearer eyJ...
```

### Key Endpoints

| Method | Endpoint | Role Required |
|--------|----------|--------------|
| `POST` | `/api/auth/register/` | Anyone |
| `POST` | `/api/auth/login/` | Anyone |
| `POST` | `/api/attendance/mark/` | Employee |
| `GET` | `/api/attendance/my/` | Employee |
| `GET` | `/api/attendance/team/` | Manager |
| `POST` | `/api/leaves/apply/` | Employee |
| `GET` | `/api/leaves/pending/` | Manager / HR Admin |
| `PATCH` | `/api/leaves/<id>/approve/` | Manager / HR Admin |
| `PATCH` | `/api/leaves/<id>/reject/` | Manager / HR Admin |
| `GET` | `/api/leaves/reports/summary/` | Manager / HR Admin |
| `GET` | `/api/leaves/audit/` | HR Admin only |
| `GET` | `/api/users/` | HR Admin only |
| `GET` | `/health/` | Anyone |

### WebSocket Endpoints

```javascript
// Real-time leave status updates (Employee)
ws://your-domain/ws/leaves/{user_id}/

// Manager notifications
ws://your-domain/ws/notifications/
```

---

## 🔐 Security

This project underwent a full security audit — **13 vulnerabilities patched**:

| Severity | Issue | Fix |
|----------|-------|-----|
| 🔴 Critical | Weak `SECRET_KEY` | Cryptographically random 50-char key |
| 🔴 Critical | `ALLOWED_HOSTS = ["*"]` | Defaults to empty (strict) |
| 🔴 Critical | Unsafe fallback secret | App crashes if SECRET_KEY missing |
| 🟠 High | Role self-assignment | `role` removed from registration serializer |
| 🟠 High | Docker runs as root | Non-root `appuser` in container |
| 🟠 High | No JWT expiry | 30-min access, 7-day refresh, token blacklisting |
| 🟠 High | Public metrics endpoint | Requires staff authentication |
| 🟠 High | Hardcoded DB password | Environment variable injection |
| 🟡 Medium | No rate limiting | 5/min login, 3/min register |
| 🟡 Medium | Debug toolbar always on | Only loads when `DEBUG=True` |
| 🟢 Low | Unpinned Docker images | All images pinned to specific versions |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# With coverage report
python -m pytest --cov=. --cov-report=html

# Run specific app tests
python -m pytest users/tests.py -v
```

**37 tests** covering authentication, permissions, attendance, leave workflow, and WebSocket notifications.

---

## 🔄 CI/CD Pipeline

Every push to `main` or `develop` automatically:

```
git push → Tests ✅ → Lint ✅ → Security Scan 🔒 → Docker Build 🐳 → Deploy to Railway 🚂
```

| Job | What it does |
|-----|-------------|
| **test** | Runs 37 tests with real PostgreSQL + Redis |
| **lint** | flake8, black, isort formatting checks |
| **security** | bandit static analysis + safety dependency scan |
| **docker** | Builds and pushes image to Docker Hub |
| **deploy** | Auto-deploys to Railway on `main` branch |

---

## 📁 Project Structure

```
├── config/          # Django settings, URLs, ASGI, middleware, metrics
├── users/           # Custom user model, JWT auth, role-based permissions
├── attendance/      # Attendance marking, team reports, caching
├── leaves/          # FSM leave workflow, approval, audit logging
├── notifications/   # WebSocket consumers, Celery tasks
├── nginx/           # Production reverse proxy config
├── .github/         # CI/CD workflows
├── Dockerfile       # Hardened production image
├── docker-compose.yml        # Development stack
├── docker-compose.prod.yml   # Production stack
└── railway.toml     # Railway deployment config
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

<div align="center">
Built with ❤️ using Django, Docker, and GitHub Actions
</div>
