FROM python:3.12
WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y gcc time

COPY test_code.py

CMD ["python3", "test_code.py"]