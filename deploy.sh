#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[deploy] Pulling latest changes..."
git -C "$REPO_DIR" pull origin main

echo "[deploy] Restarting containers..."
docker compose -f "$REPO_DIR/docker-compose.yml" pull
docker compose -f "$REPO_DIR/docker-compose.yml" up -d --remove-orphans

echo "[deploy] Waiting for Odoo to be ready..."
sleep 10

echo "[deploy] Installing auto_login module..."
docker compose -f "$REPO_DIR/docker-compose.yml" exec -T odoo \
  odoo -d odoo --stop-after-init -i auto_login --no-http 2>/dev/null || true

echo "[deploy] Done. Odoo is running on port 8069 (live updates: 8072)."
