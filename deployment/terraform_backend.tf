
terraform {
  backend "s3" {
    bucket         = "ezmednote.com"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    # dynamodb_table = "tfstate-lock"
    encrypt        = true
  }
}

# resource "aws_dynamodb_table" "dynamodb_tfstate_lock" {
#   #checkov:skip=CKV2_AWS_16: Auto Scaling not required for TF state bucket
#   #checkov:skip=CKV_AWS_28: Dynamodb point in time recovery not required for TF state bucket
#   #checkov:skip=CKV_AWS_119: KMS Customer Managed CMK not required for TF state bucket
#   name           = "tfstate-lock"
#   hash_key       = "LockID"
#   read_capacity  = 20
#   write_capacity = 20

#   attribute {
#     name = "LockID"
#     type = "S"
#   }

#   server_side_encryption {
#     enabled = true
#   }

# }
