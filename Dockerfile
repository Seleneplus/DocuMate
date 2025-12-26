# 1. Base Image: Use the official lightweight Python 3.10 slim image
FROM python:3.10-slim

# 2. Set Working Directory: Define the directory inside the container for our app
WORKDIR /app

# 3. System Dependencies: Install essential packages required for building Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Dependency Installation: Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Source Code: Copy the remaining application files into the container
COPY . .

# 6. Network Configuration: Expose port 8000 for external access
EXPOSE 8000

# 7. Execution: Start the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]