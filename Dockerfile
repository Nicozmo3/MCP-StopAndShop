FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy src
COPY src/ .

# Expose MCP port
EXPOSE 8080

ENTRYPOINT ["python", "main.py"] 