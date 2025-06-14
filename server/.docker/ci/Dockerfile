FROM python:3.12-slim

RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid appgroup appuser

# No .pyc files (won't invalidate cache on code change) and unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir -p /app && chown appuser:appgroup /app

RUN apt update && \
    apt install curl --no-install-recommends -y

COPY ./server/requirements.txt .
COPY ./server/requirements.ci.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.ci.txt

COPY ./server/src/ .
COPY ./common_python_modules/ .

RUN chown -R appuser:appgroup /app

USER appuser

ENTRYPOINT ["python", "-m", "server.main"]
