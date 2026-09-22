# module "backend_service" {
#   source  = "terraform-aws-modules/ecs/aws//modules/service"
#   version = "~> 7.0"
#
#   name        = "${local.project_name}-backend"
#   cluster_arn = aws_ecs_cluster.main.arn
#
#   desired_count = 1
#
#   cpu    = 512
#   memory = 1024
#
#   enable_autoscaling = false
#
#   tasks_iam_role_statements = [
#     {
#       effect    = "Allow"
#       actions   = ["bedrock:InvokeModel"]
#       resources = ["arn:aws:bedrock:${local.aws_region}::foundation-model/*"]
#     },
#   ]
#
#   task_exec_ssm_param_arns = [
#     aws_ssm_parameter.backend_database_url.arn,
#     aws_ssm_parameter.backend_jwt_secret.arn,
#     aws_ssm_parameter.backend_admin_password.arn,
#   ]
#
#   container_definitions = {
#     backend = {
#       essential = true
#       image     = "${aws_ecr_repository.backend.repository_url}:${local.backend_image_version}"
#
#       portMappings = [
#         {
#           name          = "http"
#           containerPort = 8000
#           hostPort      = 8000
#           protocol      = "tcp"
#         }
#       ]
#
#       readonlyRootFilesystem = false
#
#       healthCheck = {
#         command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
#         interval    = 30
#         timeout     = 5
#         retries     = 3
#         startPeriod = 30
#       }
#
#       environment = [
#         { name = "ADMIN_USERNAME", value = "admin" },
#         { name = "ADMIN_EMAIL", value = "admin@travel-booking.io" },
#         { name = "MCP_SERVER_URL", value = "http://${aws_lb.main.dns_name}/mcp" },
#         { name = "AWS_REGION", value = local.aws_region },
#       ]
#
#       secrets = [
#         { name = "DATABASE_URL", valueFrom = aws_ssm_parameter.backend_database_url.arn },
#         { name = "JWT_SECRET", valueFrom = aws_ssm_parameter.backend_jwt_secret.arn },
#         { name = "ADMIN_PASSWORD", valueFrom = aws_ssm_parameter.backend_admin_password.arn },
#       ]
#
#       logConfiguration = {
#         logDriver = "awslogs"
#         options = {
#           "awslogs-group"         = "/ecs/${local.project_name}-backend"
#           "awslogs-region"        = local.aws_region
#           "awslogs-stream-prefix" = "backend"
#         }
#       }
#     }
#   }
#
#   load_balancer = {
#     service = {
#       target_group_arn = aws_lb_target_group.backend.arn
#       container_name   = "backend"
#       container_port   = 8000
#     }
#   }
#
#   subnet_ids = module.vpc.private_subnets
#
#   security_group_ingress_rules = {
#     alb = {
#       from_port                    = 8000
#       to_port                      = 8000
#       ip_protocol                  = "tcp"
#       referenced_security_group_id = aws_security_group.alb.id
#     }
#   }
#
#   security_group_egress_rules = {
#     all = {
#       ip_protocol = "-1"
#       cidr_ipv4   = "0.0.0.0/0"
#     }
#   }
#
#   tags = local.tags
# }
#
# resource "aws_cloudwatch_log_group" "backend" {
#   name              = "/ecs/${local.project_name}-backend"
#   retention_in_days = 7
#
#   tags = local.tags
# }
#
# resource "aws_lb_target_group" "backend" {
#   name        = "${local.project_name}-backend"
#   port        = 8000
#   protocol    = "HTTP"
#   vpc_id      = module.vpc.vpc_id
#   target_type = "ip"
#
#   health_check {
#     path                = "/health"
#     port                = "traffic-port"
#     healthy_threshold   = 2
#     unhealthy_threshold = 3
#     timeout             = 5
#     interval            = 30
#     matcher             = "200"
#   }
#
#   tags = local.tags
# }
#
# resource "aws_lb_listener_rule" "backend" {
#   listener_arn = aws_lb_listener.http.arn
#   priority     = 200
#
#   action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.backend.arn
#   }
#
#   condition {
#     path_pattern {
#       values = ["/api/*"]
#     }
#   }
#
#   tags = local.tags
# }
