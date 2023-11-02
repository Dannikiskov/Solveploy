# Use an official Node.js runtime as a base image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json into the container
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy the entire app into the container
COPY . .

# Expose the port your app will run on
EXPOSE 5173

# Start the React app
CMD ["npm", "run", "dev"]
