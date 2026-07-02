#!/bin/bash
set -e

REPO_DIR="/opt/erp-test"

echo "[deploy] Restarting containers..."
docker compose -f "$REPO_DIR/docker-compose.yml" pull
docker compose -f "$REPO_DIR/docker-compose.yml" up -d --remove-orphans

echo "[deploy] Waiting for Odoo to be ready..."
sleep 10

echo "[deploy] Installing modules..."
docker compose -f "$REPO_DIR/docker-compose.yml" exec -T odoo \
  odoo -d odoo --stop-after-init \
  -i auto_login,izin_yonetimi,stok_yonetimi,satis_yonetimi,satin_alma,muhasebe_yonetimi,fatura_yonetimi \
  --no-http 2>/dev/null || true

echo "[deploy] Done. Odoo is running on port 8069 (live updates: 8072)."
