# Use a lightweight Python base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (curl for health checks, build tools if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project source code into container
COPY . /app/

# Expose Django port
EXPOSE 8000

# Default command (overridden per service in docker-compose.yml)
CMD ["gunicorn", "bms_tracker.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]