resource "aws_ssm_parameter" "vpc_id" {
  name  = "/${var.project_name}/vpc/id"
  type  = "String"
  value = module.vpc.vpc_id

  tags = local.tags
}

resource "aws_ssm_parameter" "vpc_cidr" {
  name  = "/${var.project_name}/vpc/cidr"
  type  = "String"
  value = module.vpc.vpc_cidr_block

  tags = local.tags
}

resource "aws_ssm_parameter" "public_subnet_ids" {
  name  = "/${var.project_name}/vpc/public-subnet-ids"
  type  = "StringList"
  value = join(",", module.vpc.public_subnets)

  tags = local.tags
}

resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "/${var.project_name}/vpc/private-subnet-ids"
  type  = "StringList"
  value = join(",", module.vpc.private_subnets)

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_dns_name" {
  name  = "/${var.project_name}/alb/dns-name"
  type  = "String"
  value = aws_lb.main.dns_name

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_arn" {
  name  = "/${var.project_name}/alb/arn"
  type  = "String"
  value = aws_lb.main.arn

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_listener_arn" {
  name  = "/${var.project_name}/alb/http-listener-arn"
  type  = "String"
  value = aws_lb_listener.http.arn

  tags = local.tags
}

resource "aws_ssm_parameter" "alb_security_group_id" {
  name  = "/${var.project_name}/alb/security-group-id"
  type  = "String"
  value = aws_security_group.alb.id

  tags = local.tags
}

resource "aws_ssm_parameter" "db_endpoint" {
  name  = "/${var.project_name}/db/endpoint"
  type  = "String"
  value = module.rds.db_instance_address

  tags = local.tags
}

resource "aws_ssm_parameter" "db_port" {
  name  = "/${var.project_name}/db/port"
  type  = "String"
  value = module.rds.db_instance_port

  tags = local.tags
}

resource "aws_ssm_parameter" "db_name" {
  name  = "/${var.project_name}/db/name"
  type  = "String"
  value = replace(var.project_name, "-", "_")

  tags = local.tags
}

resource "aws_ssm_parameter" "db_username" {
  name  = "/${var.project_name}/db/username"
  type  = "String"
  value = module.rds.db_instance_username

  tags = local.tags
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/${var.project_name}/db/password"
  type  = "SecureString"
  value = random_password.db.result

  tags = local.tags
}
