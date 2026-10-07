terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# The provider is written so the SAME code targets either LocalStack or real AWS.
# When var.use_localstack = true we point every endpoint at LocalStack, skip the
# credential/metadata validation that real AWS requires, and force path-style S3.
provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  s3_use_path_style           = var.use_localstack
  skip_credentials_validation = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  skip_requesting_account_id  = var.use_localstack

  dynamic "endpoints" {
    for_each = var.use_localstack ? [1] : []
    content {
      ec2 = var.localstack_endpoint
      s3  = var.localstack_endpoint
      iam = var.localstack_endpoint
      sts = var.localstack_endpoint
      ecr = var.localstack_endpoint
    }
  }

  default_tags {
    tags = {
      Project     = "final-devops-project"
      Owner       = "arjun"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
