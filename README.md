# AI Product Search Platform - Modular Monolith

An enterprise-grade, AI-powered product search platform that aggregates offers from multiple Russian marketplaces (Wildberries, Ozon, Avito) using a modular monolithic architecture built with FastAPI, SQLAlchemy, and PostgreSQL.

## Architecture

This project demonstrates a modular monolith pattern - all code runs in a single process but organized into independent modules with clear boundaries.

### Core Modules

1. Auth Module - User registration, login, JWT tokens, password management
2. Search Module - AI-powered search with GPT routing, multi-marketplace orchestration
3. Marketplace Module - Marketplace connectors and product scrapers
4. Products Module - Product catalog, SKU matching, normalization
5. Billing Module - Subscription plans, quota management
6. Analytics Module - Search analytics, popular queries, user activity

## Technology Stack

- Language: Python 3.11
- Web Framework: FastAPI
- ORM: SQLAlchemy 2.0 (Async)
- Database: PostgreSQL
- Cache: Redis
- Auth: JWT (access + refresh tokens)
- AI: OpenAI GPT API
- Validation: Pydantic v2
- Container: Docker & Docker Compose

## Database Schema

Tables:
- users - User accounts with subscription info
- plans - Subscription plan definitions
- subscriptions - User subscription records
- products - Product catalog
- offers - Marketplace-specific offers
- search_events - Search history and analytics

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/kukarek/test.git
cd test

docker-compose up

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your settings

docker-compose up postgres redis

python scripts/init_db.py

uvicorn app.main:app --reload
```

## API Documentation

Access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"secure123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123"}'

# Use token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Key Features

- Async/Await throughout for scalability
- Full type hints with Pydantic v2
- Clean architecture (Repository + Service patterns)
- Custom error handling with proper HTTP status codes
- Database optimization with indexes and eager loading
- Redis caching integration
- Auto-generated API documentation
- Docker support with production-ready images
- Modular design for easy extension and testing

## Project Structure

```
app/
├── core/           # Configuration, database, security
├── common/         # Shared models, schemas, exceptions
├── modules/        # Business logic (auth, search, products, etc.)
├── main.py         # FastAPI application
└── tests/          # Test suite

scripts/            # Database initialization and startup
docker/             # Docker-related files
```

## License

MIT License

---

Built with FastAPI, SQLAlchemy, and PostgreSQL
