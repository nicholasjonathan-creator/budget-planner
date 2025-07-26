🔐 RAILWAY ENVIRONMENT VARIABLES SETUP
=====================================

## 🎯 BACKEND ENVIRONMENT VARIABLES

### Copy these into your Railway backend service:

#### Standard Configuration (Copy as-is):
```
ENVIRONMENT=production
LOG_LEVEL=INFO
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true
ACCESS_TOKEN_EXPIRE=1440
```

#### Variables You Need to Fill In:

**1. MongoDB Connection String:**
```
MONGO_URL=mongodb+srv://[YOUR_USERNAME]:[YOUR_PASSWORD]@[YOUR_CLUSTER].mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase
```

**2. JWT Secret (Generate a secure 32+ character string):**
```
JWT_SECRET=budget-planner-super-secure-jwt-secret-2025-railway-deployment
```

**3. SendGrid API Key:**
```
SENDGRID_API_KEY=SG.[YOUR_SENDGRID_API_KEY]
```

**4. Sender Email:**
```
SENDER_EMAIL=noreply@budgetplanner.app
```

**5. CORS Origins (Start with wildcard, update after frontend deploy):**
```
CORS_ORIGINS=["*"]
```

---

## 🌐 FRONTEND ENVIRONMENT VARIABLES

### Copy these into your Railway frontend service:

**1. Backend URL (Update after backend is deployed):**
```
REACT_APP_BACKEND_URL=https://[YOUR_BACKEND_SERVICE_NAME].railway.app
```

**2. Environment:**
```
REACT_APP_ENVIRONMENT=production
```

**3. Build Optimization:**
```
GENERATE_SOURCEMAP=false
```

---

## 📋 HOW TO ADD IN RAILWAY:

### For Backend Service:
1. Go to your Railway dashboard
2. Click on your backend service
3. Click "Variables" tab
4. Click "New Variable" for each one:
   - Key: `ENVIRONMENT`
   - Value: `production`
   - Click "Add"
5. Repeat for all variables

### For Frontend Service:
1. Click on your frontend service  
2. Click "Variables" tab
3. Add the frontend variables

---

## ✅ DEPLOYMENT SEQUENCE:

### Phase 1: Deploy Backend First
1. ✅ Add backend environment variables
2. ✅ Deploy backend service
3. ✅ Test: `https://[backend].railway.app/api/health`
4. ✅ Copy the backend URL

### Phase 2: Deploy Frontend
1. ✅ Add frontend environment variables
2. ✅ Update `REACT_APP_BACKEND_URL` with actual backend URL
3. ✅ Deploy frontend service
4. ✅ Copy the frontend URL

### Phase 3: Update CORS
1. ✅ Go back to backend variables
2. ✅ Update `CORS_ORIGINS` with actual frontend URL:
   ```
   CORS_ORIGINS=["https://[your-frontend].railway.app"]
   ```
3. ✅ Redeploy backend

---

## 🔍 VARIABLE CHECKLIST:

### Backend Variables (9 total):
- [ ] ENVIRONMENT=production
- [ ] LOG_LEVEL=INFO  
- [ ] SENDER_NAME=Budget Planner
- [ ] ENABLE_EMAIL_SENDING=true
- [ ] ACCESS_TOKEN_EXPIRE=1440
- [ ] MONGO_URL=[your-mongodb-connection]
- [ ] JWT_SECRET=[your-secure-secret]
- [ ] SENDGRID_API_KEY=[your-sendgrid-key]
- [ ] SENDER_EMAIL=[your-verified-email]
- [ ] CORS_ORIGINS=[frontend-url-after-deployment]

### Frontend Variables (3 total):
- [ ] REACT_APP_BACKEND_URL=[backend-url-after-deployment]
- [ ] REACT_APP_ENVIRONMENT=production
- [ ] GENERATE_SOURCEMAP=false

---

## 🚀 QUICK START:

**Ready to deploy? Here's the fastest path:**

1. **Sign up at Railway** ✅
2. **Deploy backend first** ✅
3. **I'll help you set these variables** ✅
4. **Deploy frontend** ✅
5. **Connect them together** ✅

**Total time: ~15 minutes vs hours of Render debugging!**

## 🆘 NEED HELP?

Tell me:
- Which step you're on
- Any error messages you see
- Your service URLs once deployed

**Railway is going to be SO much better than Render! Let's get started! 🚄**