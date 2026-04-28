# Use Python 3.10 slim as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    CHECKPOINT_PATH=/app/outputs/warmup/agent

# Install system dependencies for cvxpy and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model to avoid latency on first request
# We use the same model defined in src/embedding.py
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Copy the rest of the application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose the port
EXPOSE 7860

# Command to run the application
CMD ["python", "app.py"]