# Terraform — Travel Booking Infrastructure

AWS infrastructure for the travel booking agent.

## Prerequisites

- Terraform >= 1.5
- AWS provider ~> 6.0
- AWS credentials with sufficient permissions

## State Management

State is stored remotely in S3:

| Setting | Value                          |
|---------|--------------------------------|
| Bucket  | `travel-booking-tfstate-v1`    |
| Key     | `statefiles/terraform.tfstate` |
| Region  | `eu-west-1`                    |

The state bucket is itself managed by Terraform (`state_bucket.tf`) with versioning enabled and all public access blocked.

## Resources

### State Bucket (`state_bucket.tf`)

S3 bucket for Terraform remote state, created using [`terraform-aws-modules/s3-bucket/aws`](https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws) 5.15.4. Versioning enabled, all public access blocked.

### GitHub OIDC (`oidc_github.tf`)

Keyless authentication for GitHub Actions via OIDC federation:

- **OIDC Provider** — `token.actions.githubusercontent.com`
- **Deployment Role** — `travel-booking-deployment-role` with `AdministratorAccess`
- **Trust Policy** — scoped to the `dipanjank/travel-booking-agent` repository (owner and repo IDs in the subject claim)

### VPC (`vpc.tf`)

Two-tier network using [`terraform-aws-modules/vpc/aws`](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws) ~> 5.0:

| Subnet tier | CIDRs                          | Purpose           |
|-------------|--------------------------------|-------------------|
| Public      | `10.0.1.0/24`, `10.0.2.0/24`   | ALB               |
| Private     | `10.0.10.0/24`, `10.0.11.0/24` | ECS services, RDS |

Two AZs (`eu-west-1a`, `eu-west-1b`), single NAT gateway, DNS enabled.

### Public ALB (`alb.tf`)

Internet-facing Application Load Balancer in the public subnets:

- **Security Group** — allows inbound HTTP (80) and HTTPS (443) from anywhere
- **HTTP Listener** — port 80, default action forwards to the frontend target group. Path-based rules route `/api/*` and `/mcp` to their respective backend services

### Private RDS Database (`rds.tf`)

