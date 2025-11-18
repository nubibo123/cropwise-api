# Sử dụng Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY model.pth .
COPY yolo_leaf_model.pt .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
