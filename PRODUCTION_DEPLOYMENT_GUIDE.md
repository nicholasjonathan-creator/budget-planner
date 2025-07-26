# 🚀 Budget Planner Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Budget Planner application to production. The application features a React frontend, FastAPI backend, MongoDB database, and automated email system with SendGrid integration.

## 📋 Prerequisites

### Required Accounts
- **MongoDB Atlas** account for production database
- **SendGrid** account for email notifications
- **Domain registrar** for custom domain (optional but recommended)
- **Hosting platform** account (Railway, Render, Vercel, or cloud provider)

### Required Tools
- Node.js 18+ and Yarn
- Python 3.11+
- Docker (for containerized deployment)
- Git

## 🔧 Environment Configuration

### 1. Required Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Environment
ENVIRONMENT=production
NODE_ENV=production

# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/budget_planner?retryWrites=true&w=majority
DB_NAME=budget_planner

# Authentication
JWT_SECRET=your-super-secure-jwt-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE=1440

# Email Configuration
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true

# Security
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
LOG_LEVEL=INFO

# Application
APP_VERSION=1.0.0
DEPLOYMENT_DATE=2025-01-26T12:00:00Z
```

### 2. Frontend Environment Variables

Create `frontend/.env.production`:

```bash
REACT_APP_BACKEND_URL=https://your-backend-domain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

## 🛠️ Pre-Deployment Setup

### 1. SendGrid Configuration

