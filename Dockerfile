FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV, PDF processing
# Note: libgl1-mesa-glx is obsolete in Debian Trixie, use libgl1 instead
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure model files are present
RUN ls -la ml/registry/ || echo "WARNING: No models in registry!"

# Create necessary directories
RUN mkdir -p \
    data/uploads \
    data/reports \
    data/processed/tabular \
    data/processed/text \
    data/processed/xray \
    data/raw \
    ml/registry

# Expose the API port (Render will override with $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server
# Use PORT environment variable from Render, fallback to 8000
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
