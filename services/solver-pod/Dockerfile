# Stage 1: Build stage
FROM minizinc/minizinc:latest

WORKDIR /app

COPY . .

RUN apt update -y && \
    apt install -y python3 python3-pip && \
    python3 -m pip install -r requirements.txt

CMD ["python3", "src/main.py"]
