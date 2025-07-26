# 🎨 Your Personal Render Deployment Guide

## 🔧 Your Unique Service Names:
- **Backend Service**: `budget-planner-be--20250726-1342`
- **Frontend Service**: `budget-planner-fe--20250726-1342`

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Repository Setup ✅
Your files are already configured with unique service names. Just commit and push:

```bash
git add .
git commit -m "Add Render deployment with unique service names"
git push origin main
```

### Step 2: Deploy Backend Service

1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your repository**
4. **Configure Backend Service:**

   **Service Settings:**
   - **Name**: `budget-planner-be--20250726-1342`
   - **Region**: `Oregon` (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start-render.sh`

   **Environment Variables:**
   Add these exact variables in Render dashboard:
   ```
   MONGO_URL = mongodb+srv://your-username:your-password@your-cluster.mongodb.net/budget_planner?retryWrites=true&w=majority&appName=YourAppName
   
   SENDGRID_API_KEY = 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
   
   JWT_SECRET = your-super-secret-jwt-key-for-production-nicholasjonathan-2025
   
   SENDER_EMAIL = noreply@budgetplanner.app
   
   ENVIRONMENT = production
   
   CORS_ORIGINS = ["https://budget-planner-fe--20250726-1342.onrender.com"]
   ```

5. **Click "Create Web Service"**
6. **Wait for backend to deploy** (usually 5-10 minutes)

### Step 3: Deploy Frontend Service

1. **Click "New +" → "Static Site"**
2. **Connect the same repository**
3. **Configure Frontend Service:**

   **Service Settings:**
   - **Name**: `budget-planner-fe--20250726-1342`
   - **Region**: `Oregon` (same as backend)
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn install && yarn build`
   - **Publish Directory**: `build`

   **Environment Variables:**
   ```
   REACT_APP_BACKEND_URL = https://budget-planner-be--20250726-1342.onrender.com
   
   REACT_APP_ENVIRONMENT = production
   
   GENERATE_SOURCEMAP = false
   ```

4. **Click "Create Static Site"**
5. **Wait for frontend to deploy** (usually 3-5 minutes)

### Step 4: Your Live URLs

After deployment, your app will be available at:

- **🌐 Frontend (Main App)**: `https://budget-planner-fe--20250726-1342.onrender.com`
- **🔧 Backend API**: `https://budget-planner-be--20250726-1342.onrender.com`

### Step 5: Verify Deployment

Test these endpoints:

1. **Backend Health Check**: 
   ```
   https://budget-planner-be--20250726-1342.onrender.com/api/health
   ```
   Should return: `{"status": "healthy", "timestamp": "..."}`

2. **Frontend App**: 
   ```
   https://budget-planner-fe--20250726-1342.onrender.com
   ```
   Should show the Budget Planner login page

3. **Test User Registration**:
   - Register a new account
   - Login successfully
   - Access the dashboard

4. **Test Email System**:
   - Go to "Notifications" tab
   - Click "Send Test Email"
   - Verify email functionality

## 🔍 Monitoring Your Deployment

### Service Status
Monitor your services in the Render dashboard:
- Check build logs if deployment fails
- Monitor service health and uptime
- View application logs for debugging

### Wake Up Sleeping Services (Free Tier)
Free tier services sleep after 15 minutes of inactivity. Use this script to wake them:

```bash
python scripts/monitor-render.py https://budget-planner-be--20250726-1342.onrender.com https://budget-planner-fe--20250726-1342.onrender.com
```

## 🆘 Troubleshooting

### Common Issues:

1. **Build Fails**: 
   - Check build logs in Render dashboard
   - Ensure all files are committed and pushed

2. **Backend Won't Start**:
   - Verify all environment variables are set correctly
   - Check that MongoDB Atlas allows connections from 0.0.0.0/0

3. **Frontend Can't Connect to Backend**:
   - Verify `REACT_APP_BACKEND_URL` matches your backend service URL
   - Check CORS_ORIGINS includes your frontend URL

4. **Email System Issues**:
   - Verify SendGrid API key is correct
   - Check sender email is verified in SendGrid

### Free Tier Limitations:
- ⏰ Services sleep after 15 minutes of inactivity
- 🕐 Cold start time: 30-60 seconds when waking up
- 📊 750 hours/month per service
- 🔄 Slower builds compared to paid plans

## 🎉 Success!

Once deployed, your Budget Planner will have:

- ✅ **User Authentication & Registration**
- ✅ **Automated Email Notifications** 
- ✅ **SMS Transaction Processing**
- ✅ **Real-time Budget Monitoring**
- ✅ **Production Admin Dashboard**
- ✅ **Multi-currency Support**
- ✅ **Professional Email Templates**

## 🔗 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Your Backend**: https://budget-planner-be--20250726-1342.onrender.com
- **Your Frontend**: https://budget-planner-fe--20250726-1342.onrender.com
- **MongoDB Atlas**: https://cloud.mongodb.com
- **SendGrid Dashboard**: https://app.sendgrid.com

---

**Ready to deploy!** Follow the steps above and your Budget Planner will be live on the internet! 🚀