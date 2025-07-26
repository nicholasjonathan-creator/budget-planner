# 🚀 Production Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Account**: To host your code
2. **MongoDB Atlas Account**: For database hosting
3. **Railway Account**: For backend hosting
4. **Vercel Account**: For frontend hosting
5. **Twilio Account**: For SMS integration (optional)

## Step 1: Setup MongoDB Atlas (5 minutes)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a free account
3. Create a new cluster:
   - Choose AWS (recommended)
   - Select "M0 Sandbox" (free tier)
   - Choose region closest to you
4. Create database user:
   - Database Access → Add New Database User
   - Username: `budgetuser`
   - Password: Generate secure password
   - Database User Privileges: Read and write to any database
5. Whitelist IP addresses:
   - Network Access → Add IP Address
   - Add `0.0.0.0/0` (allow from anywhere)
6. Get connection string:
   - Clusters → Connect → Connect your application
   - Copy the connection string
   - Replace `<password>` with your database password

## Step 2: Deploy Backend to Railway (10 minutes)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Deploy Backend**:
   ```bash
   cd backend
   railway init
   railway up
   ```

4. **Set Environment Variables**:
   ```bash
   railway variables set MONGO_URL="your-mongodb-connection-string"
   railway variables set JWT_SECRET="your-super-secret-jwt-key"
   railway variables set ENVIRONMENT="production"
   ```

5. **Get Backend URL**:
   - Go to Railway dashboard
   - Copy the deployed URL (e.g., `https://your-app.railway.app`)

## Step 3: Deploy Frontend to Vercel (5 minutes)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Update Frontend Environment**:
   ```bash
   cd frontend
   # Update .env.production with your backend URL
   echo "REACT_APP_BACKEND_URL=https://your-app.railway.app" > .env.production
   ```

3. **Deploy Frontend**:
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables in Vercel**:
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add: `REACT_APP_BACKEND_URL` = `https://your-app.railway.app`

## Step 4: Setup SMS Integration (Optional - 10 minutes)

1. **Create Twilio Account**:
   - Go to [Twilio](https://www.twilio.com/)
   - Create account and verify phone number
   - Get a Twilio phone number ($1/month)

2. **Configure Webhook**:
   - Twilio Console → Phone Numbers → Manage → Active Numbers
   - Click your number
   - Webhook URL: `https://your-backend.railway.app/api/webhooks/sms`
   - HTTP Method: POST

3. **Update Backend Environment**:
   ```bash
   railway variables set TWILIO_ACCOUNT_SID="your-account-sid"
   railway variables set TWILIO_AUTH_TOKEN="your-auth-token"
   railway variables set TWILIO_PHONE_NUMBER="your-twilio-number"
   ```

## Step 5: Test Your Deployment

1. **Test Backend**:
   ```bash
   curl https://your-backend.railway.app/api/health
   ```

2. **Test Frontend**:
   - Visit your Vercel URL
   - Test SMS demo functionality
   - Add manual transactions

3. **Test SMS Integration**:
   - Send SMS to your Twilio number
   - Check if transaction is created

## Step 6: Setup Custom Domain (Optional)

1. **Buy Domain** (e.g., GoDaddy, Namecheap)

2. **Configure Vercel Domain**:
   - Vercel Dashboard → Project → Settings → Domains
   - Add your domain
   - Update DNS records as instructed

3. **Update CORS Settings**:
   ```bash
   railway variables set CORS_ORIGINS='["https://yourdomain.com"]'
   ```

## Step 7: Monitoring & Maintenance

1. **Monitor Health**:
   - Backend: `https://your-backend.railway.app/api/health`
   - Metrics: `https://your-backend.railway.app/api/metrics`

2. **Setup Uptime Monitoring**:
   - Use services like UptimeRobot or Pingdom
   - Monitor both frontend and backend

3. **Regular Updates**:
   - Update dependencies regularly
   - Monitor logs for errors
   - Backup database periodically

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure CORS_ORIGINS includes your frontend URL
   - Check if URLs match exactly (http vs https)

2. **Database Connection Failed**:
   - Verify MongoDB Atlas connection string
   - Check IP whitelist settings
   - Ensure database user has correct permissions

3. **SMS Not Working**:
   - Verify Twilio webhook URL
   - Check Twilio credentials
   - Ensure webhook endpoint is accessible

4. **Frontend Build Errors**:
   - Check environment variables
   - Verify backend URL is correct
   - Review build logs in Vercel

### Getting Help

- **Backend Logs**: `railway logs`
- **Frontend Logs**: Check Vercel dashboard
- **Database Logs**: MongoDB Atlas monitoring
- **SMS Logs**: Twilio console

## Cost Breakdown

- **MongoDB Atlas**: Free (M0 tier)
- **Railway**: $5/month (hobby plan)
- **Vercel**: Free (hobby plan)
- **Twilio**: $1/month (phone number) + $0.0075/SMS
- **Domain**: $10-15/year (optional)

**Total**: ~$6/month for full production setup

## Next Steps

1. **Add Authentication**: Implement user registration/login
2. **Add Email Notifications**: Send budget alerts via email
3. **Mobile App**: Create React Native app
4. **Advanced Analytics**: Add more detailed insights
5. **API Keys**: Add API access for third-party integrations

## Security Checklist

- [ ] JWT secret is secure and not in code
- [ ] Database credentials are secure
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Input validation is implemented
- [ ] HTTPS is enforced
- [ ] Environment variables are set correctly

## Success! 🎉

Your Budget Planner is now live and ready for users!

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app
- **Health Check**: https://your-app.railway.app/api/health
- **API Docs**: https://your-app.railway.app/docs

Share it with friends and start tracking your expenses automatically! 📱💰