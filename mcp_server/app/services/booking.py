import random

from sqlalchemy.orm import Session

from app.db.repositories import BookingRepository, RouteRepository
from app.schemas import BookingConfirmation, BookingRequest, PassengerDetails
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
        """Create a booking with passengers for the given route and return a confirmation."""
        route = self._route_repo.get_by_id(request.route_id)
        num_passengers = len(request.passengers)

        for rf in route.route_flights:
            if rf.flight.available_seats < num_passengers:
                raise ValueError(
                    f"Flight {rf.flight.flight_number} has {rf.flight.available_seats} seat(s) "
                    f"but {num_passengers} requested"
                )

        for rf in route.route_flights:
            rf.flight.available_seats -= num_passengers

        pnr = self._generate_pnr()

        booking = self._booking_repo.create(
            pnr=pnr,
            route_id=request.route_id,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
        )

        for p in request.passengers:
            self._booking_repo.add_passenger(
                booking_id=booking.booking_id,
                name=p.name,
                date_of_birth=p.date_of_birth,
                passport_number=p.passport_number,
            )

        self._session.commit()
        self._session.refresh(booking)

        legs = [flight_to_leg(rf.flight) for rf in route.route_flights]

        return BookingConfirmation(
            pnr=booking.pnr,
            route_id=route.route_id,
            legs=legs,
            passengers=[
                PassengerDetails(name=p.name, date_of_birth=p.date_of_birth, passport_number=p.passport_number)
                for p in booking.passengers
            ],
            total_price=float(route.total_price),
            status=booking.status,
            booked_at=booking.booked_at,
        )
