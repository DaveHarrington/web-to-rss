# Define the image name
IMAGE_NAME=web-to-rss-app

# Default target executed
all: build run

# Target for building the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Target for running the Docker image
run:
	docker run -p 3000:3000 -v /var/www:/var/www $(IMAGE_NAME)

# Help target to display makefile usage
help:
	@echo "Makefile commands:"
	@echo "make build - Build the Docker image"
	@echo "make run   - Run the Docker container"
	@echo "make all   - Build and run the Docker image"

