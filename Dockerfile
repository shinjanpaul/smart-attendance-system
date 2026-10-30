# Production Dockerfile for VeriFace AI on Render.com (Optimized for 512MB RAM & Low Memory Build)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"
ENV PORT=8000

WORKDIR /app

# Install minimal system dependencies required for C++ build, Git, and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crucial: setuptools<82.0.0 is strictly required because face_recognition_models imports pkg_resources!
RUN pip install --no-cache-dir "setuptools<82.0.0" wheel pip

# Install numpy and Pillow (PIL) required by face_recognition api
RUN pip install --no-cache-dir numpy==1.26.4 pillow>=10.2.0

# Compile dlib strictly with 1 thread
RUN CMAKE_BUILD_PARALLEL_LEVEL=1 pip install --no-cache-dir dlib==19.24.4

# Install official models package
RUN pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition_models

# Install face-recognition
RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

# Verify face_recognition imports successfully right inside the build step!
RUN python -c "import face_recognition; print(' Face Recognition Engine Ready!')"

# Copy and install application requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ .
COPY frontend/ ./frontend/

# Run collectstatic for static assets
RUN python manage.py collectstatic --noinput || true

# Render dynamically assigns the PORT environment variable
EXPOSE 8000

# Run migrations and launch Daphne ASGI server
CMD ["sh", "-c", "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} smart_attendance.asgi:application"]
