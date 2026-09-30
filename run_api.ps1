Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Bharat Jyotish Enterprise API Gateway on port 8000" -ForegroundColor Green
Write-Host "Swagger UI: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "ReDoc:      http://localhost:8000/redoc" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
python -m uvicorn src.jyotish.api.main:app --host 127.0.0.1 --port 8000 --reload
