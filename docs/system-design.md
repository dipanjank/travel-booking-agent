# System Design

## 1. Architecture Overview

The system consists of three components connected in a linear chain:

```
┌─────────────────────────────┐
│   Conversational QA App     │
│   (FastAPI + LangGraph)     │
│                             │
│  - Chat UI (REST)           │
│  - LangChain ReAct agent    │
│  - Conversation memory      │
└─────────────┬───────────────┘
              │ MCP over Streamable HTTP
              v
┌─────────────────────────────┐
│        MCP Server           │
│       (fastMCP)             │
│                             │
│  - search_flights tool      │
│  - book_flight tool         │
└─────────────┬───────────────┘
              │ SQL (psycopg2 via SQLAlchemy)
              v
┌─────────────────────────────┐
│     PostgreSQL (RDS)        │
│                             │
│  airports, airlines,        │
│  flights, routes,           │
│  bookings, passengers       │
└─────────────────────────────┘
```

**Key constraint:** The QA app never accesses the database directly. All data access goes through the MCP server's tools.

---

## 2. Component Details

### 2.1 MCP Server (fastMCP)

The MCP server is built with fastMCP and exposes two tools over Streamable HTTP transport on port 8001. See [`mcp_server/README.md`](../mcp_server/README.md) for design and implementation details.

### 2.2 Conversational QA App (FastAPI + LangGraph)

The QA app is a FastAPI server that serves the chat interface and runs a LangGraph ReAct agent backed by MCP tools.

**MCP client setup:**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient({
    "travel": {
        "transport": "http",
        "url": "http://mcp-server:8001/mcp",
    },
})
tools = mcp_client.get_tools()
```

**Agent setup:**

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver(conn_string=POSTGRES_URL)

agent = create_react_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=tools,
    checkpointer=checkpointer,
)
```

**Pydantic schemas for QA App API:**

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str
```

**FastAPI endpoints:**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user=Depends(authenticate_user)):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": request.message}]},
        {"configurable": {"thread_id": request.session_id}},
    )
    return ChatResponse(
        reply=response["messages"][-1].content,
        session_id=request.session_id,
    )
```

**Authentication:** JWT-based authentication following the same pattern as `knowledge-base-qa-webapp`. A single admin user is seeded at startup from environment variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`). Passwords are hashed with bcrypt. Login returns a short-lived access token (Bearer) and sets a long-lived refresh token as an HttpOnly cookie.

**Auth utilities:**

```python
from jose import jwt
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "type": "access", "exp": datetime.utcnow() + timedelta(minutes=30)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "type": "refresh", "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
```

**Auth endpoints:**

```python
@router.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    # Validate credentials, return access_token, set refresh_token cookie

@router.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh(response: Response, token: str = Depends(get_refresh_token)):
    # Decode refresh token cookie, issue new access + refresh tokens

@router.post("/api/auth/logout")
async def logout(response: Response):
    # Delete refresh_token cookie
```

**Protected endpoint guard:**

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]
```

### 2.3 Database (PostgreSQL on RDS)

**Schema** (SQL DDL in `sql/tables.sql`):

**airports**

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

## 3. Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│   User   │         │  QA App  │         │MCP Server│
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │  POST /api/auth/login│                    │
     │  (username+password) │                    │
     │────────────────────>│                    │
     │  access_token (body) │                    │
     │  refresh_token (cookie)                   │
     │<────────────────────│                    │
     │                     │                    │
     │  POST /chat         │                    │
     │  Authorization:     │                    │
     │    Bearer <token>   │                    │
     │────────────────────>│                    │
     │                     │  MCP tool call     │
     │                     │───────────────────>│
     │                     │  tool result       │
     │                     │<───────────────────│
     │  chat response      │                    │
     │<────────────────────│                    │
     │                     │                    │
     │  POST /api/auth/refresh                   │
     │  (refresh_token cookie)                   │
     │────────────────────>│                    │
     │  new access_token   │                    │
     │  new refresh_token (cookie)               │
     │<────────────────────│                    │
```

**Auth boundaries:**
1. **User -> QA App:** JWT-based. Access token (30 min, Bearer header) + refresh token (7 days, HttpOnly cookie). Single admin user seeded from environment variables, password hashed with bcrypt.
2. **MCP Server -> PostgreSQL:** Database username/password, stored in AWS Secrets Manager, injected as environment variables at deploy time.

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
│  └─────────────────┘       └────────┬────────┘         │
│           │                         │                   │
│           │                         │ SQL               │
│           │                         v                   │
│           │                ┌─────────────────┐         │
│           │                │  RDS PostgreSQL  │         │
│           │                │  (private subnet)│         │
│           │                └─────────────────┘         │
│           │                                             │
└───────────┼─────────────────────────────────────────────┘
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
- QA App security group allows outbound to MCP Server on port 8001
- MCP Server security group allows inbound only from QA App, outbound to RDS on port 5432
- RDS security group allows inbound only from MCP Server

---

## 5. Project Structure

```
travel-booking-agent/
├── docs/
│   ├── requirements.md
│   └── system-design.md
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
├── qa_app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── schemas.py           # Pydantic models (ChatRequest, ChatResponse)
│   ├── agent.py             # LangGraph agent setup
│   ├── auth.py              # Login + session management
│   ├── mcp_client.py        # MCP client setup
│   ├── templates/           # Chat UI (Jinja2 or static)
│   └── Dockerfile
├── db/
│   └── migrations/          # Alembic migrations
│       ├── alembic.ini
│       └── versions/
├── scripts/
│   └── seed_data.py         # Populate airports, airlines, sample flights
├── pyproject.toml
└── CLAUDE.md
```

---

## 6. Key Dependencies

| Package                  | Purpose                                                 |
|--------------------------|---------------------------------------------------------|
| `pydantic`               | Schema validation for API, MCP tools, and data transfer |
| `fastmcp`                | MCP server framework                                    |
| `fastapi`                | Web framework for QA app                                |
| `uvicorn`                | ASGI server                                             |
| `sqlalchemy`             | ORM and synchronous database access                     |
| `psycopg2-binary`        | PostgreSQL driver                                       |
| `alembic`                | Database migrations                                     |
| `langchain-mcp-adapters` | Load MCP tools into LangChain                           |
| `langgraph`              | Agent framework (ReAct agent, checkpointing)            |
| `langchain-anthropic`    | Claude model integration                                |
| `httpx`                  | HTTP client                                             |
| `python-jose`            | JWT encoding/decoding (HS256)                           |
| `bcrypt`                 | Password hashing                                        |

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
