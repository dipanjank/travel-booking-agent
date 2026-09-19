# Work Planning

## Epic: MCP Server

### Story 1: Bootstrap `booking-mcp-server` Application

Set up the foundational python FastMCP project in the `booking-mcp-server`.

- [x] Scaffold python 3.14 Application with `pyproject.toml`
- [x] Setup Docker Build

### Story 2: Bootstrap `booking-mcp-server` Application

Implement tools exposed by the MCP server.

- [x] Implement search_flights tool
- [x] Implement book_flight tool
- [x] Add pytest tests

## Epic: Bootstrap Infrastructure

Set up the foundational AWS infrastructure in **eu-west-1** required to deploy the travel booking agent.

### Story 1: Terraform State and Deployment Role

As a developer, I can store Terraform state remotely and deploy infrastructure via GitHub Actions.

- [x] Create an S3 bucket for Terraform remote state with versioning and encryption enabled.
- [x] Create an IAM deployment role that Terraform will assume to provision resources.

### Story 2: ECR Repositories

As a developer, I can push container images to ECR for each service.

- [x] **Subtask 2.1:** Create ECR repository for `travel-booking-app`.
- [x] **Subtask 2.2:** Create ECR repository for `booking-mcp-server`.

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
- [x] Configure security group to allow inbound on port 5432 only from the MCP Server security group.
- [x] Store the following in SSM Parameter Store:
  - Database endpoint
  - Database port
  - Database name

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
- [ ] Create a GitHub Actions workflow to build and push the QA app backend image to ECR.

### Story 4: Python Pre-commit and Pytest Workflow

As a developer, I can automatically run pre-commit checks and pytest on pull requests to catch lint and test failures before merge.

- [x] Create a GitHub Actions workflow that runs pre-commit hooks (ruff lint/format) on Python files.
- [x] Add a pytest step to the workflow that runs the test suite against an in-memory SQLite database.
