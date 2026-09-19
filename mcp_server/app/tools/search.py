from app.db.engine import SessionLocal
from app.db.repositories import RouteRepository
from app.schemas import FlightSearchRequest, FlightSearchResult
from app.server import mcp
from app.services.search import FlightSearchService


@mcp.tool
def search_flights(request: FlightSearchRequest) -> list[FlightSearchResult]:
    """Search available flights between two airports."""
    with SessionLocal() as session:
        service = FlightSearchService(route_repo=RouteRepository(session))
        return service.search(request)
