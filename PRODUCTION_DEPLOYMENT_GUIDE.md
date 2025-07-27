# Budget Planner - Production Deployment Guide

## 🚀 Simplified Production Deployment (No Email Dependencies)

This guide provides step-by-step instructions for deploying the Budget Planner application to production with a **dashboard-only approach** - no email configuration required!

## ✨ Key Features

- **📱 SMS Transaction Parsing** - Automatic processing of bank SMS messages
- **📊 Real-time Analytics Dashboard** - Financial health scores, spending patterns
- **💰 Budget Tracking** - Set limits, track progress, get dashboard alerts
- **🔄 WhatsApp Integration** - SMS forwarding for automated transaction capture
- **👥 Multi-user Support** - Secure user authentication and data isolation
- **🇮🇳 India-specific** - Supports all major Indian banks (HDFC, SBI, ICICI, Axis, etc.)

## 🏗️ Architecture Overview

- **Frontend**: React + Tailwind CSS (hosted on Vercel/Netlify)
- **Backend**: FastAPI + Python (hosted on Railway/Render)
- **Database**: MongoDB Atlas (cloud database)
- **Integration**: Twilio (WhatsApp SMS forwarding - optional)

## 📋 Prerequisites

1. **GitHub Account** - For code hosting
2. **MongoDB Atlas Account** - For database (free tier available)
3. **Railway/Render Account** - For backend hosting (free tier available)
4. **Vercel/Netlify Account** - For frontend hosting (free tier available)
5. **Twilio Account** - For WhatsApp integration (optional, has free tier)

## 🚀 Step-by-Step Deployment

### 1. Database Setup (MongoDB Atlas)

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for a free account

2. **Create a Cluster**
   - Choose "Free" tier (M0 Sandbox)
   - Select your preferred region (choose closest to your users)
   - Name your cluster (e.g., "budget-planner")

3. **Configure Database Access**
   - Go to "Database Access" in the sidebar
   - Click "Add New Database User"
   - Create username/password (save these securely)
   - Set permissions to "Read and write to any database"

4. **Configure Network Access**
   - Go to "Network Access" in the sidebar
   - Click "Add IP Address"
   - Choose "Allow access from anywhere" (0.0.0.0/0)
   - Or add specific deployment platform IPs if preferred

5. **Get Connection String**
   - Go to "Clusters" and click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<username>`, `<password>`, and `<dbname>` with your values
   - Example: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/budgetplanner?retryWrites=true&w=majority`

### 2. Backend Deployment (Railway)

1. **Prepare Repository**
   - Push your code to GitHub
   - Ensure `/app/backend/` contains all backend files

2. **Deploy to Railway**
   - Go to [Railway](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Choose the backend service

3. **Configure Environment Variables**
   Add these environment variables in Railway dashboard:
   ```
   MONGO_URL=your_mongodb_connection_string
   JWT_SECRET_KEY=your_super_secret_jwt_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid (optional)
   TWILIO_AUTH_TOKEN=your_twilio_token (optional)
   TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number (optional)
   ```

4. **Configure Build Settings**
   - Set root directory to `/backend`
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

5. **Deploy and Test**
   - Railway will automatically deploy
   - Note the generated URL (e.g., `https://your-app.railway.app`)

### 3. Frontend Deployment (Vercel)

1. **Deploy to Vercel**
   - Go to [Vercel](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Select your repository
   - Set root directory to `/frontend`

2. **Configure Environment Variables**
   Add this environment variable in Vercel dashboard:
   ```
   REACT_APP_BACKEND_URL=https://your-backend-url.railway.app/api
   ```

3. **Configure Build Settings**
   - Build Command: `yarn build`
   - Output Directory: `build`
   - Install Command: `yarn install`

4. **Deploy and Test**
   - Vercel will automatically deploy
   - Note the generated URL (e.g., `https://your-app.vercel.app`)

### 4. Optional: WhatsApp Integration Setup

If you want SMS forwarding via WhatsApp:

1. **Create Twilio Account**
   - Go to [Twilio](https://www.twilio.com)
   - Sign up for free account

2. **Set up WhatsApp Sandbox**
   - Go to Console → Messaging → Try it out → Send a WhatsApp message
   - Follow instructions to join sandbox
   - Get your WhatsApp number and credentials

3. **Configure Webhook**
   - Set webhook URL to: `https://your-backend.railway.app/api/whatsapp/webhook`
   - Configure for incoming messages

## 🧪 Testing Your Deployment

### 1. Basic Functionality Test
- [ ] Open frontend URL
- [ ] Register a new user account
- [ ] Login successfully
- [ ] Navigate through all tabs (Overview, Analytics, Transactions, etc.)

### 2. Core Features Test
- [ ] Add a manual transaction
- [ ] View transaction in the list
- [ ] Set a budget limit
- [ ] Check analytics dashboard
- [ ] Test SMS demo functionality

### 3. Database Test
- [ ] Verify transactions are saved
- [ ] Test user authentication
- [ ] Check data persistence across sessions

## 🎯 Production Optimization

### Performance
- Frontend is optimized with React build
- Backend uses gunicorn with multiple workers
- Database queries are optimized for MongoDB

### Security
- JWT token authentication
- User data isolation
- Environment variables for secrets
- CORS properly configured

### Monitoring
- Railway/Vercel provide built-in monitoring
- Check logs via platform dashboards
- Set up uptime monitoring if needed

## 🛠️ Maintenance

### Regular Tasks
- **Monthly**: Check database usage in MongoDB Atlas
- **Quarterly**: Review and update dependencies
- **As needed**: Monitor application logs for errors

### Scaling
- **Database**: MongoDB Atlas auto-scales
- **Backend**: Railway supports easy scaling
- **Frontend**: Vercel handles traffic automatically

## 🎉 Success!

Your Budget Planner is now live in production! Users can:

✅ **Track Income & Expenses** - Manual entry and SMS parsing  
✅ **Set Budget Limits** - Category-wise budget management  
✅ **View Analytics** - Financial health scores and spending insights  
✅ **Process SMS** - Automatic transaction capture from bank messages  
✅ **Multi-user Support** - Each user has isolated, secure data  

## 📞 Support

For technical issues:
1. Check application logs in Railway/Vercel dashboards
2. Review MongoDB Atlas connection status
3. Verify environment variables are set correctly
4. Test API endpoints directly if needed

---

**Deployment Simplified! No email configuration, no complex setup - just pure financial tracking power! 🚀**