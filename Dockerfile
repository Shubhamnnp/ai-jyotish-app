# Enterprise production-grade Python container for JyotishOS (Phase 6, Task P6-T8)
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV EPHE_PATH=/app/ephe

WORKDIR /app

# Install system dependencies, libpq for PostgreSQL, curl for healthchecks, & Indic fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    fonts-noto-cjk \
    fonts-deva \
    fonts-indic \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Streamlit (8501) and FastAPI (8000) ports
EXPOSE 8000 8501

# Production Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default CMD (can be overridden by docker-compose)
CMD ["uvicorn", "src.jyotish.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
