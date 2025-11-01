# RIK API - Production Docker Image
# ==================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt requirements-demo.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-demo.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p /app/data /app/logs && \
    chmod 777 /app/data /app/logs

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Default command (can be overridden)
CMD ["python", "rik_api.py"]
