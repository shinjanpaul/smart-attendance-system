# Production Dockerfile for VeriFace AI on Render.com
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies required for C++ compilation fallback, OpenCV, and linear algebra
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install pre-compiled binary dlib wheel (fast 5-second install with zero compilation)
RUN pip install --no-cache-dir dlib-bin>=19.24.2 || pip install --no-cache-dir dlib

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run collectstatic for production assets
RUN python manage.py collectstatic --noinput || true

# Render dynamically assigns the PORT environment variable
EXPOSE 8000

# Run migrations and launch ASGI Daphne server with real-time WebSocket support
CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} smart_attendance.asgi:application"]
