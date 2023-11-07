# Use an official Python runtime as a base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y dnsutils


# Copy the entire app into the container
COPY . .

# Expose the port your app will run on
EXPOSE 5000

# Start the Python app
CMD ["python", "src/main.py"]
