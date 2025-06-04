FROM gcc:14.3.0

RUN apt update && apt install -y time coreutils

# Create non-root user and group for security
RUN groupadd --system --gid 1000 runuser && \
    useradd --system --uid 1000 --gid appuser --shell /bin/bash appuser

# Working directory
WORKDIR /app

# Copy required files into the container
COPY run.sh .
COPY submitted_code.c .
COPY input.txt .

# Executable permissions for the script
RUN chmod +x run.sh

CMD ["./run.sh"]