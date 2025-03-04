# Official python image from docker hub
FROM python:3.9-slim 

WORKDIR /app

COPY . .

# Only install dependencies if requirements.txt exists (Not made yet.)
RUN pip install --no-cache-dir -r requirements.txt  

CMD ["python", "main.py"]