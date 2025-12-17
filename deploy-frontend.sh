#!/bin/bash

# Deployment script for Physical AI & Humanoid Robotics textbook frontend
# This script builds and deploys the Docusaurus site to GitHub Pages

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting deployment of Physical AI & Humanoid Robotics textbook frontend..."

# Navigate to the website directory
cd website

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the site
echo "Building the site..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed! Exiting..."
    exit 1
fi

# Deploy to GitHub Pages
echo "Deploying to GitHub Pages..."
npx docusaurus deploy

echo "Frontend deployment completed successfully!"
echo "Your site should be available at: https://your-username.github.io/physical-ai-textbook/"

# Instructions for the user
echo ""
echo "Important notes:"
echo "1. Make sure your GitHub repository is set up for GitHub Pages"
echo "2. The deployment uses the 'gh-pages' branch by default"
echo "3. You may need to configure GitHub Pages in your repository settings to use the gh-pages branch"
echo "4. If this is your first deployment, you may need to enable GitHub Pages in your repo settings"