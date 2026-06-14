# MCP Server Dockerfile
# Optimized for Docker Compose

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY src/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Copy SSL certificates
COPY certs/ ./certs/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose MCP port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8081)).close()" || exit 1

# Run the MCP server (uses environment variables from docker-compose)
ENTRYPOINT ["python", "main.py"]