PostgreSQL database using [`terraform-aws-modules/rds/aws`](https://registry.terraform.io/modules/terraform-aws-modules/rds/aws) ~> 6.0:

- **Engine** — PostgreSQL 17, `db.t4g.micro`
- **Storage** — 10 GB, auto-scaling up to 20 GB
- **Networking** — private subnets, security group allows port 5432 from VPC CIDR
- **Password** — random 24-character, stored in SSM

### ECS Cluster (`ecs.tf`)

Shared ECS cluster for all services:

- **Cluster** — `travel-booking-cluster` with Fargate and Fargate Spot capacity providers
- **Default Strategy** — Fargate with base of 1

### ECS MCP Server Service (`ecs_mcp_server.tf`)

Fargate service for the booking MCP server, deployed in private subnets behind the ALB:

- **Task** — 512 CPU / 1024 MB, image from `booking-mcp-server` ECR repo
- **Container** — port 8001, TCP health check on port 8001
- **Secrets** — `DATABASE_URL` injected from SSM (full PostgreSQL connection string)
- **Security Group** — inbound 8001 from ALB only, all outbound
- **ALB Routing** — target group on port 8001, listener rule forwarding `/mcp` (priority 100)
- **Logs** — CloudWatch log group `/ecs/travel-booking-mcp-server`, 7-day retention

### ECS QA App Backend Service (`ecs_backend.tf`)

Fargate service for the QA app backend, deployed in private subnets behind the ALB:

- **Task** — 512 CPU / 1024 MB, image from `travel-booking-app-backend` ECR repo
- **Container** — port 8000, health check on `/health`
- **Environment** — `ADMIN_USERNAME`, `ADMIN_EMAIL` as plain env vars
- **Secrets** — `DATABASE_URL`, `JWT_SECRET`, `ADMIN_PASSWORD` injected from SSM SecureString
- **Security Group** — inbound 8000 from ALB only, all outbound
- **ALB Routing** — target group on port 8000, listener rule forwarding `/api/*` (priority 200)
- **Logs** — CloudWatch log group `/ecs/travel-booking-backend`, 7-day retention

### ECS QA App Frontend Service (`ecs_frontend.tf`)

Fargate service for the QA app frontend, deployed in private subnets behind the ALB:

- **Task** — 256 CPU / 512 MB, image from `travel-booking-app-frontend` ECR repo
- **Container** — port 3000, health check on `/`
- **Security Group** — inbound 3000 from ALB only, all outbound
- **ALB Routing** — target group on port 3000, set as the listener default action (catch-all for `/*`)
- **Logs** — CloudWatch log group `/ecs/travel-booking-frontend`, 7-day retention

### SSM Parameters (`ssm.tf`)

Network, ALB, ECS, database, and backend configuration stored in SSM Parameter Store:

| Parameter                                            | Type         |
|------------------------------------------------------|--------------|
| `/${project_name}/vpc/id`                            | String       |
| `/${project_name}/vpc/cidr`                          | String       |
| `/${project_name}/vpc/public-subnet-ids`             | StringList   |
| `/${project_name}/vpc/private-subnet-ids`            | StringList   |
| `/${project_name}/alb/dns-name`                      | String       |
| `/${project_name}/alb/arn`                           | String       |
| `/${project_name}/alb/http-listener-arn`             | String       |
| `/${project_name}/alb/security-group-id`             | String       |
| `/${project_name}/ecs/cluster-arn`                   | String       |
| `/${project_name}/ecs/cluster-name`                  | String       |
| `/${project_name}/db/url`                            | SecureString |
| `/${project_name}/db/endpoint`                       | String       |
| `/${project_name}/db/port`                           | String       |
| `/${project_name}/db/name`                           | String       |
| `/${project_name}/db/username`                       | String       |
| `/${project_name}/db/password`                       | SecureString |
| `/${project_name}/backend/database-url`              | SecureString |
| `/${project_name}/backend/jwt-secret`                | SecureString |
| `/${project_name}/backend/admin-password`            | SecureString |

### ECR Repositories (`ecr.tf`)

Container registries for application images:

| Repository                     | Description        |
|--------------------------------|--------------------|
| `travel-booking-app`           | QA app backend     |
| `travel-booking-app-frontend`  | QA app frontend    |
| `booking-mcp-server`           | MCP server service |

All repositories have mutable tags, force delete enabled, and a lifecycle policy that keeps the last 5 images.

## Locals and Generated Secrets (`main.tf`)

All configuration is defined as locals (no input variables). Random passwords for the backend JWT secret and admin user are generated via `random_password` and stored in SSM.

| Name                       | Default          |
|----------------------------|------------------|
| `aws_region`               | `eu-west-1`      |
| `project_name`             | `travel-booking` |
| `mcp_server_image_version` | `0.1.0`          |
| `backend_image_version`    | `0.1.0`          |
| `frontend_image_version`   | `0.1.0`          |

## Outputs

| Name                           | Description                               |
|--------------------------------|-------------------------------------------|
| `state_bucket_name`            | Name of the S3 state bucket               |
| `state_bucket_arn`             | ARN of the S3 state bucket                |
| `deployment_role_arn`          | ARN of the GitHub Actions deployment role |
| `vpc_id`                       | ID of the VPC                             |
| `public_subnet_ids`            | IDs of the public subnets                 |
| `private_subnet_ids`           | IDs of the private subnets                |
| `alb_arn`                      | ARN of the ALB                            |
| `alb_dns_name`                 | DNS name of the ALB                       |
| `alb_http_listener_arn`        | ARN of the ALB HTTP listener              |
| `alb_security_group_id`        | ID of the ALB security group              |
| `ecs_cluster_arn`              | ARN of the ECS cluster                    |
| `ecs_cluster_name`             | Name of the ECS cluster                   |
| `rds_endpoint`                 | Endpoint of the RDS instance              |
| `rds_port`                     | Port of the RDS instance                  |
| `database_security_group_id`   | ID of the database security group         |

## CI/CD

The Terraform workflow (`.github/workflows/terraform.yml`) runs on changes to the `terraform/` directory:

- **All branches**: `fmt -check`, `init`, `validate`, `plan` (plan output is posted as a PR comment)
- **Main branch only**: `terraform apply -auto-approve` using the saved plan

Authentication uses OIDC — no static AWS credentials are stored in GitHub.
