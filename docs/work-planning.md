# Work Planning

## Epic: MCP Server

### Story 1: Bootstrap `booking-mcp-server` Application

Set up the foundational python FastMCP project in the `booking-mcp-server`.

- [x] Scaffold python 3.14 Application with `pyproject.toml`
- [x] Setup Docker Build

### Story 2: Implement tools

Implement tools exposed by the MCP server.

- [x] Implement search_flights tool
- [x] Implement book_flight tool
- [x] Add pytest tests

## Epic: Conversational Booking Agent

Build the conversational QA app that lets users search and book flights via natural language, backed by a LangGraph ReAct agent calling MCP tools.

### Story 1: Bootstrap Backend (`backend/`)

Set up the foundational FastAPI project in `backend/`.

- [x] Scaffold `backend/booking_agent/` package with `__init__.py`, `main.py` (FastAPI entry point), and `schemas.py` (ChatRequest, ChatResponse)
- [x] Add backend dependencies to `pyproject.toml` (fastapi, uvicorn, langgraph, langchain-aws, langchain-mcp-adapters, httpx, boto3)
- [x] Setup Docker build (`backend/Dockerfile`)

### Story 2: Authentication & User Management

As a user, I can log in with a username and password so that I can access the chat interface. My session stays alive transparently via token refresh, and I can log out when done. Unauthenticated requests are rejected. As an admin, I can create, list, and delete users with role-based access control. JWT-based, database-backed, same pattern as `knowledge-base-qa-webapp`.

**Subtask 2.1 — Database layer and User model**
- [x] Add database dependencies to `pyproject.toml` (`sqlalchemy`, `pydantic-settings`)
- [x] Implement `database.py` with sync SQLAlchemy engine, `SessionLocal`, `Base`, and `get_db` generator
- [x] Implement `models/user.py` with `User` ORM model (UUID PK, username, email, password_hash, role with CHECK constraint, timestamps)
- [x] Add `Settings` via `pydantic-settings` for `JWT_SECRET`, `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, token expiry settings

**Subtask 2.2 — Auth utilities, schemas, and repositories**
- [x] Add auth dependencies to `pyproject.toml` (`python-jose[cryptography]`, `bcrypt`)
- [x] Implement `utils/auth.py`: `hash_password`, `verify_password` (bcrypt, 12 rounds), `create_access_token` (30 min, HS256), `create_refresh_token` (7 days, HS256), `decode_token`, `generate_password`
- [x] Implement `schemas/auth.py`: `LoginRequest`, `TokenResponse`
- [x] Implement `schemas/user.py`: `CreateUserRequest`, `CreateUserResponse`, `UserResponse`, `UserListResponse`, `MessageResponse`
- [x] Implement `repositories/base.py` with `GenericRepository[T]` (sync CRUD)
- [x] Implement `repositories/user_repository.py` with `UserRepository` extending `GenericRepository[User]`

**Subtask 2.3 — Services and endpoints**
- [x] Implement `services/auth_service.py` with `AuthService` (login, refresh — validates against DB)
- [x] Implement `services/admin_service.py` with `AdminService` (create_user with random password, list_users, delete_user)
- [x] `POST /api/auth/login` — validate credentials against DB, return access token in body, set refresh token as HttpOnly cookie
- [x] `POST /api/auth/refresh` — decode refresh token from cookie, look up user in DB, issue new tokens
- [x] `POST /api/auth/logout` — delete refresh token cookie
- [x] `POST /api/admin/users` — create user (admin only), return one-time password
- [x] `GET /api/admin/users` — list all users (admin only)
- [x] `DELETE /api/admin/users/{user_id}` — delete user (admin only, cannot delete admins)

**Subtask 2.4 — Endpoint protection and dependency injection**
- [x] Implement `dependencies.py` with `get_current_user` (decodes Bearer token, looks up User in DB), `require_admin` (checks ADMIN_USER role), `get_refresh_token`
- [x] Guard admin endpoints with `Depends(require_admin)`

**Subtask 2.5 — Admin user seeding**
- [x] On startup, create tables via `Base.metadata.create_all(engine)`
- [x] Seed admin user from `ADMIN_USERNAME` / `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars if no ADMIN_USER exists in DB

### Story 3: MCP Client Integration

Connect the backend to the MCP server using `langchain-mcp-adapters`.

- [ ] Implement `mcp_client.py` with `MultiServerMCPClient` configured for Streamable HTTP transport
- [ ] Load `search_flights` and `book_flight` as LangChain tools

### Story 4: LangGraph ReAct Agent

Set up the conversational agent that handles multi-turn flight search and booking.

- [ ] Implement `agent.py` with `create_react_agent` using `ChatBedrockConverse` (Claude Sonnet via Bedrock) and MCP tools
- [ ] Configure PostgreSQL-backed conversation checkpointing (`PostgresSaver`)
- [ ] Wire agent invocation into `POST /chat` endpoint with session-based `thread_id`

### Story 5: Bootstrap Frontend (`frontend/`)

Set up the SvelteKit project for the chat UI.

- [ ] Scaffold SvelteKit app in `frontend/` with TypeScript
- [ ] Setup Docker build (`frontend/Dockerfile`)

### Story 6: Chat UI

Build the chat interface in SvelteKit.

- [ ] Create auth store (Svelte writable) to hold access token and auth state
- [ ] Create API wrapper (`lib/api.ts`) that attaches `Authorization: Bearer <token>`, sends `credentials: 'include'`, and auto-refreshes via `POST /api/auth/refresh` on 401
- [ ] Create login page that authenticates against `POST /api/auth/login` and stores access token
- [ ] Create chat page with message input and conversation history
- [ ] Add layout-level route guard to redirect unauthenticated users to `/login`

