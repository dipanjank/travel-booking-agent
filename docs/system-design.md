# System Design

## 1. Architecture Overview

The system consists of three components connected in a linear chain:

```
┌─────────────────────────────┐
│   Conversational QA App     │
│   (FastAPI + LangGraph)     │
│                             │
│  - Auth & user management   │
│  - Chat API (REST)          │
│  - LangChain ReAct agent    │
│  - Conversation memory      │
└──────┬──────────────┬───────┘
       │              │ MCP over Streamable HTTP
       │ SQL          v
       │    ┌─────────────────────────────┐
       │    │        MCP Server           │
       │    │       (fastMCP)             │
       │    │                             │
       │    │  - search_flights tool      │
       │    │  - book_flight tool         │
       │    └─────────────┬───────────────┘
       │                  │ SQL (psycopg2 via SQLAlchemy)
       v                  v
┌─────────────────────────────┐
│     PostgreSQL (RDS)        │
│                             │
│  users (QA app),            │
│  airports, airlines,        │
│  flights, routes,           │
│  bookings, passengers       │
└─────────────────────────────┘
```

**Database access:** The QA app accesses the database directly for authentication and user management (the `users` table). All flight and booking data access goes through the MCP server's tools.

---

## 2. Component Details

### 2.1 MCP Server (fastMCP)

The MCP server is built with fastMCP and exposes two tools over Streamable HTTP transport on port 8001. See [`mcp_server/README.md`](../mcp_server/README.md) for design and implementation details.

### 2.2 Conversational QA App (FastAPI + LangGraph)

The QA app is a FastAPI server with database-backed authentication, role-based user management, and a LangGraph ReAct agent backed by MCP tools. It uses synchronous SQLAlchemy sessions and sync `def` route handlers.

**Layered architecture:**

- **Models** — SQLAlchemy ORM models (`User`)
- **Repositories** — Data access layer (`GenericRepository[T]`, `UserRepository`)
- **Services** — Business logic (`AuthService`, `AdminService`, `AgentService`)
- **Routers** — FastAPI route handlers (`auth`, `admin`)
- **Dependencies** — FastAPI dependency injection wiring

**Database setup (sync SQLAlchemy):**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(settings.database_url, pool_size=10, max_overflow=5)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
```

**Application startup:** Tables are created via `Base.metadata.create_all(engine)`. An initial admin user is seeded from environment variables (`ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`) if no `ADMIN_USER` exists in the database.

**User management:** Admin users (`ADMIN_USER` role) can create, list, and delete users via the `/api/admin/users` endpoints. New users receive a randomly generated one-time password. Two roles are supported: `ADMIN_USER` and `APPLICATION_USER`. Admin users cannot be deleted.

**Admin endpoints:**

```python
router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])

@router.post("/users", status_code=201)
def create_user(body: CreateUserRequest, service=Depends(get_admin_service)):
    return service.create_user(body)

@router.get("/users")
def list_users(service=Depends(get_admin_service)):
    return service.list_users()

@router.delete("/users/{user_id}")
def delete_user(user_id: str, service=Depends(get_admin_service)):
    return service.delete_user(user_id)
```

**Authentication:** JWT-based. Login validates credentials against the `users` table, returns a short-lived access token (30 min, Bearer header) and sets a long-lived refresh token (7 days, HttpOnly cookie). Passwords are hashed with bcrypt (12 rounds). Tokens are encoded with HS256 via `python-jose`.

**Auth endpoints:**

```python
router = APIRouter(prefix="/api/auth")

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, response: Response, service=Depends(get_auth_service)):
    token_response, refresh_token = service.login(body)
    _set_refresh_cookie(response, refresh_token)
    return token_response

@router.post("/refresh", response_model=TokenResponse)
def refresh(response: Response, token=Depends(get_refresh_token), service=Depends(get_auth_service)):
    token_response, new_refresh_token = service.refresh(token)
    _set_refresh_cookie(response, new_refresh_token)
    return token_response

