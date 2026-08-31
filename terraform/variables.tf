variable "aws_region" {
  description = "Región de AWS donde se desplegará la infraestructura"
  type        = string
  default     = "us-east-2"
}

variable "key_name" {
  description = "Nombre del Key Pair existente en AWS para acceder por SSH"
  type        = string
}

variable "repo_url" {
  description = "URL pública de GitHub de tu proyecto de la calculadora"
  type        = string
  default     = "https://github.com/TU_USUARIO/TU_REPOSITORIO.git" # Cambia esto por el repo del proyecto
}