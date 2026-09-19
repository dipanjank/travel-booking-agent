# Booking MCP Server

MCP server for flight search and booking, built with [fastMCP](https://github.com/jlowin/fastmcp). Exposes tools over Streamable HTTP on port 8001. Connects to PostgreSQL via SQLAlchemy.

## Tools

| Tool             | Input                  | Output                | Description                                  |
|------------------|------------------------|-----------------------|----------------------------------------------|
| `search_flights` | `FlightSearchRequest`  | `FlightSearchResult[]`| Search available routes between two airports |
| `book_flight`    | `BookingRequest`       | `BookingConfirmation` | Book a route for one or more passengers      |

### search_flights

Accepts origin/destination IATA codes (required) and optional filters:

- `date` — departure date
- `time_of_day` — morning (06-12), afternoon (12-18), evening (18-24)
- `airline` — airline IATA code (matches any leg)
- `max_price` — upper price limit
- `max_stops` — maximum number of stops
- `cabin_class` — economy, business, or first (matches any leg)

Returns matching routes with their flight legs, total duration, number of stops, and total price.

### book_flight

Accepts a `route_id` (from search results), passenger details (name, date of birth, passport number), and contact information. Creates a booking with a unique 6-character PNR and returns a confirmation with the full itinerary.

## Architecture

```
MCP Tool call
  -> Service (business logic, schema conversion)
    -> Repository (data access, query building)
      -> SQLAlchemy ORM
        -> PostgreSQL
```

### Layers

**Tools** (`app/tools/`) — MCP tool entry points. Create a database session, instantiate repositories and services via dependency injection, and delegate to the service layer.

**Services** (`app/services/`) — Business logic. `FlightSearchService` converts route query results to response schemas. `BookingService` generates unique PNRs, orchestrates booking and passenger creation, and commits the transaction.

**Repositories** (`app/db/repositories.py`) — Data access. `RouteRepository` builds dynamic search queries with optional filters via private `_filter_by_*` methods. `BookingRepository` handles booking and passenger inserts.

**Models** (`app/db/models.py`) — SQLAlchemy ORM models mapping to the database schema (airports, airlines, flights, routes, route_flights, bookings, passengers).

**Schemas** (`app/schemas.py`) — Pydantic models for MCP tool inputs and outputs.

### Dependency flow

```
tools/search.py:
  SessionLocal -> RouteRepository -> FlightSearchService.search()

tools/booking.py:
  SessionLocal -> RouteRepository + BookingRepository -> BookingService.book()
```

Services never create their own repositories or sessions — these are injected by the tool layer, making services testable with mocks.

### Pre-computed routes

Routes are pre-computed and stored in the `routes` table with denormalized columns (`departure_airport`, `arrival_airport`, `total_duration`, `total_price`, `num_stops`). The `route_flights` junction table links each route to its ordered flight legs.

This avoids computing multi-leg itineraries at query time — search queries filter directly on the `routes` table instead of joining and aggregating flights on every request. The trade-off is that routes must be regenerated when flight data changes (schedules, prices, new flights), but flight data in this system changes infrequently compared to how often searches run, so optimizing for read performance is the right call.

## Configuration

| Environment variable | Description                                          |
|----------------------|------------------------------------------------------|
| `DATABASE_URL`       | PostgreSQL connection string (`postgresql+psycopg2://...`) |

## Docker

```bash
docker build -t booking-mcp-server .
docker run -p 8001:8001 -e DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db booking-mcp-server
```

## Dependencies

| Package          | Purpose                    |
|------------------|----------------------------|
| `fastmcp`        | MCP server framework       |
| `sqlalchemy`     | ORM and database access    |
| `psycopg2-binary`| PostgreSQL driver          |
| `pydantic`       | Schema validation          |
