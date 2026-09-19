from app.db.engine import SessionLocal
from app.db.repositories import BookingRepository, RouteRepository
from app.schemas import BookingConfirmation, BookingRequest
from app.server import mcp
from app.services.booking import BookingService


@mcp.tool
def book_flight(request: BookingRequest) -> BookingConfirmation:
    """Book a flight for one or more passengers. Returns PNR and itinerary."""
    with SessionLocal() as session:
        service = BookingService(
            route_repo=RouteRepository(session),
            booking_repo=BookingRepository(session),
            session=session,
        )
        return service.book(request)
