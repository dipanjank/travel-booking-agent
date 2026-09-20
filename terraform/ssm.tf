resource "aws_ssm_parameter" "vpc_id" {
  name  = "/${local.project_name}/vpc/id"
  type  = "String"
  value = module.vpc.vpc_id

  tags = local.tags
}

resource "aws_ssm_parameter" "vpc_cidr" {
  name  = "/${local.project_name}/vpc/cidr"
  type  = "String"
  value = module.vpc.vpc_cidr_block

  tags = local.tags
}

resource "aws_ssm_parameter" "public_subnet_ids" {
  name  = "/${local.project_name}/vpc/public-subnet-ids"
  type  = "StringList"
  value = join(",", module.vpc.public_subnets)

  tags = local.tags
}

resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "/${local.project_name}/vpc/private-subnet-ids"
  type  = "StringList"
  value = join(",", module.vpc.private_subnets)

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_dns_name" {
  name  = "/${local.project_name}/alb/dns-name"
  type  = "String"
  value = aws_lb.main.dns_name

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_arn" {
  name  = "/${local.project_name}/alb/arn"
  type  = "String"
  value = aws_lb.main.arn

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_listener_arn" {
  name  = "/${local.project_name}/alb/http-listener-arn"
  type  = "String"
  value = aws_lb_listener.http.arn

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_security_group_id" {
  name  = "/${local.project_name}/alb/security-group-id"
  type  = "String"
  value = aws_security_group.alb.id

  tags = local.tags
}

resource "aws_ssm_parameter" "ecs_cluster_arn" {
  name  = "/${local.project_name}/ecs/cluster-arn"
  type  = "String"
  value = aws_ecs_cluster.main.arn

  tags = local.tags
}

resource "aws_ssm_parameter" "ecs_cluster_name" {
  name  = "/${local.project_name}/ecs/cluster-name"
  type  = "String"
  value = aws_ecs_cluster.main.name

  tags = local.tags
}

resource "aws_ssm_parameter" "database_url" {
  name  = "/${local.project_name}/db/url"
  type  = "SecureString"
  value = "postgresql+psycopg2://${module.rds.db_instance_username}:${random_password.db.result}@${module.rds.db_instance_address}:${module.rds.db_instance_port}/${replace(local.project_name, "-", "_")}"

  tags = local.tags
}

resource "aws_ssm_parameter" "backend_database_url" {
  name  = "/${local.project_name}/backend/database-url"
  type  = "SecureString"
  value = "postgresql+psycopg://${module.rds.db_instance_username}:${random_password.db.result}@${module.rds.db_instance_address}:${module.rds.db_instance_port}/${replace(local.project_name, "-", "_")}"

  tags = local.tags
}

resource "aws_ssm_parameter" "backend_jwt_secret" {
  name  = "/${local.project_name}/backend/jwt-secret"
  type  = "SecureString"
  value = random_password.jwt_secret.result

  tags = local.tags
}

resource "aws_ssm_parameter" "backend_admin_password" {
  name  = "/${local.project_name}/backend/admin-password"
  type  = "SecureString"
  value = random_password.admin_password.result

  tags = local.tags
}

resource "aws_ssm_parameter" "db_endpoint" {
  name  = "/${local.project_name}/db/endpoint"
  type  = "String"
  value = module.rds.db_instance_address

  tags = local.tags
}

resource "aws_ssm_parameter" "db_port" {
  name  = "/${local.project_name}/db/port"
  type  = "String"
  value = module.rds.db_instance_port

  tags = local.tags
}

resource "aws_ssm_parameter" "db_name" {
  name  = "/${local.project_name}/db/name"
  type  = "String"
  value = replace(local.project_name, "-", "_")

  tags = local.tags
}

resource "aws_ssm_parameter" "db_username" {
  name  = "/${local.project_name}/db/username"
  type  = "String"
  value = module.rds.db_instance_username

  tags = local.tags
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/${local.project_name}/db/password"
  type  = "SecureString"
  value = random_password.db.result

  tags = local.tags
}
