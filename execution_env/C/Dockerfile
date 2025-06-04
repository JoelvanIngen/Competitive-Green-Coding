FROM gcc:latest

# working directory
WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y time coreutils

# Copy required files into the container
COPY run.sh .
COPY submitted_code.c .
COPY input.txt .

# executable permissions for the script
RUN chmod +x run.sh

CMD ["./run.sh"]