FROM python:3.10-slim

WORKDIR /app

COPY ./app /app/app

RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch torchvision \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy psycopg2-binary \
    passlib[argon2] python-jose[cryptography] python-multipart \
    email-validator slowapi Pillow pillow-heif requests \
    opencv-python-headless==4.8.1.78 \
    mediapipe==0.10.8 \
    numpy==1.24.3 \
    httpx beautifulsoup4 lxml \
    celery redis \
    alembic \
    timm

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
