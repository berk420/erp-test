$ErrorActionPreference = "Stop"
$RepoDir = $PSScriptRoot

Write-Host "[deploy] Pulling latest changes..."
git -C $RepoDir pull origin main

Write-Host "[deploy] Restarting containers..."
docker compose -f "$RepoDir\docker-compose.yml" pull
docker compose -f "$RepoDir\docker-compose.yml" up -d --remove-orphans

Write-Host "[deploy] Waiting for Odoo to be ready..."
Start-Sleep -Seconds 10

Write-Host "[deploy] Installing modules..."
docker compose -f "$RepoDir\docker-compose.yml" exec -T odoo `
    odoo -d odoo --stop-after-init `
    -i auto_login,izin_yonetimi,stok_yonetimi,satis_yonetimi,satin_alma,muhasebe_yonetimi,fatura_yonetimi `
    --no-http 2>$null
if (-not $?) { Write-Host "[deploy] Module install skipped (already installed or DB not ready yet)." }

Write-Host "[deploy] Done. Odoo is running on port 8069 (live updates: 8072)."
