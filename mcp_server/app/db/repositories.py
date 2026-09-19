from datetime import datetime, time

from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.db.models import Booking, Flight, Passenger, Route, RouteFlight
from app.schemas import FlightSearchRequest

TIME_RANGES = {
    "morning": (time(6, 0), time(12, 0)),
    "afternoon": (time(12, 0), time(18, 0)),
    "evening": (time(18, 0), time(23, 59)),
}


class RouteRepository:
    """Data access layer for routes and route search queries."""

    def __init__(self, session: Session):
        """Initialise with a SQLAlchemy session."""
        self._session = session

    def get_by_id(self, route_id: int) -> Route:
        """Return a single route by its ID, or raise NoResultFound."""
        return self._session.query(Route).filter(Route.route_id == route_id).one()

    def search(self, request: FlightSearchRequest) -> list[Route]:
        """Return routes matching the search filters (origin, destination, date, etc.)."""
        query = (
            self._session.query(Route)
            .filter(Route.departure_airport == request.origin, Route.arrival_airport == request.destination)
            .distinct()
        )
        if request.date:
            query = self._filter_by_date(query, request.date)
        if request.time_of_day:
            query = self._filter_by_time_of_day(query, request.time_of_day)
        if request.airline:
            query = self._filter_by_airline(query, request.airline)
        if request.max_price is not None:
            query = query.filter(Route.total_price <= request.max_price)
        if request.max_stops is not None:
            query = query.filter(Route.num_stops <= request.max_stops)
        if request.cabin_class:
            query = self._filter_by_cabin_class(query, request.cabin_class)
        return query.all()

    def _route_ids_by_flight(self, *filters):
        """Return a subquery of route IDs whose flights match the given filters."""
        return (
            self._session.query(RouteFlight.route_id)
            .join(Flight, RouteFlight.flight_id == Flight.flight_id)
            .filter(*filters)
        )

    def _filter_by_date(self, query, departure_date):
        """Keep routes whose first leg departs on the given date."""
        day_start = datetime.combine(departure_date, time.min)
        day_end = datetime.combine(departure_date, time.max)
        return query.filter(
            Route.route_id.in_(
                self._route_ids_by_flight(
                    RouteFlight.leg_order == 1,
                    Flight.departure_time >= day_start,
                    Flight.departure_time <= day_end,
                )
            )
        )

    def _filter_by_time_of_day(self, query, time_of_day: str):
        """Keep routes whose first leg departs within the given time-of-day window."""
        t_start, t_end = TIME_RANGES[time_of_day]
        sub = self._route_ids_by_flight(
            RouteFlight.leg_order == 1,
            extract("hour", Flight.departure_time) >= t_start.hour,
        )
        if t_end.hour != 23:
            sub = sub.filter(extract("hour", Flight.departure_time) < t_end.hour)
        return query.filter(Route.route_id.in_(sub))

    def _filter_by_airline(self, query, airline: str):
        """Keep routes that include at least one leg operated by the given airline."""
        return query.filter(
            Route.route_id.in_(
                self._route_ids_by_flight(Flight.airline_code == airline)
            )
        )

    def _filter_by_cabin_class(self, query, cabin_class: str):
        """Keep routes that include at least one leg with the given cabin class."""
        return query.filter(
            Route.route_id.in_(
                self._route_ids_by_flight(Flight.cabin_class == cabin_class)
            )
        )


class BookingRepository:
    """Data access layer for bookings and passengers."""

    def __init__(self, session: Session):
        """Initialise with a SQLAlchemy session."""
        self._session = session

    def pnr_exists(self, pnr: str) -> bool:
        """Return True if a booking with the given PNR already exists."""
        return self._session.query(Booking).filter(Booking.pnr == pnr).first() is not None

    def create(self, pnr: str, route_id: int, contact_email: str, contact_phone: str) -> Booking:
        """Insert a new booking and flush to obtain its ID."""
        booking = Booking(
            pnr=pnr,
            route_id=route_id,
            contact_email=contact_email,
            contact_phone=contact_phone,
        )
        self._session.add(booking)
        self._session.flush()
        return booking

    def add_passenger(self, booking_id: int, name: str, date_of_birth, passport_number: str) -> Passenger:
        """Add a passenger record to an existing booking."""
        passenger = Passenger(
            booking_id=booking_id,
            name=name,
            date_of_birth=date_of_birth,
            passport_number=passport_number,
        )
        self._session.add(passenger)
        return passenger
