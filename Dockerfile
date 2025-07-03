# --- Build Stage --- 
FROM python:3.11-slim AS build

WORKDIR /app

# Install prerequisites for building Python packages
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Runtime Stage --- 
FROM python:3.11-slim

# Environment variables for better logging
ENV PYTHONUNBUFFERED=1

# Create a dedicated app directory
WORKDIR /app

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Install curl (for wait-for-it)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and binaries from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy your application code
COPY . .

# Download wait-for-it to a safe temporary location and move it to /usr/local/bin
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    -o /tmp/wait-for-it.sh && \
    chmod +x /tmp/wait-for-it.sh && \
    mv /tmp/wait-for-it.sh /usr/local/bin/wait-for-it.sh

# Change ownership of the /app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set entrypoint using wait-for-it and run the application
ENTRYPOINT ["wait-for-it.sh", "db:5432", "-t", "30", "--", "python", "src/main.py"]
