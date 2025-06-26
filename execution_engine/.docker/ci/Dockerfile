FROM python:3.12-slim

ARG HOST_DOCKER_GID
ARG HOST_USER_UID

RUN groupadd --system --gid "$HOST_DOCKER_GID" appgroup && \
    useradd --system --uid "$HOST_USER_UID" --gid appgroup appuser

# No .pyc files (won't invalidate cache on code change) and unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir -p /app && chown appuser:appgroup /app
RUN mkdir -p /runtimes && chown appuser:appgroup /runtimes

RUN apt update && \
    apt install curl --no-install-recommends -y

COPY ./execution_engine/requirements.txt .
COPY ./execution_engine/requirements.ci.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.ci.txt

COPY ./execution_engine/src/ .
COPY ./execution_engine/tests/ tests/
COPY ./common_python_modules/ .

RUN chown -R appuser:appgroup /app

USER appuser

ENTRYPOINT ["python", "-m", "execution_engine.main"]
