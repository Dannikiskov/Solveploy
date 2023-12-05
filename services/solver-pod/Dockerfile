FROM python:latest

#ENV rabbitmqusername=$rabbitmqusername
#ENV rabbitmqpassword=$rabbitmqpassword

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
