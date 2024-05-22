# Use the base image
FROM solveploy-base:latest

WORKDIR /app
# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt

# Copy the entire app into the container
COPY . .

RUN wget https://github.com/audemard/glucose/archive/refs/tags/4.2.1.tar.gz
RUN tar -xzf 4.2.1.tar.gz
WORKDIR /app/glucose-4.2.1/parallel
RUN make
ENV PATH="/app/glucose-4.2.1/parallel:$PATH"
WORKDIR /app

# Start the Python app
CMD ["python", "src/main.py"]