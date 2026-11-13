@echo off
title JyotishOS Backend API
echo Starting JyotishOS FastAPI Backend Engine on http://127.0.0.1:8000
python -m uvicorn src.jyotish.api.main:app --host 127.0.0.1 --port 8000 --reload
