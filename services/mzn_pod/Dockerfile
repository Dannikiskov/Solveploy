# Use the base image
FROM solveploy-backend-base-image:latest

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt

# Copy the entire app into the container
COPY . .

# Start the Python app
CMD ["python", "src/main.py"]