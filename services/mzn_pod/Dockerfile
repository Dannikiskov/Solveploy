FROM dannikiskov/solveploy-base:latest

COPY requirements.txt .

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]