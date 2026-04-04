FROM python:3.11
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
COPY docker/requirements.app.txt .
RUN pip install -r requirements.app.txt
COPY app/ ./app/
CMD ["python", "app/start.py"]