@router.post("/logout")
def logout(response: Response, _=Depends(get_current_user)):
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out"}
```

**Protected endpoint guard:**

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    user = repo.get_by_id(uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN_USER":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

**MCP client and agent:** Managed by `AgentService`, which starts the MCP client and creates the ReAct agent during application startup, and tears them down on shutdown.

```python
class AgentService:
    async def start(self) -> None:
        self._mcp_client = MultiServerMCPClient({"travel": {"transport": "streamable_http", "url": settings.mcp_server_url}})
        await self._mcp_client.__aenter__()
        tools = self._mcp_client.get_tools()
        checkpointer = PostgresSaver(conn_string=settings.checkpoint_postgres_url) if settings.checkpoint_postgres_url else None
        self._agent = create_react_agent(model=settings.agent_model, tools=tools, checkpointer=checkpointer)

    async def invoke(self, message: str, session_id: str) -> str:
        result = await self._agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": session_id}},
        )
        return result["messages"][-1].content
```

### 2.3 Database (PostgreSQL on RDS)

**Schema:**

**users** (managed by QA app via SQLAlchemy ORM)

| Column        | Type         | Constraints                                              |
|---------------|--------------|----------------------------------------------------------|
| id            | UUID         | PK, default uuid4                                        |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL                                         |
| email         | VARCHAR(255) | UNIQUE, NOT NULL                                         |
| password_hash | VARCHAR(255) | NOT NULL                                                 |
| role          | VARCHAR(20)  | NOT NULL, CHECK IN ('ADMIN_USER', 'APPLICATION_USER')    |
| created_at    | TIMESTAMP    | NOT NULL, default now()                                  |
| updated_at    | TIMESTAMP    | NOT NULL, default now(), on update now()                 |

**airports** (SQL DDL in `sql/tables.sql`)

| Column    | Type         | Constraints |
|-----------|--------------|-------------|
| iata_code | CHAR(3)      | PK          |
| name      | VARCHAR(255) | NOT NULL    |
| city      | VARCHAR(255) | NOT NULL    |
| country   | VARCHAR(100) | NOT NULL    |
| timezone  | VARCHAR(50)  | NOT NULL    |

**airlines**

| Column    | Type         | Constraints |
|-----------|--------------|-------------|
| iata_code | CHAR(2)      | PK          |
| name      | VARCHAR(255) | NOT NULL    |

**flights**

| Column            | Type          | Constraints              |
|-------------------|---------------|--------------------------|
| flight_id         | SERIAL        | PK                       |
| airline_code      | CHAR(2)       | FK -> airlines.iata_code |
| flight_number     | VARCHAR(10)   | NOT NULL                 |
| departure_airport | CHAR(3)       | FK -> airports.iata_code |
| arrival_airport   | CHAR(3)       | FK -> airports.iata_code |
| departure_time    | TIMESTAMPTZ   | NOT NULL                 |
| arrival_time      | TIMESTAMPTZ   | NOT NULL                 |
| duration_minutes  | INT           | NOT NULL                 |
| cabin_class       | VARCHAR(20)   | NOT NULL                 |
| base_price        | DECIMAL(10,2) | NOT NULL                 |
| available_seats   | INT           | NOT NULL                 |

**routes**

| Column            | Type          | Constraints              |
|-------------------|---------------|--------------------------|
| route_id          | SERIAL        | PK                       |
| departure_airport | CHAR(3)       | FK -> airports.iata_code |
| arrival_airport   | CHAR(3)       | FK -> airports.iata_code |
| total_duration    | INT           | NOT NULL                 |
| total_price       | DECIMAL(10,2) | NOT NULL                 |
| num_stops         | INT           | NOT NULL                 |

**route_flights** (junction table)

| Column    | Type | Constraints                           |
|-----------|------|---------------------------------------|
| route_id  | INT  | PK (composite), FK -> routes.route_id |
| flight_id | INT  | FK -> flights.flight_id               |
| leg_order | INT  | PK (composite)                        |

**bookings**

| Column        | Type         | Constraints                   |
|---------------|--------------|-------------------------------|
| booking_id    | SERIAL       | PK                            |
| pnr           | CHAR(6)      | UNIQUE, NOT NULL              |
| route_id      | INT          | FK -> routes.route_id         |
| contact_email | VARCHAR(255) | NOT NULL                      |
| contact_phone | VARCHAR(20)  | NOT NULL                      |
| booked_at     | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()       |
| status        | VARCHAR(20)  | NOT NULL, DEFAULT 'CONFIRMED' |

**passengers**

| Column          | Type         | Constraints               |
|-----------------|--------------|---------------------------|
| passenger_id    | SERIAL       | PK                        |
| booking_id      | INT          | FK -> bookings.booking_id |
| name            | VARCHAR(255) | NOT NULL                  |
| date_of_birth   | DATE         | NOT NULL                  |
| passport_number | VARCHAR(20)  | NOT NULL                  |

**Indexes:**

| Index                   | Table         | Columns                                              | Purpose                  |
|-------------------------|---------------|------------------------------------------------------|--------------------------|
| idx_flights_route_date  | flights       | (departure_airport, arrival_airport, departure_time) | Primary search query     |
| idx_flights_airline     | flights       | (airline_code)                                       | Airline filter           |
| idx_flights_price       | flights       | (base_price)                                         | Price filter             |
| idx_bookings_pnr        | bookings      | (pnr)                                                | PNR lookup               |
| idx_route_flights_route | route_flights | (route_id, leg_order)                                | Route composition lookup |

**Database access layer:** SQLAlchemy 2.0 with synchronous engine (`psycopg2` driver). Connection pool managed by SQLAlchemy, configured with pool size matching expected concurrency.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql+psycopg2://user:pass@rds-host:5432/travel",
    pool_size=10,
    max_overflow=5,
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
```