1. **Create SendGrid Account**
   - Sign up at [sendgrid.com](https://sendgrid.com)
   - Verify your email address

2. **Generate API Key**
   - Go to Settings → API Keys
   - Create API Key with "Full Access" permissions
   - Copy the API key to `SENDGRID_API_KEY`

3. **Sender Verification**
   - Go to Settings → Sender Authentication
   - Add and verify your sender email address
   - This email must match `SENDER_EMAIL` in environment variables

4. **Domain Authentication (Recommended)**
   - Go to Settings → Sender Authentication → Domain Authentication
   - Follow DNS setup instructions for your domain
   - This improves email deliverability

### 2. MongoDB Atlas Setup

1. **Create MongoDB Atlas Cluster**
   - Sign up at [mongodb.com/atlas](https://www.mongodb.com/atlas)
   - Create a free M0 cluster
   - Choose a region close to your hosting location

2. **Configure Database Access**
   - Create database user with read/write permissions
   - Add IP addresses to whitelist (0.0.0.0/0 for any IP, or specific IPs)

3. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy connection string to `MONGO_URL`

### 3. Security Configuration

1. **Generate JWT Secret**
   ```bash
   openssl rand -base64 32
   ```

2. **Configure CORS Origins**
   - Update `CORS_ORIGINS` with your actual domain(s)
   - Include both www and non-www versions if applicable

## 🚀 Deployment Options

### Option 1: Railway Deployment (Recommended)

Railway provides easy deployment with automatic builds and deployments.

#### Backend Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**
   ```bash
   railway login
   railway init
   ```

3. **Deploy Backend**
   ```bash
   cd backend
   railway up
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set MONGO_URL="your-mongo-url"
   railway variables set SENDGRID_API_KEY="your-sendgrid-key"
   railway variables set JWT_SECRET="your-jwt-secret"
   railway variables set SENDER_EMAIL="your-sender-email"
   railway variables set ENVIRONMENT="production"
   ```

#### Frontend Deployment

1. **Create Frontend Service**
   ```bash
   cd frontend
   railway init
   railway up
   ```

2. **Set Environment Variables**
   ```bash
   railway variables set REACT_APP_BACKEND_URL="https://your-backend.railway.app"
   railway variables set REACT_APP_ENVIRONMENT="production"
   ```

### Option 2: Render Deployment

Render provides free hosting with automatic SSL certificates.

#### Backend Deployment

1. **Connect Repository**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Create new "Web Service"

2. **Configure Build Settings**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

3. **Set Environment Variables**
   - Add all production environment variables in Render dashboard

#### Frontend Deployment

1. **Create Static Site**
   - Create new "Static Site" in Render
   - **Build Command**: `yarn install && yarn build`
   - **Publish Directory**: `build`
   - **Root Directory**: `frontend`

2. **Configure Redirects**
   Create `frontend/_redirects`:
   ```
   /api/* https://your-backend.onrender.com/api/:splat 200
   /* /index.html 200
   ```

### Option 3: Vercel + Railway

Deploy frontend to Vercel and backend to Railway for optimal performance.

#### Frontend on Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Environment Variables**
   - Add `REACT_APP_BACKEND_URL` in Vercel dashboard

#### Backend on Railway
Follow Railway backend deployment steps above.

### Option 4: Docker Deployment

For self-hosted or cloud provider deployment.

1. **Build and Run**
   ```bash
   # Copy environment file
   cp .env.production .env
   
   # Build and start services
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Configure Reverse Proxy**
   Set up nginx or similar to route traffic:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /api/ {
           proxy_pass http://localhost:8001;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

## 🔍 Post-Deployment Verification

### 1. Run Health Checks

```bash
# Make the script executable
chmod +x health-check.sh

# Run health checks
./health-check.sh
```

### 2. Test Core Functionality

1. **User Registration/Login**
   - Register a new user account
   - Login with credentials
   - Verify JWT token generation

2. **Email System**
   - Go to Notifications settings
   - Click "Send Test Email"
   - Check email delivery

3. **SMS Processing**
   - Test SMS input via SMS Demo
   - Verify transaction creation
   - Check manual classification for failed SMS

4. **Budget Management**
   - Create budget limits
   - Add transactions
   - Verify budget alerts

### 3. Admin Features (Admin Users Only)

1. **Create Admin User**
   ```bash
   # Connect to your production database and create admin user
   python3 -c "
   import asyncio
   from motor.motor_asyncio import AsyncIOMotorClient
   from passlib.context import CryptContext
   from datetime import datetime
   
   async def create_admin():
       client = AsyncIOMotorClient('your-production-mongo-url')
       db = client.budget_planner
       
       pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
       admin_user = {
           'email': 'admin@yourdomain.com',
           'username': 'admin',
           'password_hash': pwd_context.hash('secure-admin-password'),
           'role': 'admin',
           'is_active': True,
           'created_at': datetime.utcnow(),
           'updated_at': datetime.utcnow()
       }
       
       await db.users.insert_one(admin_user)
       print('Admin user created')
   
   asyncio.run(create_admin())
   "
   ```

2. **Test Admin Features**
   - Login as admin user
   - Access "Production" tab
   - Test scheduler controls
   - Verify production status monitoring

## 🔒 Security Checklist

- [ ] JWT secret is secure and not exposed
- [ ] CORS origins are restricted to your domains
- [ ] Database access is properly secured
- [ ] SendGrid API key is kept secret
- [ ] HTTPS is enabled for all domains
- [ ] Environment variables are not committed to version control
- [ ] Admin accounts use strong passwords
- [ ] Database backups are configured

## 📊 Monitoring and Maintenance

### 1. Monitor Email System

- Check SendGrid dashboard for email statistics
- Monitor notification logs in application
- Set up alerts for failed email deliveries

### 2. Database Monitoring

- Monitor MongoDB Atlas metrics
- Set up alerts for high usage
- Regular backup verification

### 3. Application Monitoring

- Monitor server response times
- Check error logs regularly
- Monitor user registration and activity

### 4. Regular Updates

- Keep dependencies updated
- Monitor security advisories
- Regular backup testing

## 🆘 Troubleshooting

### Common Issues

1. **Email Not Sending**
   - Verify SendGrid API key
   - Check sender email verification
   - Review CORS settings

2. **Database Connection Issues**
   - Verify MongoDB connection string
   - Check IP whitelist settings
   - Confirm database user permissions

3. **Authentication Problems**
   - Verify JWT secret is set
   - Check token expiration settings
   - Confirm CORS configuration

4. **Frontend Not Loading**
   - Check backend URL in frontend environment
   - Verify build process completed
   - Check browser console for errors

### Support Resources

- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **SendGrid**: [docs.sendgrid.com](https://docs.sendgrid.com)
- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Render**: [render.com/docs](https://render.com/docs)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)

## 📈 Performance Optimization

### 1. Frontend Optimization

- Enable gzip compression
- Use CDN for static assets
- Implement code splitting
- Optimize images and assets

### 2. Backend Optimization

- Use connection pooling for database
- Implement caching where appropriate
- Monitor and optimize query performance
- Use production WSGI server

### 3. Database Optimization

- Create appropriate indexes
- Monitor slow queries
- Use connection pooling
- Regular maintenance tasks

## 🔄 Continuous Deployment

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Railway
      run: |
        npm install -g @railway/cli
        railway deploy --service backend
        railway deploy --service frontend
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 🎉 Congratulations!

Your Budget Planner application is now deployed to production with:

- ✅ Secure user authentication
- ✅ Automated email notifications  
- ✅ SMS transaction processing
- ✅ Real-time budget monitoring
- ✅ Admin production management
- ✅ Comprehensive monitoring

Your users can now enjoy a fully-featured financial management platform with automated insights and professional email communications!

For additional support or questions, refer to the troubleshooting section or check the monitoring dashboard for system health.