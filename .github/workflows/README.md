# GitHub Workflows

## Service Workflows

### MCP Server (`mcp-server.yml`)

Runs on pushes and pull requests to `main` when files under `mcp_server/` change.

| Job             | Description                                                                                                                                        |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| `python-checks` | Calls `python-checks.yml` — runs pre-commit hooks and pytest                                                                                       |
| `docker`        | Calls `docker-build.yml` — builds and optionally pushes the Docker image to ECR. Runs after `python-checks` passes. Only pushes on merge to `main` |

### Terraform (`terraform.yml`)

Runs on pushes and pull requests to `main` when files under `terraform/` change.

| Step            | Description                                                     |
|-----------------|-----------------------------------------------------------------|
| Format check    | `terraform fmt -check -diff`                                    |
| Init + Validate | Initialise providers and validate configuration                 |
| Plan            | Generate an execution plan. On PRs, posts the plan as a comment |
| Apply           | Applies the plan on merge to `main`                             |

Uses OIDC to assume the deployment role for AWS access.

## Reusable Workflows

### Python Checks (`python-checks.yml`)

Reusable workflow for Python linting and testing.

| Input            | Required | Default | Description                          |
|------------------|----------|---------|--------------------------------------|
| `directory`      | yes      | —       | Folder containing the Python project |
| `python-version` | no       | `3.14`  | Python version to use                |

**Jobs:**

- **pre-commit** — runs all pre-commit hooks defined in `.pre-commit-config.yaml`
- **pytest** — installs the project with dev dependencies and runs `pytest tests/ -v`

### Docker Build (`docker-build.yml`)

Reusable workflow for building Docker images and pushing to ECR.

| Input            | Required | Default | Description                        |
|------------------|----------|---------|------------------------------------|
| `directory`      | yes      | —       | Folder containing the Dockerfile   |
| `ecr-repo`       | yes      | —       | ECR repository name                |
| `aws-region`     | yes      | —       | AWS region                         |
| `role-to-assume` | yes      | —       | IAM role ARN for AWS credentials   |
| `publish`        | yes      | —       | Push image to ECR (`true`/`false`) |

When `publish` is `false`, the image is built locally to validate the Dockerfile. When `true`, it logs into ECR via OIDC, builds, and pushes with the tag read from the `VERSION` file in the directory.
