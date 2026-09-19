@echo off
title AI Jyotish SaaS & Grahalakshanam Suite
echo ====================================================
echo Starting AI Jyotish SaaS Application...
echo ====================================================
echo.
python -m streamlit run src/jyotish/ui/app.py --server.port 8501 --server.headless false
pause

