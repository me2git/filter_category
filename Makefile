.PHONY: help build up down restart logs clean backend-logs frontend-logs shell-backend shell-frontend

# Default target
help:
	@echo "Tourism Category Filter - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build          Build all Docker images"
	@echo "  up             Start all services"
	@echo "  down           Stop all services"
	@echo "  restart        Restart all services"
	@echo "  logs           View logs from all services"
	@echo "  backend-logs   View backend logs"
	@echo "  frontend-logs  View frontend logs"
	@echo "  shell-backend  Open shell in backend container"
	@echo "  shell-frontend Open shell in frontend container"
	@echo "  clean          Remove all containers and images"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Start services with build
up-build:
	docker-compose up -d --build

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart

# View all logs
logs:
	docker-compose logs -f

# View backend logs
backend-logs:
	docker-compose logs -f backend

# View frontend logs
frontend-logs:
	docker-compose logs -f frontend

# Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/sh

# Open shell in frontend container
shell-frontend:
	docker-compose exec frontend /bin/sh

# Clean up
clean:
	docker-compose down -v --rmi all --remove-orphans

# Development: Start with live reload
dev:
	docker-compose up

# Production build (frontend)
prod-build:
	docker-compose exec frontend npm run build
