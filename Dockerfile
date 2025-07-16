# Stage 1: Build Stage - install dependencies
FROM python:3.11-slim AS build

WORKDIR /app

# Install build dependencies and curl (wait-for-it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/app

WORKDIR /app

# Install runtime dependencies including netcat for wait loops and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -ms /bin/bash appuser

# Copy installed Python packages and binaries from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Add wait-for-it script to wait for dependencies in entrypoint
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    -o /usr/local/bin/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Fix permissions so non-root user can access files
RUN chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["/entrypoint.sh"]
