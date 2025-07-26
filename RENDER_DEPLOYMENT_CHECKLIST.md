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