### Story 7: Add Tests

- [ ] Add pytest tests for authentication (login, session validation, protected endpoint rejection)
- [ ] Add pytest tests for the chat endpoint (mocked agent)
- [ ] Add frontend tests (Vitest/Playwright)

## Epic: Bootstrap Infrastructure

Set up the foundational AWS infrastructure in **eu-west-1** required to deploy the travel booking agent.

### Story 1: Terraform State and Deployment Role

As a developer, I can store Terraform state remotely and deploy infrastructure via GitHub Actions.

- [x] Create an S3 bucket for Terraform remote state with versioning and encryption enabled.
- [x] Create an IAM deployment role that Terraform will assume to provision resources.

### Story 2: ECR Repositories

As a developer, I can push container images to ECR for each service.

- [x] **Subtask 2.1:** Create ECR repository for `travel-booking-app-backend`.
- [ ] **Subtask 2.2:** Create ECR repository for `travel-booking-app-frontend`.
- [x] **Subtask 2.3:** Create ECR repository for `booking-mcp-server`.

### Story 3: VPC and Subnets

As a developer, I can deploy services into a VPC with public and private subnets, with network configuration stored in SSM Parameter Store.

- [x] Create a VPC with public and private subnets across availability zones.
- [x] Store the following in SSM Parameter Store:
  - VPC CIDR and VPC ID
  - Public subnet CIDRs and IDs
  - Private subnet CIDRs and IDs

### Story 4: Public ALB

As a developer, I can route internet traffic to the QA app through a public Application Load Balancer, with its DNS name stored in SSM Parameter Store.

- [x] Create an internet-facing Application Load Balancer in the public subnets.
- [x] Configure security group to allow inbound HTTPS from the internet.
- [x] Store the ALB DNS name in SSM Parameter Store.

### Story 5: Private RDS Database

As a developer, I can connect the MCP server to a private PostgreSQL database, with connection parameters stored in SSM Parameter Store.

- [x] Create a PostgreSQL RDS instance in the private subnets.
- [x] Configure security group to allow inbound on port 5432 from the MCP Server and QA App Backend security groups.
- [x] Store the following in SSM Parameter Store:
  - Database endpoint
  - Database port
  - Database name

### Story 6: ECS Cluster

As a developer, I have a shared ECS cluster to deploy all services into.

- [x] Create an ECS cluster with Fargate capacity providers
- [x] Store cluster ARN and name in SSM Parameter Store

### Story 7: ECS Service for MCP Server

As a developer, I can deploy the MCP server as a Fargate service behind the ALB, reachable at `/book-mcp-server`.

- [x] Create ECS task definition for `booking-mcp-server` (Fargate, image from ECR, port 8001)
- [x] Inject database credentials from Secrets Manager as environment variables
- [x] Create ECS service in private subnets
- [x] Configure security group: allow inbound on port 8001 from the ALB security group, allow outbound to RDS on port 5432
- [x] Create ALB target group and listener rule to route `/book-mcp-server/*` to the MCP server service

### Story 8: ECS Service for QA App Backend

As a developer, I can deploy the QA app backend as a Fargate service behind the ALB.

- [ ] Create ECS task definition for `qa-app-backend` (Fargate, image from ECR, port 8000)
- [ ] Inject environment variables (JWT secret, admin credentials, database URL from Secrets Manager, MCP server URL via ALB)
- [ ] Create ECS service in public subnets
- [ ] Configure security group: allow inbound on port 8000 from the ALB security group, allow outbound to MCP server on port 8001 and to RDS on port 5432
- [ ] Create ALB target group and listener rule to route `/api/*` to the backend service

### Story 9: ECS Service for QA App Frontend

As a developer, I can deploy the QA app frontend as a Fargate service behind the ALB.

- [ ] Create ECS task definition for `qa-app-frontend` (Fargate, image from ECR, port 3000)
- [ ] Create ECS service in public subnets
- [ ] Configure security group: allow inbound on port 3000 from the ALB security group
- [ ] Create ALB target group and listener rule to route `/*` (default) to the frontend service

---

## Epic: GitHub Workflows

Set up CI/CD pipelines using GitHub Actions for infrastructure deployment and container image builds.

### Story 1: Terraform Deployment Workflow

As a developer, I can automatically plan and apply Terraform changes through a GitHub Actions workflow.

- [x] Create a GitHub Actions workflow to plan and apply Terraform changes.

### Story 2: MCP Server ECR Image Build and Push Workflow

As a developer, I can automatically build and push the MCP server image to ECR on code changes.

- [x] Create a GitHub Actions workflow to build and push the `booking-mcp-server` image to ECR.

### Story 3: QA App Image Build and Push Workflows

As a developer, I can automatically build and push the QA app images to ECR on code changes.

- [ ] Create a GitHub Actions workflow to build and push the QA app frontend image to ECR.
- [x] Create a GitHub Actions workflow to build and push the QA app backend image to ECR.

### Story 4: Python Pre-commit and Pytest Workflow

As a developer, I can automatically run pre-commit checks and pytest on pull requests to catch lint and test failures before merge.

- [x] Create a GitHub Actions workflow that runs pre-commit hooks (ruff lint/format) on Python files.
- [x] Add a pytest step to the workflow that runs the test suite against an in-memory SQLite database.
