FROM python:3.11
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
COPY docker/requirements.backend.txt .
RUN pip install -r requirements.backend.txt
COPY docker/backend_runner.sh /usr/local/bin/backend_runner.sh
RUN chmod +x /usr/local/bin/backend_runner.sh
COPY Backend/ ./app/
CMD ["/usr/local/bin/backend_runner.sh"]