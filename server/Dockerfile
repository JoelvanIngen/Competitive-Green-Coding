FROM python:3.12
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup appuser

COPY src/* .

RUN chown -R appuser:appgroup /app

USER appuser

ENTRYPOINT ["python", "-m", "server.main"]