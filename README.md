# Travel Booking Agent

Flight search and booking through natural language conversation. Two-service architecture: a conversational QA app backed by a Model Context Protocol (MCP) server that handles all flight data access.

```
User -> ALB -> QA App (FastAPI + LangGraph) -> MCP Server (fastMCP) -> PostgreSQL (RDS)
```

## Components

| Component                             | Directory            | Description                                                                           |
|---------------------------------------|----------------------|---------------------------------------------------------------------------------------|
| [MCP Server](mcp_server/README.md)    | `mcp_server/`        | fastMCP server exposing `search_flights` and `book_flight` tools over Streamable HTTP |
| QA App                                | `qa_app/`            | FastAPI web server with a LangGraph ReAct agent that calls MCP tools                  |
| [Infrastructure](terraform/README.md) | `terraform/`         | Terraform modules for AWS deployment (VPC, ECS Fargate, RDS, ALB, ECR)                |
| [CI/CD](.github/workflows/README.md)  | `.github/workflows/` | GitHub Actions workflows for linting, testing, and Docker image builds                |

## Documentation

- [Requirements](docs/requirements.md) -- functional requirements for flight search, booking, and conversational QA
- [System Design](docs/system-design.md) -- architecture, database schema, deployment topology, and authentication flow
- [Work Planning](docs/work-planning.md) -- epics, stories, and task tracking

## Tech Stack

- **Language:** Python 3.14
- **MCP Server:** fastMCP, SQLAlchemy 2.0, psycopg2
- **QA App:** FastAPI, LangGraph, langchain-anthropic, langchain-mcp-adapters
- **Database:** PostgreSQL (AWS RDS)
- **Infrastructure:** Terraform, AWS (ECS Fargate, RDS, ALB, ECR, Secrets Manager)
- **CI/CD:** GitHub Actions with OIDC-based AWS authentication
- **Linting:** ruff, pre-commit

## Development

Create a virtualenv and install dependencies for the MCP server:

```bash
cd mcp_server
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

Run pre-commit hooks:

```bash
pre-commit run --all-files
```
