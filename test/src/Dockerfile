# --- Build Stage ---
    FROM python:3.9-slim AS build

    WORKDIR /app
    
    # Copy requirements file and install dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # --- Runtime Stage ---
    FROM python:3.9-slim
    
    WORKDIR /app
    
    # Install only what's necessary (curl for wait-for-it)
    RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
    
    # Copy installed Python packages from build stage
    COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
    COPY --from=build /usr/local/bin /usr/local/bin
    
    # Copy application code (including main.py, src/, etc.)
    COPY . .
    
    # Download wait-for-it script
    RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
        chmod +x /usr/local/bin/wait-for-it
    
    # Entry point that waits for DB to be ready before launching app
    CMD ["wait-for-it", "db:5432", "--", "python", "/app/main.py"]
    