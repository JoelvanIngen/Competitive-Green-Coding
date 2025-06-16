FROM gcc:14.3.0

RUN apt update && apt install -y time coreutils

# Create non-root user and group for security
RUN groupadd --system --gid 1001 appuser && \
    useradd --system --uid 1001 --gid appuser --shell /bin/bash appuser

# Working directory
WORKDIR /app

# Copy required files into the container
COPY run.sh .
COPY submitted_code.c .
COPY input.txt .

# Make non-root user own /app
RUN chown -R appuser:appuser /app

# Executable permissions for the script
RUN chmod +x run.sh

# Switch user
USER appuser

CMD ["./run.sh"]