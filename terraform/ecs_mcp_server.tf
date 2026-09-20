module "mcp_server_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 7.0"

  name        = "${local.project_name}-mcp-server"
  cluster_arn = aws_ecs_cluster.main.arn

  desired_count = 1

  cpu    = 512
  memory = 1024

  enable_autoscaling = false

  task_exec_ssm_param_arns = [
    aws_ssm_parameter.database_url.arn,
  ]

  container_definitions = {
    mcp-server = {
      essential = true
      image     = "${aws_ecr_repository.mcp_server.repository_url}:${local.mcp_server_image_version}"

      portMappings = [
        {
          name          = "http"
          containerPort = 8001
          hostPort      = 8001
          protocol      = "tcp"
        }
      ]

      readonlyRootFilesystem = false

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8001/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }

      secrets = [
        { name = "DATABASE_URL", valueFrom = aws_ssm_parameter.database_url.arn },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${local.project_name}-mcp-server"
          "awslogs-region"        = local.aws_region
          "awslogs-stream-prefix" = "mcp-server"
        }
      }
    }
  }

  load_balancer = {
    service = {
      target_group_arn = aws_lb_target_group.mcp_server.arn
      container_name   = "mcp-server"
      container_port   = 8001
    }
  }

  subnet_ids = module.vpc.private_subnets

  security_group_ingress_rules = {
    alb = {
      from_port                    = 8001
      to_port                      = 8001
      ip_protocol                  = "tcp"
      referenced_security_group_id = aws_security_group.alb.id
    }
  }

  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "mcp_server" {
  name              = "/ecs/${local.project_name}-mcp-server"
  retention_in_days = 7

  tags = local.tags
}

resource "aws_lb_target_group" "mcp_server" {
  name        = "${local.project_name}-mcp-server"
  port        = 8001
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = local.tags
}

resource "aws_lb_listener_rule" "mcp_server" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mcp_server.arn
  }

  condition {
    path_pattern {
      values = ["/book-mcp-server/*"]
    }
  }

  tags = local.tags
}
