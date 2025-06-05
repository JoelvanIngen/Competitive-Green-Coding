FROM python:3.12
WORKDIR /app

COPY . .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup appuser

RUN chown -R appuser:appgroup /app

USER appuser

WORKDIR /app/src

ENTRYPOINT ["python", "-m", "exection_engine.main"]
