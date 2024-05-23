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

RUN wget https://github.com/arminbiere/gimsatul/archive/refs/tags/rel-1.1.2.tar.gz
RUN tar -xzf rel-1.1.2.tar.gz
WORKDIR /app/gimsatul-rel-1.1.2
RUN ./configure && make
ENV PATH="/app/gimsatul-rel-1.1.2:$PATH"
WORKDIR /app

CMD ["python", "src/main.py"]