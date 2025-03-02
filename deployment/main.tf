provider "aws" {
  region  = "us-east-1"
#   profile = "mednoteai"
}

data "aws_secretsmanager_secret" "ezmednote" {
  name = "ezmednote"
}
data "aws_secretsmanager_secret_version" "current_ezmednote" {
  secret_id = data.aws_secretsmanager_secret.ezmednote.id
}

locals {
  ezmednote = jsondecode(data.aws_secretsmanager_secret_version.current_ezmednote.secret_string)
}


# resource "aws_s3_bucket" "ezmednote_certs" {
#   bucket = "ezmednote.certs"
#   lifecycle {
#     prevent_destroy = true
#   }
# }

# resource "aws_s3_bucket" "mednoteai" {
#   bucket = "mednoteai"
#   lifecycle {
#     prevent_destroy = true
#   }
# }

resource "aws_key_pair" "mednoteai_key" {
  key_name   = "mednoteai_key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDft+PfdP3ittp9W2x3wa/HQIyRwEFBrrF+p+tERJRyU0Ss5aQ4gndto5AY+YxudExEF99zX32QeTxaB1qvaQrdD4wTnXrj/zxypaNzMkONc8N1255r2DN4rDM/1GV3bjFi780U6NZIV6nM7n49mUi03wCgt8M90HDoF1V/ybpGSrxOowEH4UntCpIpGFrMr/Uw8Is0Yz0k+HnKB0lMaCryX+SEMu4pA2IBYvnlOzgUtBOZkUDcydrOJR2Jkq1drn4hWUoHDRbrcQvQ+aZyX+Szs7EFCQOAuXtZhMKD6WAexCEwkiv7+kOA/CNlfRZm1/9ThdjFJ0j+MRTSrvxJWAW7ad3uooPRVjyU9hv22uq/B7JRhDyH8VySA0FSXChQO4MruW+GHZ3Hp6BRwo4L+Ybyo7tPv2vWI2HTR64aROFcHFHm5NKBPw7gV8IANHsONF1x0c7vRzbBb+HtnBpuHUSKSeRPSShxewKFYkhwv+spc3gpeLh204JgDyHDMrHEPls= nozander@nozander-pc"
}
resource "aws_security_group" "public_access" {
  name        = "public"
  description = "Allow SSH and HTTPS inbound traffic, and HTTPS outbound traffic"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "HTTP_Out"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mednote.ai"
  }
}

# resource "aws_instance" "mednoteai" {
#   ami                    = "ami-0857f4292ceff2e66" # Use the desired AMI ID
#   instance_type          = "g4dn.xlarge"
#   key_name               = aws_key_pair.mednoteai_key.key_name
#   vpc_security_group_ids = [aws_security_group.public_access.id]
#   tags = {
#     Name = "mednote.ai"
#   }
# #   instance_market_options {
# #     market_type = "spot"
# #     spot_options {
# #       max_price = "0.35"
# #     }
# #   }
#   user_data = templatefile("${path.module}/userdata.tftpl", {
#     gh_mednote = local.ezmednote.gh,
#     aws_cli    = local.ezmednote.cli,
#     hf         = local.ezmednote.hf,
#     device     = "cpu",
#     stage      = "dev"
#     domain     = "ezmednote.skywarditsoloutions.com"
#     public_api = "https://ezmednote.skywarditsoloutions.com/api"
#     origin     = "https://ezmednote.skywarditsoloutions.com"
#     }
#   )
#   user_data_replace_on_change = false

# }

resource "aws_instance" "mednoteai_prod" {
  ami           = "ami-03af0e9dc07b16c7f" # Use the desired AMI ID
  instance_type = "g4dn.xlarge"
  key_name      = aws_key_pair.mednoteai_key.key_name
  # p2.xlarge instances have 4 vCPUs and 61 GiB of memory
  vpc_security_group_ids = [aws_security_group.public_access.id]

  tags = {
    Name = "mednote.ai.prod"
  }
  cpu_options {
    core_count       = 2
    threads_per_core = 2
  }
  user_data = templatefile("${path.module}/userdata.tftpl", {
    gh_mednote = local.ezmednote.gh,
    aws_cli    = local.ezmednote.cli,
    hf         = local.ezmednote.hf,
    device     = "cuda",
    stage      = "prod"
    domain     = "ezmednote.com"
    origin     = "https://ezmednote.com"
    public_api = "https://ezmednote.com/api" }

  )
  user_data_replace_on_change = true
}



# resource "aws_eip" "mednoteai" {
#   instance = aws_instance.mednoteai.id
#   vpc      = true
# }
# output "elastic_ip" {
#   value = aws_eip.mednoteai.public_ip
# }

# output "instance_id" {
#   value = aws_instance.mednoteai.id
# }
# output "public_dns" {
#   value = aws_instance.mednoteai.public_dns
# }

# output "private_ip" {
#   value = aws_instance.mednoteai.private_ip
# }
resource "aws_eip" "mednoteai_prod" {
  instance = aws_instance.mednoteai_prod.id
  vpc      = true
}


output "elastic_ip_prod" {
  value = aws_eip.mednoteai_prod.public_ip
}
output "instance_id_prod" {
  value = aws_instance.mednoteai_prod.id
}
