# Use the base image
FROM solveploy-base:latest

# Copy the entire app into the container
COPY . .

# Install app dependencies
RUN pip install -r requirements.txt

# Start the Python app
CMD ["python", "src/main.py"]