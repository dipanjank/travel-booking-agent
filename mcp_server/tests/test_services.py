from unittest.mock import patch

import pytest

from app.db.models import Flight
from app.db.repositories import BookingRepository, RouteRepository
from app.schemas import BookingRequest, FlightSearchRequest
from app.services.booking import BookingService
from app.services.search import FlightSearchService


class TestFlightSearchService:
    """Tests for FlightSearchService.search."""

    def test_search_returns_results(self, session, seed_data):
        """Return FlightSearchResult schemas for matching routes."""
        repo = RouteRepository(session)
        service = FlightSearchService(repo)
        results = service.search(FlightSearchRequest(origin="JFK", destination="LAX"))
        assert len(results) == 4
        assert all(r.route_id is not None for r in results)

    def test_search_result_fields(self, session, seed_data):
        """Verify that search results contain correct fields from the route and flight data."""
        repo = RouteRepository(session)
        service = FlightSearchService(repo)
        results = service.search(FlightSearchRequest(origin="JFK", destination="LAX", max_stops=0, max_price=300))
        assert len(results) == 1
        result = results[0]
        assert result.route_id == 1
        assert result.total_duration_minutes == 210
        assert result.num_stops == 0
        assert result.total_price == 300.0

    def test_search_result_legs(self, session, seed_data):
        """Verify that flight legs are correctly populated."""
        repo = RouteRepository(session)
        service = FlightSearchService(repo)
        results = service.search(FlightSearchRequest(origin="JFK", destination="LAX", max_stops=0, max_price=300))
        leg = results[0].legs[0]
        assert leg.flight_number == "AA100"
        assert leg.airline == "American Airlines"
        assert leg.departure_airport == "JFK"
        assert leg.arrival_airport == "LAX"
        assert leg.duration_minutes == 210
        assert leg.cabin_class == "economy"

    def test_search_multi_leg_route(self, session, seed_data):
        """Verify that a connecting route returns multiple legs in order."""
        repo = RouteRepository(session)
        service = FlightSearchService(repo)
        results = service.search(FlightSearchRequest(origin="JFK", destination="LAX", max_stops=1, max_price=250))
        connecting = [r for r in results if r.num_stops == 1]
        assert len(connecting) == 1
        legs = connecting[0].legs
        assert len(legs) == 2
        assert legs[0].departure_airport == "JFK"
        assert legs[0].arrival_airport == "ORD"
        assert legs[1].departure_airport == "ORD"
        assert legs[1].arrival_airport == "LAX"

    def test_search_empty_results(self, session, seed_data):
        """Return empty list when no routes match."""
        repo = RouteRepository(session)
        service = FlightSearchService(repo)
        results = service.search(FlightSearchRequest(origin="ORD", destination="JFK"))
        assert results == []


class TestBookingService:
    """Tests for BookingService.book."""

    def _make_request(self, route_id=1):
        """Build a valid BookingRequest."""
        return BookingRequest(
            route_id=route_id,
            user_id="test-user-id",
        )

    def test_book_returns_confirmation(self, session, seed_data):
        """Return a BookingConfirmation with a PNR and correct route."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        confirmation = service.book(self._make_request())
        assert len(confirmation.pnr) == 6
        assert confirmation.route_id == 1
        assert confirmation.status == "CONFIRMED"
        assert confirmation.total_price == 300.0

    def test_book_includes_legs(self, session, seed_data):
        """Verify the confirmation includes flight leg details."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        confirmation = service.book(self._make_request())
        assert len(confirmation.legs) == 1
        assert confirmation.legs[0].flight_number == "AA100"

    def test_book_connecting_route(self, session, seed_data):
        """Book a connecting route and verify both legs appear."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        confirmation = service.book(self._make_request(route_id=3))
        assert len(confirmation.legs) == 2
        assert confirmation.total_price == 250.0

    def test_book_invalid_route(self, session, seed_data):
        """Raise when booking a nonexistent route."""
        from sqlalchemy.exc import NoResultFound

        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        with pytest.raises(NoResultFound):
            service.book(self._make_request(route_id=999))

    def test_book_decrements_available_seats(self, session, seed_data):
        """Booking reduces available_seats on each flight in the route by 1."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        flight_before = session.query(Flight).filter(Flight.flight_id == 1).one()
        seats_before = flight_before.available_seats
        service.book(self._make_request())
        session.expire_all()
        flight_after = session.query(Flight).filter(Flight.flight_id == 1).one()
        assert flight_after.available_seats == seats_before - 1

    def test_book_no_seats(self, session, seed_data):
        """Raise ValueError when a flight has zero available seats."""
        flight = session.query(Flight).filter(Flight.flight_id == 1).one()
        flight.available_seats = 0
        session.commit()
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        with pytest.raises(ValueError, match="0 seat"):
            service.book(self._make_request())

    def test_book_connecting_route_decrements_all_legs(self, session, seed_data):
        """Booking a connecting route decrements seats on every leg."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        f3_before = session.query(Flight).filter(Flight.flight_id == 3).one().available_seats
        f4_before = session.query(Flight).filter(Flight.flight_id == 4).one().available_seats
        service.book(self._make_request(route_id=3))
        session.expire_all()
        assert session.query(Flight).filter(Flight.flight_id == 3).one().available_seats == f3_before - 1
        assert session.query(Flight).filter(Flight.flight_id == 4).one().available_seats == f4_before - 1

    def test_pnr_uniqueness(self, session, seed_data):
        """Each booking gets a distinct PNR."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)
        pnr1 = service.book(self._make_request()).pnr
        pnr2 = service.book(self._make_request()).pnr
        assert pnr1 != pnr2

    def test_pnr_retry_on_collision(self, session, seed_data):
        """Retry PNR generation when a collision occurs."""
        route_repo = RouteRepository(session)
        booking_repo = BookingRepository(session)
        service = BookingService(route_repo, booking_repo, session)

        with patch("app.services.booking.random.choices") as mock_choices:
            mock_choices.side_effect = [
                list("AAAAAA"),  # first booking
                list("AAAAAA"),  # collision
                list("BBBBBB"),  # retry succeeds
            ]
            pnr1 = service.book(self._make_request()).pnr
            assert pnr1 == "AAAAAA"
            pnr2 = service.book(self._make_request()).pnr
            assert pnr2 == "BBBBBB"
