web: streamlit run src/jyotish/ui/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
api: uvicorn src.jyotish.api.main:app --host 0.0.0.0 --port $PORT

