from datetime import date

import pytest

from app.db.models import Flight
from app.db.repositories import BookingRepository, RouteRepository
from app.schemas import FlightSearchRequest


class TestRouteRepositorySearch:
    """Tests for RouteRepository.search with all filter combinations."""

    def test_search_by_origin_destination(self, session, seed_data):
        """Return all JFK->LAX routes when no optional filters are set."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX")
        results = repo.search(request)
        assert len(results) == 4
        assert all(r.departure_airport == "JFK" and r.arrival_airport == "LAX" for r in results)

    def test_search_no_results(self, session, seed_data):
        """Return empty list when no routes match the origin/destination."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="ORD", destination="LAX")
        results = repo.search(request)
        assert results == []

    def test_search_reverse_direction(self, session, seed_data):
        """Return LAX->JFK routes, not JFK->LAX."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="LAX", destination="JFK")
        results = repo.search(request)
        assert len(results) == 1
        assert results[0].route_id == 4

    def test_filter_by_date(self, session, seed_data):
        """Return only routes whose first leg departs on the given date."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", date=date(2025, 7, 15))
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        assert route_ids == {1, 2, 3}

    def test_filter_by_date_different_day(self, session, seed_data):
        """Return only the route departing on July 16."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", date=date(2025, 7, 16))
        results = repo.search(request)
        assert len(results) == 1
        assert results[0].route_id == 5

    def test_filter_by_date_no_match(self, session, seed_data):
        """Return empty list when no routes depart on the given date."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", date=date(2025, 7, 20))
        results = repo.search(request)
        assert results == []

    def test_filter_by_time_of_day_morning(self, session, seed_data):
        """Return routes whose first leg departs between 06:00 and 12:00."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", time_of_day="morning")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 1 (08:00), Route 3 (07:00), Route 5 (09:00) — all morning
        assert route_ids == {1, 3, 5}

    def test_filter_by_time_of_day_afternoon(self, session, seed_data):
        """Return routes whose first leg departs between 12:00 and 18:00."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", time_of_day="afternoon")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 2 (14:00) — afternoon
        assert route_ids == {2}

    def test_filter_by_time_of_day_evening(self, session, seed_data):
        """Return routes whose first leg departs between 18:00 and 24:00."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="LAX", destination="JFK", time_of_day="evening")
        results = repo.search(request)
        assert len(results) == 1
        assert results[0].route_id == 4

    def test_filter_by_airline(self, session, seed_data):
        """Return routes that include at least one leg by the given airline."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", airline="UA")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 2 (UA only), Route 3 (AA+UA) — both have a UA leg
        assert route_ids == {2, 3}

    def test_filter_by_airline_aa(self, session, seed_data):
        """Return routes that include at least one leg by AA."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", airline="AA")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 1, Route 3, Route 5 — all have an AA leg
        assert route_ids == {1, 3, 5}

    def test_filter_by_airline_no_match(self, session, seed_data):
        """Return empty list when no routes include the airline."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", airline="DL")
        results = repo.search(request)
        assert results == []

    def test_filter_by_max_price(self, session, seed_data):
        """Return routes with total_price <= max_price."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", max_price=300)
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 1 ($300), Route 3 ($250)
        assert route_ids == {1, 3}

    def test_filter_by_max_price_excludes_expensive(self, session, seed_data):
        """Ensure routes above max_price are excluded."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", max_price=249)
        results = repo.search(request)
        assert results == []

    def test_filter_by_max_stops(self, session, seed_data):
        """Return routes with num_stops <= max_stops."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", max_stops=0)
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 1, Route 2, Route 5 — all direct (0 stops)
        assert route_ids == {1, 2, 5}

    def test_filter_by_max_stops_includes_connecting(self, session, seed_data):
        """Return all routes when max_stops is high enough."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", max_stops=1)
        results = repo.search(request)
        assert len(results) == 4

    def test_filter_by_cabin_class_economy(self, session, seed_data):
        """Return routes that include at least one economy-class leg."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", cabin_class="economy")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Route 1, Route 3, Route 5 — have economy legs
        assert route_ids == {1, 3, 5}

    def test_filter_by_cabin_class_business(self, session, seed_data):
        """Return routes that include at least one business-class leg."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", cabin_class="business")
        results = repo.search(request)
        assert len(results) == 1
        assert results[0].route_id == 2

    def test_filter_by_cabin_class_first(self, session, seed_data):
        """Return routes that include at least one first-class leg."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="LAX", destination="JFK", cabin_class="first")
        results = repo.search(request)
        assert len(results) == 1
        assert results[0].route_id == 4

    def test_combined_date_and_max_price(self, session, seed_data):
        """Combine date and max_price filters."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", date=date(2025, 7, 15), max_price=500)
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # July 15: routes 1,2,3. Price <= 500: routes 1 ($300), 3 ($250)
        assert route_ids == {1, 3}

    def test_combined_time_of_day_and_airline(self, session, seed_data):
        """Combine time_of_day and airline filters."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", time_of_day="morning", airline="UA")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Morning routes: 1,3,5. UA routes: 2,3. Intersection: {3}
        assert route_ids == {3}

    def test_combined_max_stops_and_cabin_class(self, session, seed_data):
        """Combine max_stops and cabin_class filters."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX", max_stops=0, cabin_class="economy")
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Direct: 1,2,5. Economy: 1,3,5. Intersection: {1, 5}
        assert route_ids == {1, 5}

    def test_combined_all_filters(self, session, seed_data):
        """Apply all filters simultaneously."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(
            origin="JFK", destination="LAX",
            date=date(2025, 7, 15), time_of_day="morning",
            airline="AA", max_price=500, max_stops=0, cabin_class="economy",
        )
        results = repo.search(request)
        route_ids = {r.route_id for r in results}
        # Only Route 1 matches all: July 15, 08:00 (morning), AA, $300, direct, economy
        assert route_ids == {1}

    def test_excludes_sold_out_direct_route(self, session, seed_data):
        """Exclude a direct route when its flight has no available seats."""
        flight = session.query(Flight).filter(Flight.flight_id == 1).one()
        flight.available_seats = 0
        session.commit()
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX")
        route_ids = {r.route_id for r in repo.search(request)}
        assert 1 not in route_ids
        assert route_ids == {2, 3, 5}

    def test_excludes_connecting_route_with_sold_out_leg(self, session, seed_data):
        """Exclude a connecting route when any leg has no available seats."""
        flight = session.query(Flight).filter(Flight.flight_id == 4).one()
        flight.available_seats = 0
        session.commit()
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX")
        route_ids = {r.route_id for r in repo.search(request)}
        # Route 3 (JFK->ORD->LAX) excluded because leg 2 (flight 4) is sold out
        assert 3 not in route_ids

    def test_includes_route_with_available_seats(self, session, seed_data):
        """Include routes where all flights have available seats."""
        repo = RouteRepository(session)
        request = FlightSearchRequest(origin="JFK", destination="LAX")
        results = repo.search(request)
        assert len(results) == 4


class TestRouteRepositoryGetById:
    """Tests for RouteRepository.get_by_id."""

    def test_get_by_id(self, session, seed_data):
        """Return the route with the given ID."""
        repo = RouteRepository(session)
        route = repo.get_by_id(1)
        assert route.route_id == 1
        assert route.departure_airport == "JFK"

    def test_get_by_id_not_found(self, session, seed_data):
        """Raise when the route ID does not exist."""
        from sqlalchemy.exc import NoResultFound

        repo = RouteRepository(session)
        with pytest.raises(NoResultFound):
            repo.get_by_id(999)


class TestBookingRepository:
    """Tests for BookingRepository."""

    def test_pnr_exists_false(self, session, seed_data):
        """Return False when no booking has the given PNR."""
        repo = BookingRepository(session)
        assert repo.pnr_exists("XXXXXX") is False

    def test_create_booking(self, session, seed_data):
        """Create a booking and return it with an assigned ID."""
        repo = BookingRepository(session)
        booking = repo.create(pnr="ABC123", route_id=1, user_id="test-user-id")
        assert booking.booking_id is not None
        assert booking.pnr == "ABC123"
        assert booking.route_id == 1

    def test_pnr_exists_true(self, session, seed_data):
        """Return True after a booking with that PNR has been created."""
        repo = BookingRepository(session)
        repo.create(pnr="ABC123", route_id=1, user_id="test-user-id")
        assert repo.pnr_exists("ABC123") is True
