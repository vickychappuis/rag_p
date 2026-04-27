variable "aws_region" {
  default = "us-east-1"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "ami_id" {
  description = "Ubuntu 24.04 LTS AMI for us-east-1"
  default     = "ami-0f9de6e2d2f067fca"
}

variable "deployer_ip" {
  description = "Your public IP for SSH access (CIDR format)"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  sensitive   = true
}

variable "cohere_api_key" {
  description = "Cohere API key"
  sensitive   = true
}
