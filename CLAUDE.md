# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Travel booking agent — two-service system for flight search/booking via natural language conversation.

- **MCP Server** (`mcp_server/`): Built with fastMCP, exposes `search_flights` and `book_flight` tools over Streamable HTTP. Connects to PostgreSQL.
- **QA App** (`backend/`): FastAPI web server with a LangGraph ReAct agent that calls MCP tools. Serves the chat interface.
- **Database**: PostgreSQL (RDS). Accessed only by the MCP server.

## Tech Stack

- Python, FastAPI, uvicorn
- fastMCP (MCP server), langchain-mcp-adapters (MCP client)
- LangGraph + langchain-anthropic (conversational agent)
- SQLAlchemy 2.0 + psycopg2 (database), Alembic (migrations)
- AWS: ECS Fargate, RDS PostgreSQL, Secrets Manager, ECR

## Architecture

```
User -> ALB -> QA App (FastAPI + LangGraph) -> MCP Server (fastMCP) -> PostgreSQL (RDS)
```

QA App authenticates users with username/password. MCP Server has no authentication (planned for later). DB credentials stored in Secrets Manager.

## Development Environment

- **IDE:** PyCharm
- **Git branching:** feature branches off `main`

## Key Documentation

- `docs/requirements.md` — functional requirements
- `docs/system-design.md` — full system design, schema, deployment architecture
