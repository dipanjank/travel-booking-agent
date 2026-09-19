from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Airline, Airport, Base, Flight, Route, RouteFlight


@pytest.fixture()
def session():
    """Create an in-memory SQLite database and yield a session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def seed_data(session):
    """Insert airports, airlines, flights, and routes for testing.

    Creates two airports (JFK, LAX), two airlines (AA, UA), and four routes:
    - Route 1: JFK->LAX direct, AA, morning, economy, $300
    - Route 2: JFK->LAX direct, UA, afternoon, business, $800
    - Route 3: JFK->LAX via ORD (1 stop), AA+UA, morning first leg, economy, $250
    - Route 4: LAX->JFK direct, AA, evening, first, $1200
    """
    airports = [
        Airport(iata_code="JFK", name="John F Kennedy", city="New York", country="US", timezone="America/New_York"),
        Airport(
            iata_code="LAX", name="Los Angeles Intl", city="Los Angeles", country="US", timezone="America/Los_Angeles"
        ),
        Airport(iata_code="ORD", name="O'Hare Intl", city="Chicago", country="US", timezone="America/Chicago"),
    ]
    airlines = [
        Airline(iata_code="AA", name="American Airlines"),
        Airline(iata_code="UA", name="United Airlines"),
    ]
    session.add_all(airports + airlines)
    session.flush()

    flights = [
        Flight(
            flight_id=1, airline_code="AA", flight_number="AA100",
            departure_airport="JFK", arrival_airport="LAX",
            departure_time=datetime(2025, 7, 15, 8, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 15, 11, 30, tzinfo=timezone.utc),
            duration_minutes=210, cabin_class="economy", base_price=300, available_seats=50,
        ),
        Flight(
            flight_id=2, airline_code="UA", flight_number="UA200",
            departure_airport="JFK", arrival_airport="LAX",
            departure_time=datetime(2025, 7, 15, 14, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 15, 17, 30, tzinfo=timezone.utc),
            duration_minutes=210, cabin_class="business", base_price=800, available_seats=20,
        ),
        Flight(
            flight_id=3, airline_code="AA", flight_number="AA101",
            departure_airport="JFK", arrival_airport="ORD",
            departure_time=datetime(2025, 7, 15, 7, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 15, 9, 0, tzinfo=timezone.utc),
            duration_minutes=120, cabin_class="economy", base_price=150, available_seats=60,
        ),
        Flight(
            flight_id=4, airline_code="UA", flight_number="UA201",
            departure_airport="ORD", arrival_airport="LAX",
            departure_time=datetime(2025, 7, 15, 10, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 15, 12, 30, tzinfo=timezone.utc),
            duration_minutes=150, cabin_class="economy", base_price=100, available_seats=40,
        ),
        Flight(
            flight_id=5, airline_code="AA", flight_number="AA300",
            departure_airport="LAX", arrival_airport="JFK",
            departure_time=datetime(2025, 7, 15, 20, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 15, 23, 30, tzinfo=timezone.utc),
            duration_minutes=210, cabin_class="first", base_price=1200, available_seats=10,
        ),
        # Flight on a different date for date-filter testing
        Flight(
            flight_id=6, airline_code="AA", flight_number="AA102",
            departure_airport="JFK", arrival_airport="LAX",
            departure_time=datetime(2025, 7, 16, 9, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 7, 16, 12, 30, tzinfo=timezone.utc),
            duration_minutes=210, cabin_class="economy", base_price=320, available_seats=45,
        ),
    ]
    session.add_all(flights)
    session.flush()

    routes = [
        Route(
            route_id=1, departure_airport="JFK", arrival_airport="LAX",
            total_duration=210, total_price=300, num_stops=0,
        ),
        Route(
            route_id=2, departure_airport="JFK", arrival_airport="LAX",
            total_duration=210, total_price=800, num_stops=0,
        ),
        Route(
            route_id=3, departure_airport="JFK", arrival_airport="LAX",
            total_duration=330, total_price=250, num_stops=1,
        ),
        Route(
            route_id=4, departure_airport="LAX", arrival_airport="JFK",
            total_duration=210, total_price=1200, num_stops=0,
        ),
        Route(
            route_id=5, departure_airport="JFK", arrival_airport="LAX",
            total_duration=210, total_price=320, num_stops=0,
        ),
    ]
    session.add_all(routes)
    session.flush()

    route_flights = [
        RouteFlight(route_id=1, flight_id=1, leg_order=1),
        RouteFlight(route_id=2, flight_id=2, leg_order=1),
        RouteFlight(route_id=3, flight_id=3, leg_order=1),
        RouteFlight(route_id=3, flight_id=4, leg_order=2),
        RouteFlight(route_id=4, flight_id=5, leg_order=1),
        RouteFlight(route_id=5, flight_id=6, leg_order=1),
    ]
    session.add_all(route_flights)
    session.commit()
