FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/focus_engine
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

WORKDIR /app
ENV PYTHONPATH=/app:/app/focus_engine

EXPOSE 8000

CMD ["uvicorn", "focus_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
