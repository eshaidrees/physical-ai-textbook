#!/bin/bash

# Deployment script for Physical AI & Humanoid Robotics textbook backend
# This script builds and deploys the FastAPI application

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting deployment of Physical AI & Humanoid Robotics textbook backend..."

# Build the Docker image
echo "Building Docker image..."
docker build -t physical-ai-textbook-backend .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
else
    echo "Docker build failed! Exiting..."
    exit 1
fi

# Tag the image for your container registry (replace with your registry)
echo "Tagging Docker image..."
docker tag physical-ai-textbook-backend your-registry/physical-ai-textbook-backend:latest

# Push the image to the container registry (uncomment when ready)
# echo "Pushing image to container registry..."
# docker push your-registry/physical-ai-textbook-backend:latest

# Run the container locally for testing (remove when deploying to cloud)
echo "Running container locally for testing..."
docker run -d -p 8000:8000 --name physical-ai-textbook-backend-container physical-ai-textbook-backend

echo "Backend deployment completed!"
echo "The API should be available at: http://localhost:8000"
echo "API documentation available at: http://localhost:8000/docs"

# Instructions for the user
echo ""
echo "Important notes:"
echo "1. For production deployment, replace 'your-registry' with your actual container registry"
echo "2. Consider using a cloud platform like AWS, GCP, or Azure for hosting"
echo "3. For Qdrant, you may need to set up a separate instance or use Qdrant Cloud"
echo "4. Update the API endpoints in the frontend to point to your deployed backend"
echo ""
echo "For cloud deployment options:"
echo "- AWS ECS: Deploy the container to Amazon ECS"
echo "- Google Cloud Run: Deploy as a managed service"
echo "- Azure Container Instances: Deploy the container directly"
echo "- Heroku: Use the container registry support"
echo "- Railway: Easy deployment platform for containers"