# Use an official lightweight Python image
FROM python:3.8-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Start the server using a basic Python HTTP server on port 3000
CMD python -m http.server 3000 --directory /var/www
