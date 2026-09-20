from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

mcp = FastMCP("TravelBookingServer")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    """Health check endpoint for ALB target group."""
    return JSONResponse({"status": "ok"})
