# Deployment and Maintenance Guide for Physical AI & Humanoid Robotics Textbook

This document provides comprehensive instructions for deploying, maintaining, and updating the Physical AI & Humanoid Robotics textbook application.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Process](#deployment-process)
4. [Configuration](#configuration)
5. [Maintenance Procedures](#maintenance-procedures)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)
9. [Backup and Recovery](#backup-and-recovery)
10. [Updates and Scaling](#updates-and-scaling)

## Architecture Overview

The textbook application consists of two main components:

### Frontend (Docusaurus)
- Static site generated with Docusaurus
- Hosted on GitHub Pages
- Contains textbook content and chat interface
- Communicates with backend via API calls

### Backend (FastAPI)
- Python-based API server
- Hosted on cloud platform (AWS, GCP, Azure, etc.)
- Implements RAG (Retrieval-Augmented Generation) functionality
- Uses Qdrant for vector storage
- Integrates sentence-transformers for embeddings

## Prerequisites

### For Frontend Deployment
- Node.js (v18 or higher)
- npm or yarn
- GitHub account with repository access

### For Backend Deployment
- Docker
- Container registry (Docker Hub, AWS ECR, GCP Container Registry, etc.)
- Cloud platform account (for deployment)
- Qdrant instance (local or cloud)

## Deployment Process

### Frontend Deployment to GitHub Pages

1. **Prepare the repository**
   ```bash
   cd website
   npm install
   ```

2. **Update configuration**
   - Edit `docusaurus.config.ts` with your GitHub username and repository name
   - Update the `organizationName` and `projectName` fields

3. **Build and deploy**
   ```bash
   npm run build
   npx docusaurus deploy
   ```

4. **Configure GitHub Pages**
   - Go to repository Settings > Pages
   - Select source as "gh-pages" branch
   - Enable "Enforce HTTPS"

### Backend Deployment

1. **Build the Docker image**
   ```bash
   docker build -t physical-ai-textbook-backend .
   ```

2. **Push to container registry**
   ```bash
   docker tag physical-ai-textbook-backend your-registry/physical-ai-textbook-backend:latest
   docker push your-registry/physical-ai-textbook-backend:latest
   ```

3. **Deploy to cloud platform**
   - AWS ECS: Create task definition and service
   - Google Cloud Run: `gcloud run deploy textbook-backend --image your-registry/physical-ai-textbook-backend --platform managed`
   - Azure: Deploy to Container Instances or App Service

4. **Configure Qdrant**
   - For production, use Qdrant Cloud or self-hosted Qdrant instance
   - Update backend configuration to point to your Qdrant instance

## Configuration

### Environment Variables

The backend supports the following environment variables:

```bash
# Qdrant Configuration
QDRANT_URL=your-qdrant-instance-url
QDRANT_API_KEY=your-api-key  # If using Qdrant Cloud

# Port Configuration
PORT=8000

# Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Or other model name
```

### Updating API Endpoints

After deployment, update the frontend to use your backend endpoints by modifying:
- `website/src/components/ChatInterface.js`
- Update all API call URLs from `http://localhost:8000` to your deployed backend URL

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- Monitor application availability
- Check error logs
- Verify backup completion

#### Weekly
- Review performance metrics
- Check for security updates
- Test functionality manually

#### Monthly
- Review usage analytics
- Update dependencies
- Perform security audit

### Content Updates

To update textbook content:

1. **Update markdown files in `website/docs/`**
2. **Rebuild the site**
   ```bash
   cd website
   npm run build
   ```
3. **Deploy updates**
   ```bash
   npx docusaurus deploy
   ```

### Embedding New Content

To add new content to the RAG system:

1. **Use the `/embed` endpoint** to add new content to the vector database
2. **Alternatively, update the embedding script** to process new content

Example API call:
```bash
curl -X POST "https://your-backend-domain/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "New content to embed",
    "source": "Chapter X: Topic Name"
  }'
```

## Monitoring and Logging

### Frontend Monitoring
- GitHub Pages provides basic metrics
- Consider adding Google Analytics or similar
- Monitor page load times and user engagement

### Backend Monitoring
- Monitor API response times
- Track error rates
- Monitor resource usage (CPU, memory)
- Set up alerts for failures

### Logging Configuration
The backend logs important events to stdout. For production:

1. **Implement structured logging** if needed
2. **Set up log aggregation** with your cloud provider
3. **Configure log retention policies**

## Troubleshooting

### Common Issues and Solutions

#### Frontend Issues
- **Chat interface not connecting to backend**: Check CORS settings and API endpoints
- **Slow page loads**: Optimize images and enable compression
- **Translation issues**: Verify locale configuration

#### Backend Issues
- **API timeouts**: Check Qdrant connectivity and performance
- **High memory usage**: Monitor embedding model memory requirements
- **Slow responses**: Optimize vector search and consider indexing

#### Deployment Issues
- **Build failures**: Verify dependencies and Node.js version
- **Docker build failures**: Check Dockerfile and base image compatibility
- **DNS issues**: Verify domain configuration and propagation

### Debugging Commands

#### Frontend
```bash
# Local development
cd website
npm start

# Check build
npm run build
```

#### Backend
```bash
# Run locally
python main.py

# Or with uvicorn
uvicorn main:app --reload --port 8000
```

## Security Considerations

### API Security
- Implement rate limiting
- Use HTTPS for all communications
- Validate and sanitize all inputs
- Implement proper authentication if needed

### Data Security
- Encrypt sensitive data in transit
- Secure Qdrant instance with authentication
- Regularly update dependencies

### Access Control
- Limit access to administrative functions
- Implement proper authentication for content updates
- Use environment variables for sensitive configuration

## Backup and Recovery

### Frontend Backup
- The site is hosted on GitHub Pages, so the repository serves as backup
- Ensure all content is committed to version control

### Backend Backup
- Regularly backup Qdrant data
- Maintain Docker image backups
- Keep deployment configurations in version control

### Recovery Procedures
1. **Restore from GitHub repository** for frontend
2. **Rebuild and redeploy Docker image** for backend
3. **Restore Qdrant data** from latest backup
4. **Update DNS records** if needed

## Updates and Scaling

### Updating the Application

#### Frontend Updates
1. Make changes to content or configuration
2. Run `npm run build`
3. Run `npx docusaurus deploy`

#### Backend Updates
1. Update the code in `main.py`
2. Rebuild Docker image
3. Push new image to registry
4. Update deployment with new image

### Scaling Considerations

#### Horizontal Scaling
- Deploy multiple backend instances behind a load balancer
- Use managed services that auto-scale (like Google Cloud Run)
- Consider using a managed Qdrant service for better scaling

#### Vertical Scaling
- Increase instance size for higher performance
- Optimize embedding model for performance vs. quality trade-off
- Consider caching frequently accessed content

### Performance Optimization

#### Frontend Optimization
- Enable gzip compression
- Optimize images with the ideal-image plugin
- Minimize bundle size
- Use CDN for static assets

#### Backend Optimization
- Optimize vector search with proper indexing
- Implement caching for frequent queries
- Monitor and optimize embedding model performance
- Consider using a lighter embedding model for better performance

## Contact and Support

For issues with deployment or maintenance:
- Check the GitHub repository for known issues
- Review logs for error details
- Contact the development team if issues persist