---

## 3. Authentication & User Management Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐        ┌──────────┐
│  Admin   │         │  QA App  │         │MCP Server│        │PostgreSQL│
└────┬─────┘         └────┬─────┘         └────┬─────┘        └────┬─────┘
     │  POST /api/auth/login│                    │                   │
     │  (username+password) │                    │                   │
     │────────────────────>│                    │                   │
     │                     │  query users table  │                   │
     │                     │─────────────────────────────────────── >│
     │  access_token (body) │                    │                   │
     │  refresh_token (cookie)                   │                   │
     │<────────────────────│                    │                   │
     │                     │                    │                   │
     │  POST /api/admin/users                    │                   │
     │  Authorization:     │                    │                   │
     │    Bearer <token>   │                    │                   │
     │  {username, email,  │                    │                   │
     │   role}             │                    │                   │
     │────────────────────>│                    │                   │
     │                     │  insert into users  │                   │
     │                     │─────────────────────────────────────── >│
     │  {user + one-time   │                    │                   │
     │   password}         │                    │                   │
     │<────────────────────│                    │                   │
     │                     │                    │                   │
     │  POST /chat         │                    │                   │
     │  Authorization:     │                    │                   │
     │    Bearer <token>   │                    │                   │
     │────────────────────>│                    │                   │
     │                     │  MCP tool call     │                   │
     │                     │───────────────────>│                   │
     │                     │  tool result       │                   │
     │                     │<───────────────────│                   │
     │  chat response      │                    │                   │
     │<────────────────────│                    │                   │
```

**Auth boundaries:**
1. **User -> QA App:** JWT-based. Access token (30 min, Bearer header) + refresh token (7 days, HttpOnly cookie). Users stored in the `users` table with bcrypt-hashed passwords. Initial admin seeded at startup from environment variables. Admin users can create additional users with role-based access control (`ADMIN_USER`, `APPLICATION_USER`).
2. **QA App -> PostgreSQL:** Direct connection via SQLAlchemy (sync) for the `users` table. Credentials stored in AWS Secrets Manager.
3. **MCP Server -> PostgreSQL:** Database username/password, stored in AWS Secrets Manager, injected as environment variables at deploy time.

---

## 4. AWS Deployment

```
┌─────────────────────────────────────────────────────────┐
│                         VPC                             │
│                                                         │
│  ┌─────────────────┐       ┌─────────────────┐         │
│  │  ECS Fargate    │       │  ECS Fargate    │         │
│  │  QA App         │──────>│  MCP Server     │         │
│  │  (public subnet)│  MCP  │  (private subnet)│         │
│  │  Port 8000      │       │  Port 8001      │         │
│  └────────┬────────┘       └────────┬────────┘         │
│           │                         │                   │
│           │ SQL (users)             │ SQL (flights,     │
│           │                         │     bookings)     │
│           v                         v                   │
│           │                ┌─────────────────┐         │
│           └───────────────>│  RDS PostgreSQL  │         │
│                            │  (private subnet)│         │
│                            └─────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
            │
            v
   ┌─────────────────┐
   │  ALB             │
   │  (internet-facing)│
   └─────────────────┘
