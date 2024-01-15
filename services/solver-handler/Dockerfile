# Use an official Python runtime as a base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt

RUN wget https://github.com/MiniZinc/MiniZincIDE/releases/download/2.8.2/MiniZincIDE-2.8.2-bundle-linux-x86_64.tgz
RUN tar -xzf MiniZincIDE-2.8.2-bundle-linux-x86_64.tgz
RUN rm MiniZincIDE-2.8.2-bundle-linux-x86_64.tgz
ENV PATH="/app/MiniZincIDE-2.8.2-bundle-linux-x86_64/bin:$PATH"
RUN echo $PATH

# Copy the entire app into the container
COPY . .

# Expose the port your app will run on
EXPOSE 5001

# Start the Python app
CMD ["minizinc", "--help"]
