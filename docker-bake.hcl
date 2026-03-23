group "default" {
  targets = ["fastapi-app"]
}

variable "VERSION" {
  default = "unknown"
}

target "fastapi-app" {
  context = "."
  dockerfile = "Dockerfile"
  
  tags = [
    "docker.io/kcandidate/fastapi-app:${VERSION}",
    "docker.io/kcandidate/fastapi-app:latest"
  ]

  platforms = [
    "linux/amd64"
  ]

  labels = {
    "org.opencontainers.image.title"       = "fastapi-app"
    "org.opencontainers.image.description" = "Simple fastapi app"
  }
}