import app.tools.booking  # noqa: F401
import app.tools.search  # noqa: F401
from app.server import mcp  # noqa: F401

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
