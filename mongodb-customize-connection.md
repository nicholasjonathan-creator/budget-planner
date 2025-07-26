🔐 MONGODB CONNECTION STRING CUSTOMIZATION
==========================================

## ✅ GREAT! You got the connection string from Atlas:
```
mongodb+srv://<db_username>:<db_password>@buildadatabase.ahqwxzz.mongodb.net/?retryWrites=true&w=majority&appName=Buildadatabase
```

## 🔧 NOW WE NEED TO CUSTOMIZE IT:

### Step 1: Get Your Database Credentials

You need to replace `<db_username>` and `<db_password>` with your actual MongoDB Atlas credentials.

#### Where to find these:
1. **In MongoDB Atlas dashboard**
2. **Go to "Database Access"** (left sidebar)
3. **Look for your database user** - this shows your username
4. **If you forgot the password**, you can reset it

#### Common usernames might be:
- Your email address
- A username you created (like "admin", "dbuser", etc.)
- The name you used when setting up the cluster

### Step 2: Replace Placeholders

Take your connection string and replace:
- `<db_username>` → your actual MongoDB username
- `<db_password>` → your actual MongoDB password

### Step 3: Add Database Name

Add `/budget_planner` after the host and before the `?`:

**Original:**
```
mongodb+srv://username:password@buildadatabase.ahqwxzz.mongodb.net/?retryWrites=true&w=majority&appName=Buildadatabase
```

**With database name:**
```
mongodb+srv://username:password@buildadatabase.ahqwxzz.mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase
```

---

## 🎯 EXAMPLE OF FINAL CONNECTION STRING:

If your username was "john" and password was "mypassword123", your final string would be:
```
mongodb+srv://john:mypassword123@buildadatabase.ahqwxzz.mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase
```

---

## 🔍 HOW TO GET YOUR CREDENTIALS:

### Option A: Check Database Access
1. In MongoDB Atlas, click **"Database Access"** (left sidebar)
2. You'll see your database users listed
3. The username is shown there
4. If you need to reset password, click "Edit" → "Edit Password"

### Option B: Create New Database User (if needed)
1. In "Database Access", click **"Add New Database User"**
2. Choose **"Password"** authentication
3. Create username: `budgetplanner` (or any name you want)
4. Create password: `SecurePassword123!` (or generate one)
5. Set role: **"Atlas Admin"** or **"Read and write to any database"**
6. Click **"Add User"**

---

## 🚨 IMPORTANT SECURITY CHECK:

Make sure **Network Access** allows Railway:
1. Go to **"Network Access"** (left sidebar)
2. Should show **"0.0.0.0/0"** (allows access from anywhere)
3. If not, click **"Add IP Address"** → **"Allow access from anywhere"**

---

## 🤔 WHAT'S YOUR SITUATION?

**Tell me:**

**A)** **"I know my username and password"** - Great! Just replace the placeholders and add `/budget_planner`

**B)** **"I need to check Database Access"** - Go to Database Access tab in Atlas

**C)** **"I forgot my password"** - I'll help you reset it

**D)** **"I need to create a new database user"** - I'll guide you through it

**E)** **"I'm ready with the final connection string"** - Perfect! Let's add it to Railway

---

## 🎯 NEXT STEP:

Once you have your final connection string (with real username/password and `/budget_planner`), you'll add it to Railway as:

**Key:** `MONGO_URL`
**Value:** `mongodb+srv://[your-username]:[your-password]@buildadatabase.ahqwxzz.mongodb.net/budget_planner?retryWrites=true&w=majority&appName=Buildadatabase`

**Which option describes your situation? Let me know so I can help you get the final connection string! 🔐**