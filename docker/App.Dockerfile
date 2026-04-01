FROM python:3.11
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
ENV PIP_PREFER_BINARY=1
ENV PIP_NO_CACHE_DIR=1
COPY docker/requirements.app.txt .
RUN pip install --only-binary=:all: -r requirements.app.txt
COPY app/ ./app/
CMD ["python", "app/start.py"]