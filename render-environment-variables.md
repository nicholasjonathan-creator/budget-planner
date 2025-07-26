🔐 RENDER BACKEND ENVIRONMENT VARIABLES TEMPLATE
===============================================

Copy and paste these into your Render backend service environment variables section:

## Standard Configuration Variables:
```
ENVIRONMENT=production
LOG_LEVEL=INFO
SENDER_NAME=Budget Planner
ENABLE_EMAIL_SENDING=true
ACCESS_TOKEN_EXPIRE=1440
```

## Variables You Need to Fill In:

### 1. MongoDB Connection (Required)
```
MONGO_URL=mongodb+srv://[YOUR_USERNAME]:[YOUR_PASSWORD]@[YOUR_CLUSTER].mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase
```
**Where to get this:**
- Go to MongoDB Atlas dashboard
- Click "Connect" on your cluster
- Choose "Connect your application"
- Copy the connection string
- Replace <username> and <password> with your actual credentials

### 2. JWT Secret (Required)
```
JWT_SECRET=[GENERATE_A_SECURE_RANDOM_STRING_32_CHARS_OR_MORE]
```
**Example:** `JWT_SECRET=your-super-secure-jwt-secret-key-for-production-2025-budget-planner`

### 3. SendGrid API Key (Required for email features)
```
SENDGRID_API_KEY=SG.[YOUR_SENDGRID_API_KEY]
```
**Where to get this:**
- Go to SendGrid dashboard
- Navigate to Settings > API Keys
- Create a new API key with Full Access
- Copy the key (starts with "SG.")

### 4. Sender Email (Required for email features)
```
SENDER_EMAIL=[YOUR_VERIFIED_EMAIL]@[YOUR_DOMAIN]
```
**Examples:** 
- `SENDER_EMAIL=noreply@budgetplanner.app`
- `SENDER_EMAIL=notifications@yourdomain.com`

**Note:** This email must be verified in SendGrid

### 5. CORS Origins (Update with your frontend URL)
```
CORS_ORIGINS=["https://budget-planner-fe-[YOUR_FRONTEND_ID].onrender.com"]
```
**Update after frontend is deployed**

## ⚠️ IMPORTANT REMINDERS:

1. **No Spaces**: Don't add spaces around the = sign
2. **No Quotes**: Don't wrap values in quotes in Render (it adds them automatically)
3. **Case Sensitive**: Variable names are case-sensitive
4. **Secure Values**: Never share these values publicly

## 🔍 How to Add in Render:

1. In your Render backend service dashboard
2. Go to "Environment" tab
3. Click "Add Environment Variable"
4. Add each variable one by one:
   - Key: ENVIRONMENT
   - Value: production
   - Click "Save Changes"

## ✅ Verification Checklist:

- [ ] MONGO_URL contains your actual MongoDB credentials
- [ ] JWT_SECRET is at least 32 characters long
- [ ] SENDGRID_API_KEY starts with "SG."
- [ ] SENDER_EMAIL is verified in SendGrid
- [ ] CORS_ORIGINS will be updated with frontend URL
- [ ] All 9 environment variables are set
- [ ] No typos in variable names

## 🚀 After Setting Variables:

1. Click "Manual Deploy" to redeploy with new variables
2. Watch the deploy logs for any errors
3. Test the health endpoint: https://[your-service].onrender.com/api/health
4. Update the frontend configuration with your backend URL