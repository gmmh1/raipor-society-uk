Write-Host "Bootstrapping Raipor Society UK Community OS" -ForegroundColor Cyan

if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

docker compose up --build -d

docker compose exec backend python manage.py migrate

Write-Host "Bootstrap completed." -ForegroundColor Green
Write-Host "API: http://localhost:8000/api/health/" -ForegroundColor Green
Write-Host "Admin: http://localhost:8000/admin/" -ForegroundColor Green
Write-Host "Grafana: http://localhost:3000/" -ForegroundColor Green
