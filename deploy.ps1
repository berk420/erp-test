$ErrorActionPreference = "Stop"
$RepoDir = $PSScriptRoot

Write-Host "[deploy] Pulling latest changes..."
git -C $RepoDir pull origin main

Write-Host "[deploy] Restarting containers..."
docker compose -f "$RepoDir\docker-compose.yml" pull
docker compose -f "$RepoDir\docker-compose.yml" up -d --remove-orphans

Write-Host "[deploy] Done. Odoo is running on port 8069."
