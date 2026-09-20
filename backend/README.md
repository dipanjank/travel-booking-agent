# QA App Backend

FastAPI web server for the travel booking agent. Handles

- user authentication
- admin user management
- conversational flight search via a LangGraph ReAct agent backed by MCP tools.

## API Endpoints

### Authentication (`/api/auth`)

| Method | Path                | Description                                                                                      | Auth   |
|--------|---------------------|--------------------------------------------------------------------------------------------------|--------|
| POST   | `/api/auth/login`   | Authenticate with username/password. Returns access token, sets refresh token as HttpOnly cookie | None   |
| POST   | `/api/auth/refresh` | Issue new token pair using refresh token cookie                                                  | Cookie |
| POST   | `/api/auth/logout`  | Delete refresh token cookie                                                                      | Bearer |

### Chat (`/api`)

| Method | Path        | Description                                                        | Auth   |
|--------|-------------|--------------------------------------------------------------------|--------|
| POST   | `/api/chat` | Send a message to the flight search agent and receive a response   | Bearer |

The chat endpoint accepts `{ message, thread_id }` and returns `{ response, thread_id }`. Conversations are scoped per user — the backend prefixes the client's `thread_id` with the authenticated user's ID to ensure isolation.

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

**Services** (`booking_agent/services/`) — `AuthService` handles login and token refresh. `AdminService` handles user creation (with generated passwords), listing, and deletion. `AgentService` manages the MCP client and LangGraph ReAct agent lifecycle — started at application startup and used to invoke the conversational agent.

**Routers** (`booking_agent/routers/`) — Thin HTTP layer. Injects services via FastAPI `Depends()`.

**Dependencies** (`booking_agent/dependencies.py`) — Wires the injection chain: `get_db` -> `get_user_repo` -> `get_auth_service` / `get_admin_service`. `get_agent_service` returns the singleton `AgentService`. Auth guards: `get_current_user` (Bearer token), `require_admin` (role check).

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
| `MCP_SERVER_URL`                   | MCP server Streamable HTTP endpoint URL    | (required)           |
| `AGENT_MODEL`                      | Bedrock model ID for the agent             | `qwen.qwen3-next-80b-a3b` |
| `AWS_REGION`                       | AWS region for Bedrock                     | `eu-west-1`          |

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
export JWT_SECRET=dev-secret ADMIN_PASSWORD=dev-password DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/db MCP_SERVER_URL=http://localhost:8001/mcp
uvicorn booking_agent.main:app --reload --port 8000
```

## Docker

```bash
docker build -t qa-app-backend .
docker run -p 8000:8000 \
  -e JWT_SECRET=secret \
  -e ADMIN_PASSWORD=password \
  -e DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db \
  -e MCP_SERVER_URL=http://mcp-server:8001/mcp \
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
| `langchain-mcp-adapters` | MCP client for LangChain  |
| `langgraph`         | ReAct agent framework        |
| `langgraph-checkpoint-postgres` | Conversation checkpointing |
| `langchain-aws`     | ChatBedrockConverse model    |
