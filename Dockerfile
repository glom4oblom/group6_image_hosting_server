FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser

RUN mkdir -p /images /app/backups && chown -R appuser:appuser /images /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY scripts/ /app/scripts/

RUN chown -R appuser:appuser /app

USER appuser
WORKDIR /app

EXPOSE 8000

CMD ["python", "src/app.py"]