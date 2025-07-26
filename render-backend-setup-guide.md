🔧 RENDER BACKEND SERVICE RECONFIGURATION GUIDE
================================================

## Step 1: Access Your Render Dashboard

1. Go to https://render.com
2. Sign in to your account
3. Navigate to your dashboard

## Step 2: Locate/Create Backend Service

### Option A: If Service Exists (Reconfigure)
1. Find your backend service (look for names like "budget-planner-be-*" or similar)
2. Click on the service name
3. Go to "Settings" tab

### Option B: If Service Doesn't Exist (Create New)
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository
4. Choose your budget planner repository

## Step 3: Basic Service Configuration

### Service Settings:
```
Name: budget-planner-backend-[your-unique-id]
Branch: main (or your default branch)
Root Directory: backend
Runtime: Python 3
```

### Build & Deploy Settings:
```
Build Command: pip install -r requirements.txt
Start Command: ./start-render.sh
```

## Step 4: Environment Variables (CRITICAL)

Add these environment variables in the "Environment" section:

### Required Variables:
```
ENVIRONMENT=production
LOG_LEVEL=INFO
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true
ACCESS_TOKEN_EXPIRE=1440
```

### Variables You Need to Provide:
```
MONGO_URL=mongodb+srv://[username]:[password]@[cluster].mongodb.net/budget_planner?retryWrites=true&w=majority&appName=[appname]

JWT_SECRET=[generate-a-secure-random-string-at-least-32-characters]

SENDGRID_API_KEY=SG.[your-sendgrid-api-key]

SENDER_EMAIL=[your-verified-sender-email]@[your-domain]
```

### CORS Configuration:
```
CORS_ORIGINS=["https://budget-planner-fe-[your-frontend-id].onrender.com"]
```

## Step 5: Advanced Settings

### Health Check:
```
Health Check Path: /api/health
```

### Auto-Deploy:
```
✅ Enable "Auto-Deploy" from main branch
```

### Service Plan:
```
Plan: Free (or upgrade if needed)
Region: Oregon (or your preferred region)
```

## Step 6: Verify Start Script

Make sure your `/backend/start-render.sh` exists and is executable:

```bash
#!/bin/bash
echo "🚀 Starting Budget Planner Backend for Render"
echo "Environment: $ENVIRONMENT"
echo "Log Level: $LOG_LEVEL"

# Start the application
exec gunicorn server:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile - \
    --error-logfile -
```

## Step 7: Deploy Process

1. Click "Create Web Service" (for new) or "Save Changes" (for existing)
2. Watch the build logs for any errors
3. Wait for deployment to complete (5-15 minutes)
4. Check the service URL works: `https://[your-service-name].onrender.com/api/health`

## Step 8: Common Issues & Solutions

### Issue 1: Build Fails
**Solution**: Check that `requirements.txt` includes all dependencies:
```
fastapi==0.104.1
uvicorn==0.24.0
gunicorn==21.2.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pymongo==4.6.0
motor==3.3.2
sendgrid==6.11.0
python-dotenv==1.0.0
apscheduler==3.10.4
pydantic==2.5.0
email-validator==2.1.0
```

### Issue 2: Service Won't Start
**Causes**:
- Missing environment variables
- Invalid MongoDB connection string
- Port binding issues

**Solution**: Check logs and ensure all environment variables are set

### Issue 3: Database Connection Fails
**Solution**: Verify MONGO_URL format:
```
mongodb+srv://username:password@cluster.mongodb.net/budget_planner?retryWrites=true&w=majority
```

## Step 9: Get Your Service URL

Once deployed successfully, your backend URL will be:
```
https://[your-service-name].onrender.com
```

Copy this URL - you'll need it for frontend configuration.

## Step 10: Test Your Backend

Test these endpoints:
```
GET https://[your-service-name].onrender.com/api/health
GET https://[your-service-name].onrender.com/api/categories
```

## 🚨 IMPORTANT NOTES:

1. **Environment Variables**: Double-check all environment variables are set correctly
2. **MongoDB**: Ensure your MongoDB Atlas cluster allows connections from anywhere (0.0.0.0/0)
3. **SendGrid**: Make sure your SendGrid account is active and sender email is verified
4. **Build Logs**: Always check build logs for errors
5. **Service Name**: Note down the exact service name for frontend configuration

## 🆘 If You Need Help:

Share with me:
1. The exact error messages from build/deploy logs
2. Your service name once created
3. Any specific issues you encounter

I'll help you troubleshoot and get the backend running!