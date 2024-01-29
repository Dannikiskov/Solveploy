FROM python:3.12.1-bookworm AS python

WORKDIR /app

COPY requirements.txt .


FROM minizinc/minizinc:latest AS minizinc

WORKDIR /app

COPY --from=python /usr/local/bin/python /usr/local/bin/python
COPY --from=python /usr/lib/x86_64-linux-gnu  /usr/lib/x86_64-linux-gnu 
COPY --from=python /usr/local/lib /usr/local/lib
COPY . .

RUN python -m pip install -r requirements.txt

CMD ["python3", "src/main.py"]
