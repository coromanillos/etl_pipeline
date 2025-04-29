# Build Stage
FROM python:3.9-slim AS build

WORKDIR /app

# Copy only the requirements.txt to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install curl to download wait-for-it script
RUN apt-get update && apt-get install -y curl

# Runtime Stage
FROM python:3.9-slim

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app /app

# Copy the rest of the application code
COPY . .

# Download the wait-for-it script and make it executable
RUN curl -sSL https://github.com/vishnubob/wait-for-it/releases/download/v2.7.0/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it

# Set the default command to run the application with wait-for-it to ensure the db is ready
CMD ["sh", "-c", "wait-for-it db:5432 -- python main.py"]
