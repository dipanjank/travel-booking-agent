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

The MCP server is built with fastMCP and exposes two tools over Streamable HTTP transport.

**Server setup:**

```python
from fastmcp import FastMCP

mcp = FastMCP("TravelBookingServer")
```

**Pydantic schemas for MCP tools:**

```python
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal

# --- Search tool schemas ---

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., pattern=r"^[A-Z]{3}$", description="Departure airport IATA code")
    destination: str = Field(..., pattern=r"^[A-Z]{3}$", description="Arrival airport IATA code")
    date: date | None = Field(None, description="Departure date")
    time_of_day: Literal["morning", "afternoon", "evening"] | None = None
    airline: str | None = Field(None, pattern=r"^[A-Z0-9]{2}$", description="Airline IATA code")
    max_price: float | None = Field(None, gt=0)
    max_stops: int | None = Field(None, ge=0)
    cabin_class: Literal["economy", "business", "first"] | None = None

class FlightLeg(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    cabin_class: str

class FlightSearchResult(BaseModel):
    route_id: int
    legs: list[FlightLeg]
    total_duration_minutes: int
    num_stops: int
    total_price: float

# --- Booking tool schemas ---

class PassengerDetails(BaseModel):
    name: str = Field(..., min_length=1)
    date_of_birth: date
    passport_number: str = Field(..., min_length=5)

class BookingRequest(BaseModel):
    route_id: int
    passengers: list[PassengerDetails] = Field(..., min_length=1)
    contact_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    contact_phone: str

class BookingConfirmation(BaseModel):
    pnr: str
    route_id: int
    legs: list[FlightLeg]
    passengers: list[PassengerDetails]
    total_price: float
    status: str
    booked_at: datetime
```

**Tool definitions using Pydantic schemas:**

```python
@mcp.tool
def search_flights(request: FlightSearchRequest) -> list[FlightSearchResult]:
    """Search available flights between two airports."""
    # Build dynamic SQL query with filters
    # Join flights -> routes for multi-hop results
    # Return list of matching itineraries

@mcp.tool
def book_flight(request: BookingRequest) -> BookingConfirmation:
    """Book a flight for one or more passengers. Returns PNR and itinerary."""
    # Insert into bookings table, generate PNR
    # Insert passenger records
    # Return PNR + full itinerary details
```

**Running the server:**

```python
mcp.run(transport="http", host="0.0.0.0", port=8001)
```

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

**Authentication:** Simple username/password check. A single credential pair stored as environment variables. The `/chat` endpoint requires a valid session (cookie or token issued after login).

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

| Column         | Type          | Constraints |
|----------------|---------------|-------------|
| route_id       | SERIAL        | PK          |
| total_duration | INT           | NOT NULL    |
| total_price    | DECIMAL(10,2) | NOT NULL    |
| num_stops      | INT           | NOT NULL    |

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
     │  POST /login        │                    │
     │  (username+password) │                    │
     │────────────────────>│                    │
     │  session cookie     │                    │
     │<────────────────────│                    │
     │                     │                    │
     │  POST /chat         │                    │
     │  (message)          │                    │
     │────────────────────>│                    │
     │                     │  MCP tool call     │
     │                     │───────────────────>│
     │                     │  tool result       │
     │                     │<───────────────────│
     │  chat response      │                    │
     │<────────────────────│                    │
```

**Auth boundaries:**
1. **User -> QA App:** Username/password, session cookie. Single credential pair from environment variables.
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
