variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "name_prefix" {
  description = "Prefix applied to every resource name"
  type        = string
  default     = "arjun-s21"
}

# ---- LocalStack / AWS switch ----------------------------------------------
variable "use_localstack" {
  description = "When true, target LocalStack instead of real AWS"
  type        = bool
  default     = true
}

variable "localstack_endpoint" {
  description = "LocalStack edge endpoint"
  type        = string
  default     = "http://localhost:4566"
}

variable "aws_access_key" {
  description = "AWS access key (use dummy 'test' for LocalStack)"
  type        = string
  default     = "test"
}

variable "aws_secret_key" {
  description = "AWS secret key (use dummy 'test' for LocalStack)"
  type        = string
  default     = "test"
  sensitive   = true
}

# ---- Networking -----------------------------------------------------------
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.20.101.0/24", "10.20.102.0/24"]
}

variable "azs" {
  description = "Availability zones for the subnets"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ---- Optional ECR (not available in LocalStack Community) ------------------
variable "enable_ecr" {
  description = "Create ECR repositories (requires real AWS or LocalStack Pro)"
  type        = bool
  default     = false
}
