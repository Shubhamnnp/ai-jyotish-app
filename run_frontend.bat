@echo off
title JyotishOS Modern Platform
echo ========================================================
echo   JyotishOS Modern UI (React 19 + Next.js 15)
echo   FastAPI Engine: http://127.0.0.1:8000
echo   Frontend App:   http://localhost:3000
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on port 8000...
start "JyotishOS FastAPI Backend" cmd /k "python -m uvicorn src.jyotish.api.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching Next.js Dev Server on port 3000...
cd frontend
npm run dev
