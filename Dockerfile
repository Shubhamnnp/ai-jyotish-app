# Enterprise production-grade Python container for Bharat Jyotish AI SaaS
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies, libpq for PostgreSQL, & fonts for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    fonts-noto-cjk \
    fonts-deva \
    fonts-indic \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Streamlit (8501) and FastAPI (8000) ports
EXPOSE 8000 8501

# Default CMD (can be overridden by docker-compose)
CMD ["uvicorn", "src.jyotish.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
