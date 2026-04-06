FROM python:3.11
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
COPY docker/backend/requirements.txt .
RUN pip install -r requirements.txt
COPY src/Backend/ ./app/
CMD ["fastapi", "run", "./app/main.py"]