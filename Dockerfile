# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for Chroma persistence
RUN mkdir -p /app/chroma_storage

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
# CMD ["python", "app.py"]

# Keep container running
CMD ["tail", "-f", "/dev/null"]