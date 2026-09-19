#!/bin/bash
echo "===================================================="
echo "Starting AI Jyotish SaaS Application..."
echo "===================================================="
streamlit run src/jyotish/ui/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

