FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt update && apt install -y wget \
    && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

RUN chmod +x start.sh
CMD ["sh", "start.sh"]
