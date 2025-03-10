# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip and install dependencies efficiently
COPY requirements.txt .  
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure main.py is executable (optional)
RUN chmod +x main.py

# Set the default command to run the application
CMD ["python", "main.py"]
