# -------------------------
# Stage 1: Build Layer
# -------------------------
FROM python:3.11-slim AS build

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# Stage 2: Runtime Layer
# -------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/app

WORKDIR /app

# Create non-root user
RUN useradd -ms /bin/bash appuser

# Runtime dependencies
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and binaries from build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Add wait-for-it
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    -o /usr/local/bin/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set permissions
RUN chown -R appuser:appuser /app

USER appuser
ENTRYPOINT ["/entrypoint.sh"]
