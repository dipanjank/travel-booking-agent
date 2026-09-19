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

## CI/CD

The Terraform workflow (`.github/workflows/terraform.yml`) runs on changes to the `terraform/` directory:

- **All branches**: `fmt -check`, `init`, `validate`, `plan` (plan output is posted as a PR comment)
- **Main branch only**: `terraform apply -auto-approve` using the saved plan

Authentication uses OIDC — no static AWS credentials are stored in GitHub.
