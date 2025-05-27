# --- Build Stage ---
FROM python:3.11-slim AS build

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install curl for wait-for-it
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy your application code
COPY . .

# Add wait-for-it script
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it

# Run app with wait-for-it
CMD ["wait-for-it", "db:5432", "-t", "30", "--", "python", "src/main.py"]
