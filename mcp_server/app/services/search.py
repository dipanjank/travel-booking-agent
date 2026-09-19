from app.db.models import Flight, Route
from app.db.repositories import RouteRepository
from app.schemas import FlightLeg, FlightSearchRequest, FlightSearchResult


def _flight_to_leg(flight: Flight) -> FlightLeg:
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


def _route_to_result(route: Route) -> FlightSearchResult:
    """Convert a Route ORM model (with its flight legs) to a FlightSearchResult schema."""
    return FlightSearchResult(
        route_id=route.route_id,
        legs=[_flight_to_leg(rf.flight) for rf in route.route_flights],
        total_duration_minutes=route.total_duration,
        num_stops=route.num_stops,
        total_price=float(route.total_price),
    )


class FlightSearchService:
    """Searches for flight routes matching user criteria."""

    def __init__(self, route_repo: RouteRepository):
        """Initialise with an injected RouteRepository."""
        self._route_repo = route_repo

    def search(self, request: FlightSearchRequest) -> list[FlightSearchResult]:
        """Return flight search results matching the request filters."""
        routes = self._route_repo.search(request)
        return [_route_to_result(route) for route in routes]
