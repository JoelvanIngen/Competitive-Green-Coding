FROM python:3.12-slim

ARG HOST_DOCKER_GID

RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid appgroup appuser

RUN groupadd --system --gid "$HOST_DOCKER_GID" docker && \
    usermod -aG docker appuser

# No .pyc files (won't invalidate cache on code change) and unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir -p /app && chown appuser:appgroup /app
RUN mkdir -p /runtimes && chown appuser:appgroup /runtimes

COPY ./execution_engine/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

RUN apt update && \
    apt install curl --no-install-recommends -y

COPY ./execution_engine/requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY ./execution_engine/src/ .
COPY ./common_python_modules/ .

RUN chown -R appuser:appgroup /app

USER appuser

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "execution_engine.main"]
