from app.db.models import Flight
from app.schemas import FlightLeg


def flight_to_leg(flight: Flight) -> FlightLeg:
    """Convert a Flight ORM model to a FlightLeg schema."""
    return FlightLeg(
        flight_number=flight.flight_number,
        airline=flight.airline.name,
        departure_airport=flight.departure_airport,
        arrival_airport=flight.arrival_airport,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        duration_minutes=flight.duration_minutes,
        cabin_class=flight.cabin_class,
    )
