#!/usr/bin/env bash
set -euo pipefail

# Boilerworks — FastAPI + Next.js
# Usage: ./run.sh [command]

COMPOSE_FILE=""

if [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
elif [ -f "docker-compose.yaml" ]; then
    COMPOSE_FILE="docker-compose.yaml"
fi

compose() {
    if [ -n "$COMPOSE_FILE" ]; then
        docker compose -f "$COMPOSE_FILE" "$@"
    else
        echo "No docker-compose file found"
        exit 1
    fi
}

case "${1:-help}" in
    up|start)
        compose up -d --build
        echo ""
        echo "Services starting. Check status with: ./run.sh status"
        ;;
    down|stop)
        compose down
        ;;
    restart)
        compose down
        compose up -d --build
        ;;
    status|ps)
        compose ps
        ;;
    logs)
        compose logs -f "${2:-}"
        ;;
    seed)
        compose exec api python -m app.seed
        ;;
    test)
        compose exec api pytest
        ;;
    lint)
        compose exec api ruff check . && compose exec api ruff format --check .
        ;;
    shell)
        compose exec api bash
        ;;
    migrate)
        compose exec api alembic upgrade head
        ;;
    help|*)
        echo "Usage: ./run.sh <command>"
        echo ""
        echo "Commands:"
        echo "  up, start     Start all services"
        echo "  down, stop    Stop all services"
        echo "  restart       Restart all services"
        echo "  status, ps    Show service status"
        echo "  logs [svc]    Tail logs (optionally for one service)"
        echo "  seed          Seed the database"
        echo "  test          Run tests"
        echo "  lint          Run linters"
        echo "  shell         Open a shell in the API container"
        echo "  migrate       Run Alembic migrations"
        echo "  help          Show this help"
        ;;
esac
