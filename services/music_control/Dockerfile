FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/music_control
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

WORKDIR /app
ENV PYTHONPATH=/app

EXPOSE 8004

CMD ["uvicorn", "music_control.main:app", "--host", "0.0.0.0", "--port", "8004"]
