@echo off
title Bharat Jyotish AI SaaS - API Gateway v1 (:8000)
echo ========================================================
echo Starting Bharat Jyotish Enterprise API Gateway on port 8000
echo Swagger UI: http://localhost:8000/docs
echo ReDoc:      http://localhost:8000/redoc
echo ========================================================
python -m uvicorn src.jyotish.api.main:app --host 127.0.0.1 --port 8000 --reload
pause
