FROM gcc:14.3

RUN apt update && \
    apt install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    python3.12-venv && \
    rm -rf /var/lib/apt/lists/*
RUN python3.12 -m pip install --upgrade pip
RUN python3.12 -m pip install codecarbon
