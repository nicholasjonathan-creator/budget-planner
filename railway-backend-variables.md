🔐 RAILWAY BACKEND ENVIRONMENT VARIABLES
=====================================

## 📋 HOW TO ADD THESE IN RAILWAY:

1. In Railway dashboard, click on your backend service
2. Click "Variables" tab on the left
3. Click "New Variable" button
4. Add each variable below (Key = Value)

---

## ✅ COPY-PASTE READY VARIABLES:

Add these exactly as shown:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true
ACCESS_TOKEN_EXPIRE=1440
CORS_ORIGINS=["*"]
```

---

## 🔑 VARIABLES YOU NEED TO CUSTOMIZE:

### 1. MongoDB Connection String
**Key:** `MONGO_URL`
**Value:** `mongodb+srv://[YOUR_USERNAME]:[YOUR_PASSWORD]@[YOUR_CLUSTER].mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase`

**Where to get this:**
- Go to MongoDB Atlas dashboard
- Click "Connect" on your cluster
- Choose "Connect your application"
- Copy the connection string and replace username/password

### 2. JWT Secret Key
**Key:** `JWT_SECRET`
**Value:** `budget-planner-super-secure-jwt-secret-2025-railway-deployment-[YOUR_NAME]`

**Make it unique:** Add your name or random characters to make it secure

### 3. SendGrid API Key
**Key:** `SENDGRID_API_KEY`
**Value:** `SG.[YOUR_SENDGRID_API_KEY]`

**Where to get this:**
- Go to SendGrid dashboard
- Settings > API Keys
- Create new API key with Full Access
- Copy the key (starts with "SG.")

### 4. Sender Email
**Key:** `SENDER_EMAIL`
**Value:** `noreply@budgetplanner.app`

**Or use your own verified domain:**
- `notifications@yourdomain.com`
- Must be verified in SendGrid

---

## 📊 COMPLETE VARIABLE LIST:

Here's what you should have (10 variables total):

```
1. ENVIRONMENT=production
2. LOG_LEVEL=INFO
3. SENDER_NAME=Budget Planner
4. ENABLE_EMAIL_SENDING=true
5. ACCESS_TOKEN_EXPIRE=1440
6. CORS_ORIGINS=["*"]
7. MONGO_URL=[your-mongodb-connection-string]
8. JWT_SECRET=[your-secure-jwt-secret]
9. SENDGRID_API_KEY=[your-sendgrid-api-key]
10. SENDER_EMAIL=[your-verified-sender-email]
```

---

## 🚀 QUICK SETUP PROCESS:

### Step 2a: Add Standard Variables (2 minutes)
Copy-paste these 6 variables exactly:
- ENVIRONMENT=production
- LOG_LEVEL=INFO  
- SENDER_NAME=Budget Planner
- ENABLE_EMAIL_SENDING=true
- ACCESS_TOKEN_EXPIRE=1440
- CORS_ORIGINS=["*"]

### Step 2b: Add Custom Variables (3 minutes)
Add these 4 with your own values:
- MONGO_URL=[your-mongodb-string]
- JWT_SECRET=[your-secure-secret]
- SENDGRID_API_KEY=[your-sendgrid-key]
- SENDER_EMAIL=[your-verified-email]

### Step 2c: Deploy Backend
1. Once all 10 variables are added, Railway will auto-deploy
2. Wait 2-3 minutes for build to complete
3. Your backend URL will be: `https://[service-name].railway.app`

---

## 🔍 VERIFICATION:

Once deployed, test your backend:
```
https://[your-backend-service].railway.app/api/health
```

Should return:
```json
{"status": "healthy", "timestamp": "2025-07-26T..."}
```

---

## 🆘 NEED HELP WITH ANY SPECIFIC VARIABLE?

**MongoDB URL**: I can help you get this from MongoDB Atlas
**SendGrid API Key**: I can guide you through SendGrid setup  
**JWT Secret**: I can generate a secure one for you
**Any issues**: Just let me know what error you see!

## 🎯 NEXT STEP:
Once backend is deployed and working, I'll give you the frontend variables to complete the setup!

**Ready to add these variables? Let me know if you need help with any of the custom ones!**