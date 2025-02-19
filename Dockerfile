# Use lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PORT=8000
ENV MAX_WORKERS=4
ENV PYTHONUNBUFFERED=1
ENV PILLOW_MEMORY_LIMIT=1024M  
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0  

# Install system dependencies for Pillow & OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose API port
EXPOSE 8000

# Start FastAPI using Gunicorn
CMD gunicorn main:app --workers $MAX_WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
