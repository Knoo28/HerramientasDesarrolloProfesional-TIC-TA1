terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Obtiene dinámicamente la última AMI oficial de Ubuntu 24.04 LTS
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# 1. Security Group con puertos 22, 80 y 8080 abiertos
resource "aws_security_group" "web_python" {
  name        = "web-python-sg"
  description = "Permitir SSH, HTTP y puerto 8080"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
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

  ingress {
    description = "Web 8080"
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

# 2. Instancia EC2 con aprovisionamiento
resource "aws_instance" "web_python_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.web_python.id] # Corregido

  user_data = <<-EOF
              #!/bin/bash
              set -e

              # 1. Actualizar e instalar dependencias base y Python
              apt-get update -y
              apt-get install -y git curl ca-certificates python3-pip python3-venv

              # 2. Instalar Docker
              apt-get install -y docker.io
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu

              # 3. Clonar repositorio
              cd /home/ubuntu
              git clone ${var.repo_url} app
              chown -R ubuntu:ubuntu /home/ubuntu/app
              cd /home/ubuntu/app

              # 4. Construir y levantar el contenedor Docker
              docker build -t mi-app:1.0 .
              docker run -d -p 8080:8080 --name mi-app-web --restart always mi-app:1.0
              EOF

  tags = {
    Name = "Web-Python-Server"
  }
}

# 3. Datos de salida
output "ip_publica" {
  value       = aws_instance.web_python_server.public_ip
  description = "IP pública de la instancia"
}

output "url_acceso" {
  value       = "http://${aws_instance.web_python_server.public_dns}:8080" # Corregido
  description = "URL directa para ver la aplicación en el navegador"
}