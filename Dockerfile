# Ottawa City Services RAG Chatbot - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with fixed protobuf version
RUN pip install --upgrade pip && \
    pip install protobuf==3.20.3 && \
    pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p data/raw data/processed data/vector_store logs

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app:/app/src

# Create non-root user
RUN useradd --create-home --shell /bin/bash ottawa && \
    chown -R ottawa:ottawa /app

# Switch to non-root user
USER ottawa

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["python", "launch_chatbot.py"]