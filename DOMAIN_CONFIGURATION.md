# Domain Configuration for Physical AI & Humanoid Robotics Textbook

This document provides instructions for configuring custom domains for both the frontend and backend of the textbook application.

## Frontend Domain Configuration (GitHub Pages)

### Option 1: Subdomain (e.g., textbook.yourdomain.com)
1. In your domain registrar's DNS settings, add a CNAME record:
   - Name/Host: `textbook`
   - Type: `CNAME`
   - Value/Points to: `your-username.github.io`

2. In your GitHub repository settings:
   - Go to Settings > Pages
   - Under "Custom domain", enter `textbook.yourdomain.com`
   - Click "Save"
   - Ensure "Enforce HTTPS" is checked

### Option 2: apex domain (e.g., yourdomain.com)
1. In your domain registrar's DNS settings, add A records:
   - @ 185.199.108.153
   - @ 185.199.109.153
   - @ 185.199.110.153
   - @ 185.199.111.153

2. In your GitHub repository settings:
   - Go to Settings > Pages
   - Under "Custom domain", enter `yourdomain.com`
   - Click "Save"
   - Ensure "Enforce HTTPS" is checked

### Option 3: www subdomain (e.g., www.yourdomain.com)
1. In your domain registrar's DNS settings, add a CNAME record:
   - Name/Host: `www`
   - Type: `CNAME`
   - Value/Points to: `your-username.github.io`

2. In your GitHub repository settings:
   - Go to Settings > Pages
   - Under "Custom domain", enter `www.yourdomain.com`
   - Click "Save"
   - Ensure "Enforce HTTPS" is checked

## Backend Domain Configuration

### Using a Subdomain for the API (e.g., api.textbook.yourdomain.com)
1. Add a CNAME record in your DNS settings:
   - Name/Host: `api.textbook` (or similar)
   - Type: `CNAME`
   - Value/Points to: Your cloud provider's domain (e.g., `ab12c3d4567890.dkr.ecr.us-east-1.amazonaws.com`)

### Updating Frontend to Use Custom Backend Domain

After configuring your backend domain, update the API endpoints in the frontend:

1. In `website/src/components/ChatInterface.js`, change:
   ```javascript
   const response = await fetch('http://localhost:8000/chat', {
   ```
   to:
   ```javascript
   const response = await fetch('https://api.textbook.yourdomain.com/chat', {
   ```

2. Update other API calls in the same file:
   ```javascript
   // Change embed endpoint
   const embedResponse = await fetch('http://localhost:8000/embed', {
   // to
   const embedResponse = await fetch('https://api.textbook.yourdomain.com/embed', {

   // Change query endpoint
   const queryResponse = await fetch('http://localhost:8000/query', {
   // to
   const queryResponse = await fetch('https://api.textbook.yourdomain.com/query', {
   ```

## SSL Certificate Configuration

GitHub Pages automatically provides SSL certificates for custom domains. For your backend:

### Using Cloud Provider's SSL
- AWS: Use AWS Certificate Manager (ACM)
- GCP: Use Google-managed SSL certificates
- Azure: Use Azure Key Vault or App Service managed certificates

### Using Let's Encrypt
If self-hosting, you can use Let's Encrypt for free SSL certificates:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Testing Domain Configuration

After configuration, test that everything works:

1. Visit your frontend domain: `https://textbook.yourdomain.com`
2. Test the chat functionality to ensure it connects to your backend
3. Verify that all links and resources load correctly
4. Check that the API endpoints are accessible from the frontend domain

## Troubleshooting

### DNS Propagation
DNS changes can take up to 48 hours to propagate globally. Use tools like:
- https://www.whatsmydns.net/
- `nslookup yourdomain.com`

### SSL Certificate Issues
- Wait for SSL certificates to be issued (can take 1-2 hours)
- Check that your DNS records are correctly configured
- Verify that "Enforce HTTPS" is enabled in GitHub Pages settings

### API Connection Issues
- Ensure CORS settings allow requests from your frontend domain
- Check that your backend domain is accessible
- Verify that SSL certificates are properly configured

## Updating Docusaurus Configuration

After setting up your custom domain, update the `docusaurus.config.ts` file:

```typescript
const config: Config = {
  // ...
  url: 'https://textbook.yourdomain.com',  // Your custom domain
  baseUrl: '/',
  // ...
};
```

Then rebuild and redeploy your frontend.