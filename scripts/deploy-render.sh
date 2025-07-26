#!/bin/bash

# Automated Render Deployment Script for Budget Planner
# This script sets up deployment configuration for Render

set -e

echo "🎨 Budget Planner - Render Deployment Setup"
echo "==========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Validate environment variables
print_info "Validating environment variables..."

required_vars=(
    "MONGO_URL"
    "SENDGRID_API_KEY" 
    "JWT_SECRET"
    "SENDER_EMAIL"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Set them before deploying to Render"
    exit 1
fi

print_status "Environment variables ready"

# Create render.yaml configuration
print_info "Creating Render deployment configuration..."

cat > render.yaml << 'EOF'
services:
  # Backend Service
  - type: web
    name: budget-planner-backend
    env: python
    plan: free
    region: oregon
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1"
    healthCheckPath: "/api/health"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: MONGO_URL
        sync: false
      - key: SENDGRID_API_KEY
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: SENDER_EMAIL
        sync: false
      - key: SENDER_NAME
        value: Budget Planner
      - key: ENABLE_EMAIL_SENDING
        value: true
      - key: LOG_LEVEL
        value: INFO
      - key: ACCESS_TOKEN_EXPIRE
        value: 1440
      - key: CORS_ORIGINS
        value: '["https://budget-planner-frontend.onrender.com"]'

  # Frontend Service
  - type: web
    name: budget-planner-frontend
    env: static
    plan: free
    region: oregon
    buildCommand: "yarn install && yarn build"
    staticPublishPath: ./build
    pullRequestPreviewsEnabled: false
    envVars:
      - key: REACT_APP_BACKEND_URL
        value: https://budget-planner-backend.onrender.com
      - key: REACT_APP_ENVIRONMENT
        value: production
      - key: GENERATE_SOURCEMAP
        value: false
    routes:
      - type: rewrite
        source: /api/*
        destination: https://budget-planner-backend.onrender.com/api/:splat
      - type: rewrite
        source: /*
        destination: /index.html

  # Optional: Background Worker for Email Scheduler
  # Uncomment if you want a dedicated worker for email tasks
  # - type: worker
  #   name: budget-planner-scheduler
  #   env: python
  #   plan: free
  #   buildCommand: "pip install -r requirements.txt"
  #   startCommand: "python -c 'from services.email_scheduler import email_scheduler; email_scheduler.start(); import time; time.sleep(86400)'"
  #   envVars:
  #     - key: ENVIRONMENT
  #       value: production
  #     - key: MONGO_URL
  #       sync: false
  #     - key: SENDGRID_API_KEY
  #       sync: false
  #     - key: JWT_SECRET
  #       sync: false
  #     - key: SENDER_EMAIL
  #       sync: false
EOF

print_status "Render configuration created (render.yaml)"

# Create frontend redirects for client-side routing
print_info "Creating frontend redirects configuration..."

cat > frontend/_redirects << 'EOF'
# API routes to backend
/api/* https://budget-planner-backend.onrender.com/api/:splat 200!

# Client-side routing fallback
/* /index.html 200
EOF

print_status "Frontend redirects configured"

# Create backend requirements with gunicorn for better production performance
print_info "Optimizing backend for Render..."

# Add gunicorn to requirements if not present
if ! grep -q "gunicorn" backend/requirements.txt; then
    echo "gunicorn>=21.2.0" >> backend/requirements.txt
    print_status "Added gunicorn to requirements"
fi

# Create optimized startup script
cat > backend/start-render.sh << 'EOF'
#!/bin/bash
# Render startup script with optimizations

# Run database initialization
python -c "
import asyncio
from database import init_db
asyncio.run(init_db())
"

# Start application with gunicorn for better performance
if [ "$ENVIRONMENT" = "production" ]; then
    gunicorn server:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
else
    uvicorn server:app --host 0.0.0.0 --port $PORT
fi
EOF

chmod +x backend/start-render.sh

# Update render.yaml to use the optimized startup script
sed -i 's/startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1"/startCommand: ".\/start-render.sh"/' render.yaml

print_status "Backend optimized for Render"

# Create deployment checklist
print_info "Creating deployment checklist..."

cat > RENDER_DEPLOYMENT_CHECKLIST.md << 'EOF'
# Render Deployment Checklist

## Pre-Deployment Setup

### 1. Repository Setup
- [ ] Commit all changes to your Git repository
- [ ] Push to main/master branch
- [ ] Ensure `render.yaml` is in repository root

### 2. Render Account Setup
- [ ] Create account at [render.com](https://render.com)
- [ ] Connect your GitHub/GitLab repository

### 3. Environment Variables
Set these in Render dashboard for backend service:

**Required Variables:**
- [ ] `MONGO_URL` - Your MongoDB connection string
- [ ] `SENDGRID_API_KEY` - Your SendGrid API key
- [ ] `JWT_SECRET` - Secure JWT secret (32+ characters)
- [ ] `SENDER_EMAIL` - Your verified sender email

**Optional Variables:**
- [ ] `SENDER_NAME` - Display name for emails (default: "Budget Planner")
- [ ] `LOG_LEVEL` - Logging level (default: "INFO")

## Deployment Steps

### 1. Deploy Backend Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your repository
4. Use these settings:
   - **Name**: `budget-planner-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main` or `master`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start-render.sh`
5. Add environment variables listed above
6. Deploy

### 2. Deploy Frontend Service
1. Create another "Web Service"
2. Use these settings:
   - **Name**: `budget-planner-frontend`
   - **Region**: Same as backend
   - **Branch**: `main` or `master`
   - **Root Directory**: `frontend`
   - **Environment**: `Static Site`
   - **Build Command**: `yarn install && yarn build`
   - **Publish Directory**: `build`
3. Add environment variables:
   - `REACT_APP_BACKEND_URL`: Use your backend service URL
   - `REACT_APP_ENVIRONMENT`: `production`
4. Deploy

### 3. Update CORS Settings
1. After frontend deploys, note the frontend URL
2. Update backend environment variable:
   - `CORS_ORIGINS`: `["https://your-frontend-url.onrender.com"]`
3. Redeploy backend service

## Post-Deployment

### 1. Verify Deployment
- [ ] Backend health check: `https://your-backend.onrender.com/api/health`
- [ ] Frontend loads: `https://your-frontend.onrender.com`
- [ ] User can register/login
- [ ] Email system works (test from notifications settings)

### 2. Configure Custom Domain (Optional)
- [ ] Add custom domain in Render dashboard
- [ ] Update DNS settings
- [ ] Update CORS origins

### 3. Monitor Services
- [ ] Check Render dashboard for service health
- [ ] Monitor logs for errors
- [ ] Set up uptime monitoring

## Troubleshooting

### Common Issues
1. **Build Fails**: Check build logs in Render dashboard
2. **Environment Variables**: Ensure all required vars are set
3. **CORS Errors**: Verify CORS_ORIGINS includes frontend URL
4. **Database Connection**: Check MongoDB Atlas IP whitelist
5. **Email Issues**: Verify SendGrid API key and sender email

### Support Resources
- Render Docs: https://render.com/docs
- Community Forum: https://community.render.com
- Status Page: https://status.render.com

## Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- 750 hours/month per service
- Slower builds and cold starts
- Consider upgrading for production use
EOF

print_status "Deployment checklist created"

# Create monitoring script specific to Render
cat > scripts/monitor-render.py << 'EOF'
#!/usr/bin/env python3
"""
Render-specific monitoring script
Handles free tier sleep/wake patterns
"""

import asyncio
import aiohttp
import time
from datetime import datetime

class RenderMonitor:
    def __init__(self, backend_url, frontend_url):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
    
    async def wake_services(self):
        """Wake up sleeping services on Render free tier"""
        print("🌅 Waking up services...")
        
        async with aiohttp.ClientSession() as session:
            # Wake backend
            try:
                async with session.get(f"{self.backend_url}/api/health", timeout=30) as response:
                    if response.status == 200:
                        print("✅ Backend is awake")
                    else:
                        print(f"⚠️  Backend responded with {response.status}")
            except Exception as e:
                print(f"❌ Backend wake failed: {e}")
            
            # Wake frontend
            try:
                async with session.get(self.frontend_url, timeout=30) as response:
                    if response.status == 200:
                        print("✅ Frontend is awake")
                    else:
                        print(f"⚠️  Frontend responded with {response.status}")
            except Exception as e:
                print(f"❌ Frontend wake failed: {e}")
    
    async def keep_alive(self, interval_minutes=10):
        """Keep services alive by pinging them regularly"""
        print(f"🔄 Starting keep-alive (every {interval_minutes} minutes)")
        
        while True:
            await self.wake_services()
            print(f"💤 Sleeping for {interval_minutes} minutes...")
            await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python monitor-render.py <backend_url> <frontend_url>")
        sys.exit(1)
    
    backend_url = sys.argv[1]
    frontend_url = sys.argv[2]
    
    monitor = RenderMonitor(backend_url, frontend_url)
    
    if len(sys.argv) > 3 and sys.argv[3] == "--keep-alive":
        asyncio.run(monitor.keep_alive())
    else:
        asyncio.run(monitor.wake_services())
EOF

chmod +x scripts/monitor-render.py

print_status "Render monitoring script created"

# Summary
echo ""
print_status "Render deployment setup completed! 🎉"
echo ""
echo "📋 What's been created:"
echo "   ✅ render.yaml - Main deployment configuration"
echo "   ✅ frontend/_redirects - Client-side routing"
echo "   ✅ backend/start-render.sh - Optimized startup script"
echo "   ✅ RENDER_DEPLOYMENT_CHECKLIST.md - Step-by-step guide"
echo "   ✅ scripts/monitor-render.py - Service monitoring"
echo ""
echo "🚀 Next Steps:"
echo "   1. Commit and push these files to your repository"
echo "   2. Follow RENDER_DEPLOYMENT_CHECKLIST.md"
echo "   3. Deploy backend service first, then frontend"
echo "   4. Update CORS settings with frontend URL"
echo ""
echo "📚 Resources:"
echo "   - Deployment Guide: RENDER_DEPLOYMENT_CHECKLIST.md"
echo "   - Render Dashboard: https://dashboard.render.com"
echo "   - Monitor Services: python scripts/monitor-render.py <backend> <frontend>"
echo ""
print_info "Ready for Render deployment!"