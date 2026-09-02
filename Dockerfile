FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

RUN apt-get update && apt-get install -y --no-install-recommends git libpq5 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-dev.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "pipelines/run_pipeline.py"]
CMD ["--rows", "50000", "--seed", "2026"]
