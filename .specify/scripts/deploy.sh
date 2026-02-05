#!/bin/bash

# Deployment script for RAG Chatbot for Physical AI & Humanoid Robotics Book
# This script automates the deployment process to various environments

set -e  # Exit on any error

# Default configuration
ENVIRONMENT="staging"
DOCKER_REGISTRY=""
IMAGE_NAME="rag-chatbot"
TAG="latest"
DOMAIN_NAME=""
USE_TLS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -e, --environment ENV     Deploy to specified environment (default: staging)"
    echo "  -r, --registry REGISTRY   Docker registry URL"
    echo "  -t, --tag TAG            Docker image tag (default: latest)"
    echo "  -d, --domain DOMAIN      Domain name for the deployment"
    echo "  --tls                    Enable TLS/SSL"
    echo "  --help                   Display this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -d|--domain)
            DOMAIN_NAME="$2"
            shift 2
            ;;
        --tls)
            USE_TLS=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "development" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Use staging, production, or development."
    exit 1
fi

print_status "Starting deployment to $ENVIRONMENT environment"

# Check if required tools are available
command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { print_error "Docker Compose is required but not installed. Aborting."; exit 1; }

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    print_warning ".env file not found. Please ensure all required environment variables are set."
fi

# Build the Docker images
print_status "Building Docker images..."
if [[ -n "$DOCKER_REGISTRY" ]]; then
    IMAGE_TAG="$DOCKER_REGISTRY/$IMAGE_NAME:$TAG"
else
    IMAGE_TAG="$IMAGE_NAME:$TAG"
fi

# Build backend image
print_status "Building backend image..."
docker build -t $IMAGE_TAG -f Dockerfile .

# Build frontend image
print_status "Building frontend image..."
cd frontend_book
docker build -t ${IMAGE_TAG}-frontend -f Dockerfile .
cd ..

# Tag images for registry if specified
if [[ -n "$DOCKER_REGISTRY" ]]; then
    docker tag $IMAGE_TAG $DOCKER_REGISTRY/$IMAGE_NAME:$TAG
    docker tag ${IMAGE_TAG}-frontend $DOCKER_REGISTRY/${IMAGE_NAME}-frontend:$TAG
fi

# Push images to registry if specified
if [[ -n "$DOCKER_REGISTRY" ]]; then
    print_status "Pushing images to registry..."
    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$TAG
    docker push $DOCKER_REGISTRY/${IMAGE_NAME}-frontend:$TAG
fi

# Update docker-compose.yml with environment-specific settings
print_status "Configuring docker-compose for $ENVIRONMENT environment..."

# Create environment-specific docker-compose override file
cat > docker-compose.$ENVIRONMENT.yml << EOF
version: '3.8'

services:
  backend:
    image: ${IMAGE_TAG}
    environment:
      - ENVIRONMENT=$ENVIRONMENT
      - LOG_LEVEL=INFO
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    restart: unless-stopped

  frontend:
    image: ${IMAGE_TAG}-frontend
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF

# For production, add additional security and performance configurations
if [[ "$ENVIRONMENT" == "production" ]]; then
    print_status "Applying production-specific configurations..."

    # Add security configurations
    cat >> docker-compose.$ENVIRONMENT.yml << EOF

  # Optional: Add a reverse proxy like nginx for production
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
EOF
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down || true

# Start the services with environment-specific configuration
print_status "Starting services for $ENVIRONMENT environment..."
if [[ "$ENVIRONMENT" == "production" ]]; then
    docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml up -d --remove-orphans
else
    docker-compose -f docker-compose.yml -f docker-compose.$ENVIRONMENT.yml up -d
fi

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Run health checks
print_status "Running health checks..."
for i in {1..10}; do
    if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        print_status "Backend service is healthy"
        break
    else
        print_warning "Backend not ready, waiting... ($i/10)"
        sleep 5
    fi
done

# Check frontend
for i in {1..10}; do
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_status "Frontend service is healthy"
        break
    else
        print_warning "Frontend not ready, waiting... ($i/10)"
        sleep 5
    fi
done

# Run basic functionality test
print_status "Running basic functionality test..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello", "conversation_id":"test_deployment"}' || echo "FAILED")

if [[ "$TEST_RESPONSE" != "FAILED" && -n "$TEST_RESPONSE" ]]; then
    print_status "Deployment test successful"
else
    print_error "Deployment test failed"
    exit 1
fi

# Display deployment summary
print_status "Deployment completed successfully!"
echo
echo "Environment: $ENVIRONMENT"
echo "Backend URL: http://localhost:8000"
echo "Frontend URL: http://localhost:3000"
if [[ -n "$DOMAIN_NAME" ]]; then
    echo "Domain: $DOMAIN_NAME"
fi
echo "Image Tag: $TAG"
echo

# Cleanup temporary files
rm -f docker-compose.$ENVIRONMENT.yml

print_status "Deployment process completed!"