# Stage 1: Build dependencies
FROM python:3.11-slim AS build

WORKDIR /app

# Install build tools only
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/app \
    PYTHONPATH=/app

WORKDIR /app

# Install runtime packages only
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from build stage
COPY --from=build /install /usr/local

# Create non-root user
RUN useradd -ms /bin/bash appuser

# Copy project files (relative to root context)
COPY airflow ./airflow
COPY src ./src
COPY config ./config
COPY entrypoint.sh /entrypoint.sh

# Install wait-for-it script and set permissions
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh \
    && chmod +x /entrypoint.sh \
    && chown -R appuser:appuser /app

# Create logs and plugins directories, set ownership
RUN mkdir -p /app/logs /app/plugins && chown -R appuser:appuser /app/logs /app/plugins

USER appuser

ENTRYPOINT ["/entrypoint.sh"]
