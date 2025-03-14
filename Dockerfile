# Build Stage
FROM python:3.9-slim AS build

WORKDIR /app

# Copy only the requirements.txt to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime Stage
FROM python:3.9-slim

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app /app

# Copy the rest of the application code
COPY . .

# Set the default command to run the application
CMD ["python", "main.py"]
