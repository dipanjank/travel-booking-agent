locals {
  tags = {
    Project        = var.project_name
    ManagedBy      = "terraform"
    RepositoryName = "travel-booking-agent"
  }
}
