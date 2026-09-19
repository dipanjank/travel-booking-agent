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
