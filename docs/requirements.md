# Requirements

## 1. MCP Server for Flight Search and Booking

Build an MCP (Model Context Protocol) server that exposes tools for a travel website. The server supports two operations:

### 1a. Flight Search

Search for available flights between a source airport and a destination airport.

**Required parameters:**
- Source airport (IATA code, e.g. JFK, LHR)
- Destination airport (IATA code)

**Optional filter parameters:**
- Date (departure date)
- Time of day (morning, afternoon, evening, or specific time range)
- Airline
- Maximum price
- Number of hops (0 for direct flights only, 1+ for connecting flights)
- Cabin class (economy, business, first)

**Response:** A list of matching flights, each including airline, flight number(s), departure/arrival times, number of stops, layover details (if connecting), duration, cabin class, and price.

### 1b. Flight Booking

Book a specific flight for one or more passengers.

**Required parameters:**
- Flight identifier (from search results)
- User ID (authenticated user making the booking)

**Response:** A confirmed booking containing:
- PNR (Passenger Name Record) — a unique alphanumeric booking reference
- Full itinerary — flight number(s), departure/arrival airports and times, cabin class, and total price

### 1c. Database Schema

A relational database backing the MCP server, designed for efficient query performance.

**Core tables:**

- **airports** — IATA code (PK), name, city, country, timezone
- **airlines** — IATA code (PK), name
- **flights** — flight ID (PK), airline code (FK), flight number, departure airport (FK), arrival airport (FK), departure time, arrival time, duration, cabin class, base price, available seats
- **routes** — route ID (PK), ordered set of flight IDs representing a single- or multi-hop journey, total duration, total price, number of stops
- **bookings** — booking ID (PK), PNR (unique), route ID (FK), user ID (FK), booking timestamp, status

**Indexing considerations:**
- Composite index on flights for (departure_airport, arrival_airport, departure_time) to support the primary search query
- Index on bookings.PNR for fast booking lookup
- Index on flights.airline for airline-filtered searches

## 2. Conversational QA System

Build a conversational interface where a user can interact in natural language to search for and book flights.

**Capabilities:**
- Answer questions about available flights (e.g. "Are there any direct flights from JFK to LAX on Friday under $300?")
- Handle multi-turn conversation — refine searches, compare options, ask follow-up questions
- Walk the user through the booking process — collect passenger details, confirm selections, and complete the booking
- Return the PNR and itinerary after a successful booking

**Integration:** The conversational system acts as an MCP client, invoking the flight search and booking tools defined in Requirement 1 to fulfill user requests.
