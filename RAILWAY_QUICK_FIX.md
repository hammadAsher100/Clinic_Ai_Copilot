# 🚨 RAILWAY DATABASE CONNECTION FIX

## Problem
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```

Your app crashes on startup because `DATABASE_URL` is empty.

---

## Root Cause

The `DATABASE_URL` variable is referencing a **non-existent database service name**.

**What's happening:**
- You set: `DATABASE_URL=${{Postgres.DATABASE_URL}}`
- Railway service is actually named: `copilot-db`
- When Railway can't find `Postgres` service, it resolves to empty string `""`
- SQLAlchemy fails because it can't parse an empty connection string

---

## ✅ SOLUTION (2 minutes)

### Step 1: Find Your Database Service Name

1. Go to your Railway project dashboard
2. Look at your services list
3. Find your PostgreSQL database service
4. Note the **exact service name** (shown at top of service page)

**Common names:**
- `copilot-db`
- `Postgres`
- `postgres`
- `postgresql`
- Or whatever you named it

---

### Step 2: Update DATABASE_URL Variable

1. In Railway dashboard, go to your **app service** (not database)
2. Click **"Variables"** tab
3. Find `DATABASE_URL` variable
4. Update it to match your actual database service name:

**If your database service is named `copilot-db`:**
```bash
DATABASE_URL=${{copilot-db.DATABASE_URL}}
```

**If your database service is named `Postgres`:**
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**If your database service is named `postgres`:**
```bash
DATABASE_URL=${{postgres.DATABASE_URL}}
```

**Format:** `${{YOUR-EXACT-DB-SERVICE-NAME.DATABASE_URL}}`

---

### Step 3: Verify and Redeploy

1. Click **"Save"** or wait for auto-save
2. Railway will automatically redeploy
3. Watch the logs

**Expected log output:**
```
INFO:     Initialising database tables...
INFO:     Loading ML models into memory...
INFO:     Clinical AI Co-Pilot API is ready
INFO:     Application startup complete.
```

---

## 🧪 Test After Fix

### 1. Check Health Endpoint
```bash
curl https://your-app.up.railway.app/health
```

**Should return:**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

### 2. Check Logs
In Railway dashboard → Logs tab, you should see:
```
✅ Database connected successfully
✅ Models loaded: CNN, ANN, BiLSTM
✅ FastAPI server listening on 0.0.0.0:8000
```

---

## 🔍 Alternative: Find Database URL Manually

If you can't figure out the service name:

### Option A: Use Raw Connection String

1. Click on your **PostgreSQL service**
2. Go to **"Variables"** tab
3. Copy the value of `DATABASE_URL`
4. Go back to your **app service**
5. Paste the raw URL directly:

```bash
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
```

**Pros:** Works immediately  
**Cons:** Not dynamic (if database changes, you must update manually)

---

### Option B: Use Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# List all services
railway status

# Get database connection string
railway variables
```

---

## 📋 Complete Variable Set (Copy-Paste Ready)

Once you know your database service name, use this complete set:

```bash
# Database - UPDATE SERVICE NAME!
DATABASE_URL=${{copilot-db.DATABASE_URL}}

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Model Paths
MODEL_REGISTRY_PATH=ml/registry
CNN_MODEL_PATH=ml/registry/cnn_pneumonia.h5
ANN_MODEL_PATH=ml/registry/ann_heart_risk.h5
TEXT_MODEL_PATH=ml/registry/text_triage.h5
TEXT_TOKENIZER_PATH=ml/registry/tokenizer.pkl

# Storage
UPLOAD_DIR=data/uploads
REPORTS_DIR=data/reports

# LLM (Optional)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-70b-versatile
```

---

## 🚨 Common Mistakes

### ❌ Wrong: Using generic name
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```
**Error:** Service not found (unless you actually named it "Postgres")

### ❌ Wrong: Missing braces
```bash
DATABASE_URL=copilot-db.DATABASE_URL
```
**Error:** Treated as literal string, not variable reference

### ❌ Wrong: Case sensitivity
```bash
DATABASE_URL=${{Copilot-DB.DATABASE_URL}}
```
**Error:** Railway service names are case-sensitive

### ✅ Correct: Match exact service name
```bash
DATABASE_URL=${{copilot-db.DATABASE_URL}}
```

---

## 🔧 Debugging Tips

### Check if DATABASE_URL is set correctly:

1. In Railway app service → Variables
2. Look for `DATABASE_URL`
3. Click "Show" to reveal value
4. Should see something like:
   ```
   postgresql://postgres:xxxx@postgres.railway.internal:5432/railway
   ```
5. If you see empty string `""` or the literal `${{Postgres.DATABASE_URL}}`, it's wrong

---

### Check Database Service is Running:

1. Go to Railway project
2. Find PostgreSQL service
3. Check status indicator (green = running)
4. Click service → "Metrics" tab
5. Should see active connections

---

### Check Logs for Specific Errors:

**If you see:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) 
could not translate host name "postgres.railway.internal" to address
```
**Solution:** Database service isn't running or wrong name

**If you see:**
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```
**Solution:** DATABASE_URL variable is empty (this is your current issue)

**If you see:**
```
psycopg2.OperationalError: FATAL: password authentication failed
```
**Solution:** Wrong credentials (shouldn't happen with Railway variables)

---

## ⚡ Quick Recovery Steps

**If you're presenting in 10 minutes:**

1. **Quick Fix:** Use raw connection string
   ```bash
   # In PostgreSQL service, copy DATABASE_URL value
   # In app service, paste directly (don't use ${{...}} syntax)
   DATABASE_URL=postgresql://postgres:abc123@postgres.railway.internal:5432/railway
   ```

2. **Alternative:** Use SQLite fallback
   ```bash
   # In app service variables, temporarily remove DATABASE_URL
   # App will fall back to SQLite (in-memory)
   # Not production-ready but works for demo
   ```

3. **Nuclear Option:** Redeploy with SQLite only
   - Comment out PostgreSQL in docker-compose.yml
   - Push to GitHub
   - Railway rebuilds with SQLite
   - Data won't persist but predictions work

---

## 📊 Success Checklist

After fixing, verify:

- [ ] DATABASE_URL shows actual connection string (not empty)
- [ ] App logs show "Database connected successfully"
- [ ] Health endpoint returns 200 OK
- [ ] Can create a new case via API
- [ ] HITL decisions persist in database
- [ ] Reports generate and download

---

## 🎯 Expected Timeline

- Find database service name: **1 minute**
- Update DATABASE_URL variable: **30 seconds**
- Railway redeploys: **3-5 minutes**
- Test and verify: **2 minutes**
- **Total: ~8 minutes**

---

## 📞 Still Stuck?

1. **Share your Railway logs** (last 100 lines)
2. **Check Railway Variables** screenshot
3. **List your services** in the project
4. **Database service name** exactly as shown

---

**Remember:** The key is matching the **exact service name** in your Railway project!

Good luck! 🚀
