FROM dannikiskov/solveploy-base:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN wget https://github.com/audemard/glucose/archive/refs/tags/4.2.1.tar.gz
RUN tar -xzf 4.2.1.tar.gz
WORKDIR /app/glucose-4.2.1/parallel
RUN make
ENV PATH="/app/glucose-4.2.1/parallel:$PATH"
WORKDIR /app

CMD ["python", "src/main.py"]