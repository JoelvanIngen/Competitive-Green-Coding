FROM python:3.12
WORKDIR /usr/local/app

apt-get update && apt-get install -y gcc 

COPY test_code.py

CMD ["python", "test_code.py"]