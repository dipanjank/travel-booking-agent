# QA App Backend

FastAPI web server for the travel booking agent. Handles user authentication, admin user management, and will serve the conversational chat interface backed by a LangGraph ReAct agent (not yet implemented).

## API Endpoints

### Authentication (`/api/auth`)

| Method | Path                | Description                                                                                      | Auth   |
|--------|---------------------|--------------------------------------------------------------------------------------------------|--------|
| POST   | `/api/auth/login`   | Authenticate with username/password. Returns access token, sets refresh token as HttpOnly cookie | None   |
| POST   | `/api/auth/refresh` | Issue new token pair using refresh token cookie                                                  | Cookie |
| POST   | `/api/auth/logout`  | Delete refresh token cookie                                                                      | Bearer |

### Admin (`/api/admin`)

All admin endpoints require a valid Bearer token with `ADMIN_USER` role.

| Method | Path                         | Description                                   | Response                   |
|--------|------------------------------|-----------------------------------------------|----------------------------|
| POST   | `/api/admin/users`           | Create user with random one-time password     | `CreateUserResponse` (201) |
| GET    | `/api/admin/users`           | List all users                                | `UserListResponse`         |
| DELETE | `/api/admin/users/{user_id}` | Delete a user (admin users cannot be deleted) | `MessageResponse`          |

## Architecture

```
Routers (HTTP layer)
  -> Services (business logic)
    -> Repositories (data access)
      -> SQLAlchemy ORM
        -> PostgreSQL
```

**Models** (`booking_agent/models/`) — SQLAlchemy ORM models. `User` with UUID primary key, username, email, password hash, and role (`ADMIN_USER` or `APPLICATION_USER`).

**Repositories** (`booking_agent/repositories/`) — `GenericRepository[T]` base class with CRUD operations (`get_by_id`, `get_one`, `get_all`, `count`, `create`, `delete`). `UserRepository` adds `get_by_username_or_email`.

**Services** (`booking_agent/services/`) — `AuthService` handles login and token refresh. `AdminService` handles user creation (with generated passwords), listing, and deletion.

**Routers** (`booking_agent/routers/`) — Thin HTTP layer. Injects services via FastAPI `Depends()`.

**Dependencies** (`booking_agent/dependencies.py`) — Wires the injection chain: `get_db` -> `get_user_repo` -> `get_auth_service` / `get_admin_service`. Auth guards: `get_current_user` (Bearer token), `require_admin` (role check).

### Auth flow

- **Access token:** JWT (HS256), 30-minute expiry, sent as `Authorization: Bearer <token>` header
- **Refresh token:** JWT (HS256), 7-day expiry, stored as HttpOnly cookie scoped to `/api/auth`
- **Password hashing:** bcrypt with 12 salt rounds
- **Admin seed:** An initial admin user is created on startup from environment variables if no `ADMIN_USER` exists

## Configuration

| Environment variable               | Description                                | Default              |
|------------------------------------|--------------------------------------------|----------------------|
| `JWT_SECRET`                       | Secret key for signing JWTs                | (required)           |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`  | Access token lifetime in minutes           | `30`                 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`    | Refresh token lifetime in days             | `7`                  |
| `ADMIN_USERNAME`                   | Username for the seeded admin user         | `admin`              |
| `ADMIN_EMAIL`                      | Email for the seeded admin user            | `admin@example.com`  |
| `ADMIN_PASSWORD`                   | Password for the seeded admin user         | (required)           |
| `DATABASE_URL`                     | PostgreSQL connection string               | (required)           |

## Development

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

Run the server locally:

```bash
export JWT_SECRET=dev-secret ADMIN_PASSWORD=dev-password DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/db
uvicorn booking_agent.main:app --reload --port 8000
```

## Docker

```bash
docker build -t qa-app-backend .
docker run -p 8000:8000 \
  -e JWT_SECRET=secret \
  -e ADMIN_PASSWORD=password \
  -e DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db \
  qa-app-backend
```

## Dependencies

| Package             | Purpose                      |
|---------------------|------------------------------|
| `fastapi`           | Web framework                |
| `uvicorn`           | ASGI server                  |
| `sqlalchemy`        | ORM and database access      |
| `psycopg`           | PostgreSQL driver            |
| `pydantic`          | Schema validation            |
| `pydantic-settings` | Environment variable loading |
| `python-jose`       | JWT encoding/decoding        |
| `bcrypt`            | Password hashing             |
