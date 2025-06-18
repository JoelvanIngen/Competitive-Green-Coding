FROM python:3.12-slim

ARG UID=1001
ARG GID=1001

RUN groupadd --system --gid ${GID} appgroup && \
    useradd --system --uid ${UID} --gid ${GID} appuser

# No .pyc files (won't invalidate cache on code change) and unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir -p /app && chown appuser:appgroup /app
RUN mkdir -p /storage && chown appuser:appgroup /storage

RUN apt update && \
    apt install curl --no-install-recommends -y

COPY ./db/requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY ./db/src/ .
COPY ./common_python_modules/ .
COPY ./storage-example/ /storage/

RUN chown -R appuser:appgroup /app
RUN chown -R appuser:appgroup /storage

USER appuser

ENTRYPOINT ["python", "-m", "db.main"]
