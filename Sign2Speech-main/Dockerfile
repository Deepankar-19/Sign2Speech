FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies required by OpenCV / MediaPipe / Nginx
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend
COPY backend /app/backend

# Copy frontend
COPY frontend /var/www/frontend

# Nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Make sure upload directories exist
RUN mkdir -p /app/backend/uploads/tts

# Nginx listens on port 80
EXPOSE 80

WORKDIR /app/backend

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]