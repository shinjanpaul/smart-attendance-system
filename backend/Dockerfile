# Production Dockerfile for VeriFace AI on Render.com (Optimized for 512MB RAM & Low Memory Build)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"
ENV PORT=8000

WORKDIR /app

# Install minimal system dependencies required for C++ build & OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade packaging tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install numpy first (required by dlib bindings)
RUN pip install --no-cache-dir numpy==1.26.4

# Compile dlib strictly with 1 single thread (prevents memory ballooning over 8GB)
RUN CMAKE_BUILD_PARALLEL_LEVEL=1 pip install --no-cache-dir dlib==19.24.4

# Install official face-recognition models and package without triggering duplicate dlib rebuilds
RUN pip install --no-cache-dir face-recognition-models>=0.3.0
RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

# Copy and install application requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run collectstatic for static assets
RUN python manage.py collectstatic --noinput || true

# Render dynamically assigns the PORT environment variable
EXPOSE 8000

# Run migrations and launch Daphne ASGI server
CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} smart_attendance.asgi:application"]
