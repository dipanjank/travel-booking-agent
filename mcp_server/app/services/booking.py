import random

from sqlalchemy.orm import Session

from app.db.repositories import BookingRepository, RouteRepository
from app.schemas import BookingConfirmation, BookingRequest
from app.services.converters import flight_to_leg

PNR_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class BookingService:
    """Handles flight booking creation and PNR generation."""

    def __init__(self, route_repo: RouteRepository, booking_repo: BookingRepository, session: Session):
        """Initialise with injected repositories and a session for commit control."""
        self._route_repo = route_repo
        self._booking_repo = booking_repo
        self._session = session

    def _generate_pnr(self) -> str:
        """Generate a unique 6-character alphanumeric PNR, retrying up to 10 times."""
        for _ in range(10):
            pnr = "".join(random.choices(PNR_CHARS, k=6))
            if not self._booking_repo.pnr_exists(pnr):
                return pnr
        raise RuntimeError("Failed to generate unique PNR after 10 attempts")

    def book(self, request: BookingRequest) -> BookingConfirmation:
        """Create a booking for the given route and return a confirmation."""
        route = self._route_repo.get_by_id(request.route_id)

        for rf in route.route_flights:
            if rf.flight.available_seats < 1:
                raise ValueError(
                    f"Flight {rf.flight.flight_number} has {rf.flight.available_seats} seat(s) available"
                )

        for rf in route.route_flights:
            rf.flight.available_seats -= 1

        pnr = self._generate_pnr()

        booking = self._booking_repo.create(
            pnr=pnr,
            route_id=request.route_id,
            user_id=request.user_id,
        )

        self._session.commit()
        self._session.refresh(booking)

        legs = [flight_to_leg(rf.flight) for rf in route.route_flights]

        return BookingConfirmation(
            pnr=booking.pnr,
            route_id=route.route_id,
            legs=legs,
            total_price=float(route.total_price),
            status=booking.status,
            booked_at=booking.booked_at,
        )
