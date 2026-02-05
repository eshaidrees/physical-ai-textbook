# Deployment Guide for RAG Chatbot

This document provides instructions for deploying the RAG Chatbot for Physical AI & Humanoid Robotics Book to various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Health Checks](#health-checks)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the application, ensure you have:

- Docker and Docker Compose installed
- Access to Qdrant vector database (local or cloud)
- API keys for required services (Cohere, etc.)
- Sufficient system resources (minimum 4GB RAM recommended)

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Qdrant Configuration
QDRANT_URL=your-qdrant-url
QDRANT_CLUSTER_ID=your-qdrant-cluster-id

# API Keys
COHERE_API_KEY=your-cohere-api-key

# Database
NEON_DB_URL=your-neon-db-url

# Application Settings
LOG_LEVEL=INFO
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. Build and start the services:
   ```bash
   docker-compose up --build -d
   ```

2. Verify the services are running:
   ```bash
   docker-compose ps
   ```

3. Check logs for any errors:
   ```bash
   docker-compose logs -f
   ```

### Using the Deployment Script

The project includes an automated deployment script:

```bash
# Deploy to staging environment
./.specify/scripts/deploy.sh --environment staging

# Deploy to production environment
./.specify/scripts/deploy.sh --environment production --domain your-domain.com --tls

# Deploy with custom image tag
./.specify/scripts/deploy.sh --environment staging --tag v1.0.0
```

## Manual Deployment

### Backend Service

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Service

1. Install Node.js dependencies:
   ```bash
   cd frontend_book
   npm install
   ```

2. Build and serve the application:
   ```bash
   npm run build
   npx serve -s build
   ```

## Environment-Specific Configuration

### Development
- Use local Qdrant instance
- Enable debug logging
- Use hot-reloading for development

### Staging
- Use staging Qdrant cluster
- Moderate logging levels
- Run integration tests before deployment

### Production
- Use production Qdrant cluster
- Optimize for performance
- Enable comprehensive monitoring
- Use TLS/SSL certificates

## Health Checks

The application provides a health check endpoint:
- `GET /api/v1/health` - Returns the health status of the backend service

## Monitoring

### Backend Metrics
- Response times
- Error rates
- Active conversations
- Vector store performance

### Frontend Metrics
- Page load times
- User engagement
- Error tracking

## Troubleshooting

### Common Issues

1. **Connection to Qdrant fails**
   - Verify QDRANT_URL and QDRANT_CLUSTER_ID in your .env file
   - Check that the Qdrant service is running and accessible

2. **API requests time out**
   - Ensure all required environment variables are set
   - Check that the vector store has been properly initialized

3. **Docker build fails**
   - Verify Docker is running and has sufficient resources
   - Check that all required files are present

### Log Locations

- Backend logs: `backend/logs/` (if file logging is enabled)
- Docker logs: `docker-compose logs`
- System logs: Check your hosting platform's log management system

## Scaling

### Horizontal Scaling
- The application is designed to be stateless for horizontal scaling
- Session data is stored in the vector database
- Use a load balancer to distribute traffic across multiple instances

### Performance Optimization
- Enable caching for frequently accessed content
- Optimize vector search parameters
- Use CDN for static assets

## Rollback Procedure

To rollback to a previous version:

1. Stop the current deployment:
   ```bash
   docker-compose down
   ```

2. Deploy the previous version:
   ```bash
   docker-compose --tag previous-version up -d
   ```

3. Verify the rollback was successful using health checks.