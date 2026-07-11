FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (for pdfplumber, cv2, etc)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads data/reports data/processed data/raw

# Expose the API port (Railway/Render will use $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI (use PORT env var if available, default to 8000)
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
