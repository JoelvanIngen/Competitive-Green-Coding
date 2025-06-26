FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install codecarbon
