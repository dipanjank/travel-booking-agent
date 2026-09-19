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

### SSM Parameters (`ssm.tf`)

Network configuration stored in SSM Parameter Store:

| Parameter                                 | Type       |
|-------------------------------------------|------------|
| `/${project_name}/vpc/id`                 | String     |
| `/${project_name}/vpc/cidr`               | String     |
| `/${project_name}/vpc/public-subnet-ids`  | StringList |
| `/${project_name}/vpc/private-subnet-ids` | StringList |

### ECR Repositories (`ecr.tf`)

Container registries for application images:

| Repository           | Description        |
|----------------------|--------------------|
| `travel-booking-app` | QA app service     |
| `booking-mcp-server` | MCP server service |

All repositories have mutable tags, force delete enabled, and a lifecycle policy that keeps the last 5 images.

## Variables

| Name           | Description                | Default            |
|----------------|----------------------------|--------------------|
| `aws_region`   | AWS region                 | `eu-west-1`        |
| `project_name` | Project name for resources | `travel-booking`   |

## Outputs

| Name                  | Description                               |
|-----------------------|-------------------------------------------|
| `state_bucket_name`   | Name of the S3 state bucket               |
| `state_bucket_arn`    | ARN of the S3 state bucket                |
| `deployment_role_arn` | ARN of the GitHub Actions deployment role |
| `vpc_id`              | ID of the VPC                             |
| `public_subnet_ids`   | IDs of the public subnets                 |
| `private_subnet_ids`  | IDs of the private subnets                |

## CI/CD

The Terraform workflow (`.github/workflows/terraform.yml`) runs on changes to the `terraform/` directory:

- **All branches**: `fmt -check`, `init`, `validate`, `plan` (plan output is posted as a PR comment)
- **Main branch only**: `terraform apply -auto-approve` using the saved plan

Authentication uses OIDC — no static AWS credentials are stored in GitHub.
