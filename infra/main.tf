terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- SSH Key ---

resource "tls_private_key" "deployer" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = "promtior-deployer"
  public_key = tls_private_key.deployer.public_key_openssh
}

resource "local_file" "private_key" {
  content         = tls_private_key.deployer.private_key_pem
  filename        = "${path.module}/promtior-deployer.pem"
  file_permission = "0400"
}

# --- Security Groups ---

resource "aws_security_group" "backend" {
  name        = "promtior-backend"
  description = "Backend API - only API Gateway and SSH"

  ingress {
    description = "SSH from deployer"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.deployer_ip]
  }

  ingress {
    description = "API Gateway to backend"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "qdrant" {
  name        = "promtior-qdrant"
  description = "Qdrant - only backend and SSH"

  ingress {
    description     = "Qdrant API from backend"
    from_port       = 6333
    to_port         = 6334
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  ingress {
    description = "SSH from deployer"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.deployer_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- IAM Role for Backend (SSM access) ---

resource "aws_iam_role" "backend" {
  name = "promtior-backend"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "backend_ssm" {
  name = "ssm-read"
  role = aws_iam_role.backend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/promtior/*"
    }]
  })
}

resource "aws_iam_instance_profile" "backend" {
  name = "promtior-backend"
  role = aws_iam_role.backend.name
}

# --- SSM Parameters ---

resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/promtior/openai_api_key"
  type  = "SecureString"
  value = var.openai_api_key
}

resource "aws_ssm_parameter" "cohere_api_key" {
  name  = "/promtior/cohere_api_key"
  type  = "SecureString"
  value = var.cohere_api_key
}

resource "aws_ssm_parameter" "qdrant_url" {
  name  = "/promtior/qdrant_url"
  type  = "String"
  value = "http://${aws_instance.qdrant.private_ip}:6333"
}

resource "aws_ssm_parameter" "collection_name" {
  name  = "/promtior/collection_name"
  type  = "String"
  value = "promtior"
}

resource "aws_ssm_parameter" "embedding_model" {
  name  = "/promtior/embedding_model"
  type  = "String"
  value = "text-embedding-3-large"
}

resource "aws_ssm_parameter" "llm_model" {
  name  = "/promtior/llm_model"
  type  = "String"
  value = "gpt-5.5"
}

resource "aws_ssm_parameter" "top_k" {
  name  = "/promtior/top_k"
  type  = "String"
  value = "10"
}

resource "aws_ssm_parameter" "rerank_model" {
  name  = "/promtior/rerank_model"
  type  = "String"
  value = "rerank-v3.5"
}

resource "aws_ssm_parameter" "rerank_top_n" {
  name  = "/promtior/rerank_top_n"
  type  = "String"
  value = "5"
}

resource "aws_ssm_parameter" "chunk_overlap" {
  name  = "/promtior/chunk_overlap"
  type  = "String"
  value = "200"
}

resource "aws_ssm_parameter" "root_path" {
  name  = "/promtior/root_path"
  type  = "String"
  value = "https://rag.vickychappuis.dev"
}

# --- EC2 Instances ---

resource "aws_instance" "qdrant" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.deployer.key_name

  vpc_security_group_ids = [aws_security_group.qdrant.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl enable docker
    systemctl start docker
    docker run -d --name qdrant --restart always \
      -p 6333:6333 -p 6334:6334 \
      -v qdrant_storage:/qdrant/storage \
      qdrant/qdrant:latest
  EOF

  tags = {
    Name = "promtior-qdrant"
  }
}

resource "aws_instance" "backend" {
  ami                  = var.ami_id
  instance_type        = var.instance_type
  key_name             = aws_key_pair.deployer.key_name
  iam_instance_profile = aws_iam_instance_profile.backend.name

  vpc_security_group_ids = [aws_security_group.backend.id]

  tags = {
    Name = "promtior-backend"
  }
}

# --- API Gateway ---

resource "aws_apigatewayv2_api" "main" {
  name          = "promtior-rag"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "backend" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri    = "http://${aws_instance.backend.public_ip}:8080/{proxy}"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}

# --- Custom Domain ---

resource "aws_acm_certificate" "rag" {
  domain_name       = "rag.vickychappuis.dev"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "rag" {
  certificate_arn = aws_acm_certificate.rag.arn
}

resource "aws_apigatewayv2_domain_name" "rag" {
  domain_name = "rag.vickychappuis.dev"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.rag.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.rag]
}

resource "aws_apigatewayv2_api_mapping" "rag" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.rag.id
  stage       = aws_apigatewayv2_stage.default.id
}
