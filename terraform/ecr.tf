resource "aws_ecr_repository" "qa_app" {
  name                 = "travel-booking-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = local.tags
}

resource "aws_ecr_lifecycle_policy" "qa_app" {
  repository = aws_ecr_repository.qa_app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "aws_ecr_repository" "mcp_server" {
  name                 = "booking-mcp-server"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = local.tags
}

resource "aws_ecr_lifecycle_policy" "mcp_server" {
  repository = aws_ecr_repository.mcp_server.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}
