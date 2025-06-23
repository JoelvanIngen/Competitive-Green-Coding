FROM python:3.12-slim

RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid 1001 appuser

# No .pyc files (won't invalidate cache on code change) and unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir -p /app && chown appuser:appgroup /app
RUN mkdir -p /storage && chown appuser:appgroup /storage

RUN apt update && \
    apt install curl --no-install-recommends -y

COPY ./db/requirements.txt .
COPY ./db/requirements.ci.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.ci.txt

COPY ./db/src/ .
COPY ./db/scripts/ ./scripts
COPY ./db/tests/ tests/
COPY ./common_python_modules/ .
COPY ./storage-example/ /storage/

RUN chown -R appuser:appgroup /app
RUN chown -R appuser:appgroup /storage

USER appuser

ENTRYPOINT ["python", "-m", "db.main"]
