FROM python:3.10-slim

WORKDIR /app

COPY ./app /app/app

# Install basic dependencies
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[argon2] python-jose[cryptography] python-multipart email-validator slowapi

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
