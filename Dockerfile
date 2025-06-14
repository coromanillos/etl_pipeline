# Dockerfile
# --- Build Stage --- 
FROM python:3.11-slim AS build

WORKDIR /app

# Install prerequisites
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Runtime Stage --- 
FROM python:3.11-slim

WORKDIR /app

# Reduce output buffering for logging
ENV PYTHONUNBUFFERED=1

# Install curl for wait-for-it
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Change ownership to non-root
RUN chown -R appuser:appuser /app

# Use non-root for subsequent operations
USER appuser

# Copy installed Python packages from build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy your application code
COPY . .

# Add wait-for-it script
WORKDIR /usr/local/bin
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o wait-for-it.sh && \
    chmod +x wait-for-it.sh

# Set entrypoint to wait-for-it
ENTRYPOINT ["wait-for-it.sh", "db:5432","-t","30","--","python","src/main.py"]
