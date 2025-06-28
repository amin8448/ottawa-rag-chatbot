# Ottawa RAG Chatbot - Production Dockerfile
# Multi-stage build for optimized production image

# ===== BUILD STAGE =====
FROM python:3.11-slim as builder

# Set build arguments
ARG INSTALL_DEV_DEPS=false

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# ===== PRODUCTION STAGE =====
FROM python:3.11-slim as production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r ottawa && useradd -r -g ottawa ottawa

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy NLTK data
COPY --from=builder /root/nltk_data /home/ottawa/nltk_data
ENV NLTK_DATA=/home/ottawa/nltk_data

# Copy application code
COPY src/ ./src/
COPY deployment/docker/docker_app.py ./app.py
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/logs /app/data/embeddings /app/data/processed /app/data/raw

# Set ownership and permissions
RUN chown -R ottawa:ottawa /app /home/ottawa
USER ottawa

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Expose port
EXPOSE 7860

# Start command
CMD ["python", "app.py"]

# ===== DEVELOPMENT STAGE =====
FROM production as development

# Switch back to root for installing dev dependencies
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    jupyter \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    ipython

# Install additional debugging tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to ottawa user
USER ottawa

# Override CMD for development
CMD ["python", "app.py", "--debug"]