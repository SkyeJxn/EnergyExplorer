FROM python:3.11
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
WORKDIR /app
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
ENV PIP_PREFER_BINARY=1
ENV PIP_NO_CACHE_DIR=1
COPY docker/requirements.backend.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
	libcblas3 \
	&& rm -rf /var/lib/apt/lists/*
RUN pip install --only-binary=:all: -r requirements.backend.txt
COPY docker/backend_runner.sh /usr/local/bin/backend_runner.sh
RUN chmod +x /usr/local/bin/backend_runner.sh
COPY Backend/ ./app/
CMD ["/usr/local/bin/backend_runner.sh"]