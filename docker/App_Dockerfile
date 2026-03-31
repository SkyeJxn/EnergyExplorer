FROM python:3.11-slim
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
COPY docker/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["python", "app/start.py"]