# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Use backend/ prefix when build context is repo root (cloud deployment)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from backend directory
COPY backend/ .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=api.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "api.py"]
