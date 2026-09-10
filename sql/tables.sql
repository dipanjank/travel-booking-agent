-- airports
CREATE TABLE airports (
    iata_code   CHAR(3) PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    city        VARCHAR(255) NOT NULL,
    country     VARCHAR(100) NOT NULL,
    timezone    VARCHAR(50) NOT NULL
);

-- airlines
CREATE TABLE airlines (
    iata_code   CHAR(2) PRIMARY KEY,
    name        VARCHAR(255) NOT NULL
);

-- flights
CREATE TABLE flights (
    flight_id           SERIAL PRIMARY KEY,
    airline_code        CHAR(2) NOT NULL REFERENCES airlines(iata_code),
    flight_number       VARCHAR(10) NOT NULL,
    departure_airport   CHAR(3) NOT NULL REFERENCES airports(iata_code),
    arrival_airport     CHAR(3) NOT NULL REFERENCES airports(iata_code),
    departure_time      TIMESTAMPTZ NOT NULL,
    arrival_time        TIMESTAMPTZ NOT NULL,
    duration_minutes    INT NOT NULL,
    cabin_class         VARCHAR(20) NOT NULL,
    base_price          DECIMAL(10, 2) NOT NULL,
    available_seats     INT NOT NULL
);

-- routes
CREATE TABLE routes (
    route_id        SERIAL PRIMARY KEY,
    total_duration  INT NOT NULL,
    total_price     DECIMAL(10, 2) NOT NULL,
    num_stops       INT NOT NULL
);

-- route_flights (junction table linking routes to their flight legs)
CREATE TABLE route_flights (
    route_id    INT NOT NULL REFERENCES routes(route_id),
    flight_id   INT NOT NULL REFERENCES flights(flight_id),
    leg_order   INT NOT NULL,
    PRIMARY KEY (route_id, leg_order)
);

-- bookings
CREATE TABLE bookings (
    booking_id      SERIAL PRIMARY KEY,
    pnr             CHAR(6) UNIQUE NOT NULL,
    route_id        INT NOT NULL REFERENCES routes(route_id),
    contact_email   VARCHAR(255) NOT NULL,
    contact_phone   VARCHAR(20) NOT NULL,
    booked_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED'
);

-- passengers
CREATE TABLE passengers (
    passenger_id    SERIAL PRIMARY KEY,
    booking_id      INT NOT NULL REFERENCES bookings(booking_id),
    name            VARCHAR(255) NOT NULL,
    date_of_birth   DATE NOT NULL,
    passport_number VARCHAR(20) NOT NULL
);

-- Indexes

-- Primary search query: flights from A to B on a date
CREATE INDEX idx_flights_route_date
    ON flights (departure_airport, arrival_airport, departure_time);

-- Filter by airline
CREATE INDEX idx_flights_airline ON flights (airline_code);

-- Filter by price
CREATE INDEX idx_flights_price ON flights (base_price);

-- PNR lookup
CREATE INDEX idx_bookings_pnr ON bookings (pnr);

-- Route composition lookup
CREATE INDEX idx_route_flights_route ON route_flights (route_id, leg_order);
