# Work Planning

## Epic: Bootstrap Infrastructure

Set up the foundational AWS infrastructure in **eu-west-1** required to deploy the travel booking agent.

### Story 1: Create Terraform State Bucket and Deployment Role

- [ ] Create an S3 bucket for Terraform remote state with versioning and encryption enabled.
- [ ] Create a DynamoDB table for state locking.
- [ ] Create an IAM deployment role that Terraform will assume to provision resources.

### Story 2: Create ECR Repositories

Create one ECR repository per container image:

- [ ] **Subtask 2.1:** Create ECR repository for `travel-booking-app`.
- [ ] **Subtask 2.2:** Create ECR repository for `booking-mcp-server`.

### Story 3: Create VPC and Subnets

- [ ] Create a VPC with public and private subnets across availability zones.
- [ ] Store the following in SSM Parameter Store:
  - VPC CIDR and VPC ID
  - Public subnet CIDRs and IDs
  - Private subnet CIDRs and IDs

### Story 4: Create Public ALB

- [ ] Create an internet-facing Application Load Balancer in the public subnets.
- [ ] Configure security group to allow inbound HTTPS from the internet.
- [ ] Store the ALB DNS name in SSM Parameter Store.

### Story 5: Create Private RDS Database

- [ ] Create a PostgreSQL RDS instance in the private subnets.
- [ ] Configure security group to allow inbound on port 5432 only from the MCP Server security group.
- [ ] Store the following in SSM Parameter Store:
  - Database endpoint
  - Database port
  - Database name

---

## Epic: GitHub Workflows

Set up CI/CD pipelines using GitHub Actions for infrastructure deployment and container image builds.

### Story 1: Terraform Deployment Workflow

- [ ] Create a GitHub Actions workflow to plan and apply Terraform changes.

### Story 2: MCP Server ECR Image Build and Push Workflow

- [ ] Create a GitHub Actions workflow to build and push the `booking-mcp-server` image to ECR.

### Story 3: QA App Image Build and Push Workflows

- [ ] Create a GitHub Actions workflow to build and push the QA app frontend image to ECR.
- [ ] Create a GitHub Actions workflow to build and push the QA app backend image to ECR.
