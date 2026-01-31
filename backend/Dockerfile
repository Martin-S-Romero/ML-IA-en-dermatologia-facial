FROM python:3.10-slim

WORKDIR /app

COPY ./app /app/app

# Install basic dependencies (no requirements.txt yet for simplicity in this phase)
RUN pip install fastapi uvicorn

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
