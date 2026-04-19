#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[deploy] Pulling latest changes..."
git -C "$REPO_DIR" pull origin main

echo "[deploy] Restarting containers..."
docker compose -f "$REPO_DIR/docker-compose.yml" pull
docker compose -f "$REPO_DIR/docker-compose.yml" up -d --remove-orphans

echo "[deploy] Done. Odoo is running on port 8069."
