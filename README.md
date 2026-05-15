# Blog Management System

FastAPI-based Blog Management System with JWT authentication, RBAC, Redis caching, and full CRUD operations.

## Features

- **JWT Authentication** with role-based access control (admin, author, reader)
- **Redis Cache-Aside Pattern** on post endpoints with automatic invalidation
- **Reaction System** with toggle behavior (like, love, haha, sad, angry)
- **Nested Comments** with parent/child threading
- **Admin Dashboard** with user management and system stats
- **Request Logging** with structured logging to console and file
- **Monitoring Endpoint** (`/metrics`) with request/error/cache statistics

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
uvicorn app.main:app --reload
```

### Docker

```bash
docker-compose up --build
```

### Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /register | No | Register (author/reader only) |
| POST | /login | No | Login, get JWT token |
| GET | /posts | No | List posts (paginated) |
| GET | /posts/{id} | No | View post (increments views) |
| POST | /posts | Author | Create post |
| PUT | /posts/{id} | Owner | Update own post |
| DELETE | /posts/{id} | Owner | Delete own post |
| GET | /posts/{id}/stats | No | Post analytics |
| GET | /my/posts | Author | Own posts with stats |
| POST | /posts/{id}/comments | Auth | Add comment |
| POST | /posts/{id}/comments/{cid}/reply | Auth | Reply to comment |
| PUT | /comments/{id} | Owner | Edit own comment |
| DELETE | /comments/{id} | Owner | Delete own comment |
| POST | /posts/{id}/react | Auth | Toggle reaction |
| GET | /admin/users | Admin | List all users |
| GET | /admin/users/{id} | Admin | View user details |
| PUT | /admin/users/{id}/role | Admin | Change user role |
| DELETE | /admin/users/{id} | Admin | Delete user + content |
| DELETE | /admin/posts/{id} | Admin | Delete any post |
| PUT | /admin/posts/{id} | Admin | Edit any post |
| GET | /admin/stats | Admin | System overview |
| GET | /metrics | No | Monitoring metrics |

## Project Structure

```
app/
  main.py, config.py, database.py, dependencies.py
  models/    user.py, post.py, comment.py, reaction.py
  schemas/   user.py, post.py, comment.py, reaction.py
  routes/    auth.py, posts.py, comments.py, reactions.py, admin.py
  services/  auth_service.py, post_service.py, comment_service.py, cache_service.py, permissions.py
  core/      logger.py, redis_client.py, seed.py, metrics.py
tests/
  conftest.py, test_auth.py, test_posts.py, test_comments.py, test_admin.py, test_reactions.py
```
