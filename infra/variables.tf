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

variable "llm_model" {
  description = "OpenAI chat model ID"
  default     = "gpt-5.5"
}

variable "embedding_model" {
  description = "OpenAI embedding model ID"
  default     = "text-embedding-3-large"
}

variable "rerank_model" {
  description = "Cohere rerank model ID"
  default     = "rerank-v3.5"
}

variable "top_k" {
  description = "Number of chunks to retrieve from the vector store"
  default     = "10"
}

variable "rerank_top_n" {
  description = "Number of chunks to keep after reranking"
  default     = "5"
}
