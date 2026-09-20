locals {
  aws_region               = "eu-west-1"
  project_name             = "travel-booking"
  mcp_server_image_version = "0.1.0"

  tags = {
    Project        = local.project_name
    ManagedBy      = "terraform"
    RepositoryName = "travel-booking-agent"
  }
}