```

| Component        | AWS Service                     | Notes                                                       |
|------------------|---------------------------------|-------------------------------------------------------------|
| QA App           | ECS Fargate (public subnet)     | Behind ALB, serves chat UI and API                          |
| MCP Server       | ECS Fargate (private subnet)    | Accessible only from QA App's security group                |
| Database         | RDS PostgreSQL (private subnet) | Accessible only from MCP Server's security group            |
| Secrets          | Secrets Manager                 | DB credentials, QA login credentials                        |
| Container images | ECR                             | One repo per service                                        |

**Network rules:**
- ALB accepts HTTPS from the internet, forwards to QA App on port 8000
- QA App security group allows outbound to MCP Server on port 8001 and to RDS on port 5432
- MCP Server security group allows inbound only from QA App, outbound to RDS on port 5432
- RDS security group allows inbound from both QA App and MCP Server

---

## 5. Project Structure

```
travel-booking-agent/
├── docs/
│   ├── requirements.md
│   ├── system-design.md
│   └── work-planning.md
├── mcp_server/
│   ├── __init__.py
│   ├── main.py              # FastMCP server entry point
│   ├── schemas.py           # Pydantic models (search/booking request/response)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py        # search_flights tool
│   │   └── booking.py       # book_flight tool
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py        # SQLAlchemy engine
│   │   ├── models.py        # ORM models
│   │   └── queries.py       # Query functions
│   └── Dockerfile
├── backend/
│   ├── booking_agent/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, lifespan, admin seeding
│   │   ├── config.py         # pydantic-settings configuration
│   │   ├── database.py       # SQLAlchemy engine, session, Base
│   │   ├── dependencies.py   # FastAPI DI wiring and auth guards
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py       # User ORM model
│   │   ├── repositories/
│   │   │   ├── base.py        # GenericRepository[T]
│   │   │   └── user_repository.py
│   │   ├── services/
│   │   │   ├── admin_service.py   # User management logic
│   │   │   ├── agent_service.py   # MCP client + ReAct agent lifecycle
│   │   │   └── auth_service.py    # Login, refresh, token logic
│   │   ├── routers/
│   │   │   ├── admin.py       # /api/admin/users CRUD
│   │   │   └── auth.py        # /api/auth login/refresh/logout
│   │   ├── schemas/
│   │   │   ├── __init__.py    # Re-exports all schemas
│   │   │   ├── auth.py        # LoginRequest, TokenResponse
│   │   │   ├── chat.py        # ChatRequest, ChatResponse
│   │   │   └── user.py        # CreateUserRequest/Response, UserListResponse
│   │   └── utils/
│   │       └── auth.py        # JWT, bcrypt, password generation
│   ├── pyproject.toml
│   └── Dockerfile
├── sql/
│   └── tables.sql           # DDL applied manually
├── scripts/
│   └── seed_data.py         # Populate airports, airlines, sample flights
└── CLAUDE.md
```

---

## 6. Key Dependencies

| Package                  | Purpose                                                 |
|--------------------------|---------------------------------------------------------|
| `pydantic`               | Schema validation for API, MCP tools, and data transfer |
| `pydantic-settings`      | Environment variable configuration                      |
| `fastmcp`                | MCP server framework                                    |
| `fastapi`                | Web framework for QA app                                |
| `uvicorn`                | ASGI server                                             |
| `sqlalchemy`             | ORM and synchronous database access (both services)     |
| `psycopg2-binary`        | PostgreSQL driver (MCP server)                          |
| `psycopg`                | PostgreSQL driver (QA app)                              |
| `langchain-mcp-adapters` | Load MCP tools into LangChain                           |
| `langgraph`              | Agent framework (ReAct agent, checkpointing)            |
| `langchain-anthropic`    | Claude model integration                                |
| `httpx`                  | HTTP client                                             |
| `python-jose`            | JWT encoding/decoding (HS256)                           |
| `bcrypt`                 | Password hashing (12 rounds)                            |

---

## 7. PNR Generation

PNR is a 6-character alphanumeric code (uppercase letters + digits, excluding ambiguous characters like 0/O, 1/I). Generated at booking time, checked for uniqueness against the bookings table before insert.

```python
import random
import string

PNR_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_pnr() -> str:
    return "".join(random.choices(PNR_CHARS, k=6))
```
