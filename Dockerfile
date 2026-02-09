FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    kubernetes \
    redis \
    grpcio \
    protobuf==3.20.3 \
    falcon \
    gunicorn \
    neo4j

# Copy the entire firm directory into the container
# Assuming build context is key parent directory or we copy specifically
COPY firm /app/firm

ENV PYTHONPATH=/app

# Default command (can be overridden in k8s)
CMD ["python", "/app/firm/server.py"]
