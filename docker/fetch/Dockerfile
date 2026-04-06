FROM python:3.11-slim
LABEL maintainer="Skye Jonczik <skye.jonczik@proton.me>"
RUN pip install requests
COPY docker/fetch/runner.py .
CMD ["python", "runner.py"]