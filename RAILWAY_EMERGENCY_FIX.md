# 🚨 RAILWAY EMERGENCY FIX - Healthcheck Failure

## Current Status
❌ **Healthcheck failing after 4m 51s**  
❌ **App crashes on startup**  
❌ **Error:** `Could not parse SQLAlchemy URL from string ''`

---

## 🎯 ROOT CAUSE

Your `DATABASE_URL` variable is set to `${{Postgres.DATABASE_URL}}` but:
- No service named "Postgres" exists in your Railway project
- Railway can't find it → resolves to empty string `""`
- Empty string overrides the SQLite fallback
- SQLAlchemy crashes before app starts
- Healthcheck never succeeds → deployment fails

---

## ✅ SOLUTION (3 Options - Choose Fastest)

### **Option 1: Fix Database Reference (RECOMMENDED - 2 minutes)**

**Step 1:** Open Railway Dashboard
- Go to: https://railway.app/dashboard
- Find your project: `smit-hackathon` or `clinical-ai-copilot`

**Step 2:** Check Your Database Service Name
1. Look at your services list in the project
2. Find the PostgreSQL database service
3. Click on it
4. Note the **exact name** at the top (e.g., `copilot-db`, `postgres`, etc.)

**Step 3:** Update DATABASE_URL in App Service
1. Go back to project view
2. Click on your **APP service** (the one that's failing - NOT database)
3. Click **"Variables"** tab
4. Find `DATABASE_URL` variable
5. Click to edit it
6. Update to: `${{YOUR-DB-NAME.DATABASE_URL}}`

**Example if database is named `copilot-db`:**
```bash
DATABASE_URL=${{copilot-db.DATABASE_URL}}
```

**Example if database is named `postgres`:**
```bash
DATABASE_URL=${{postgres.DATABASE_URL}}
```

7. Save (Railway auto-saves)
8. Wait for automatic redeploy (~5 minutes)

---

### **Option 2: Use Raw Connection String (FASTEST - 1 minute)**

If you need it working RIGHT NOW for your presentation:

**Step 1:** Get Database Connection String
1. Click on your **PostgreSQL database service**
2. Go to **"Variables"** tab
3. Find `DATABASE_URL` variable
4. Click "Show" to reveal value
5. Copy the entire string (looks like):
   ```
   postgresql://postgres:AbC123XyZ@postgres.railway.internal:5432/railway
   ```

**Step 2:** Paste into App Variables
1. Go to your **APP service**
2. Click **"Variables"** tab
3. Find `DATABASE_URL`
4. Paste the raw connection string directly (no `${{...}}`)
5. Save

⚠️ **Downside:** Not dynamic - if database restarts with new credentials, you must update manually.

---

### **Option 3: Remove DATABASE_URL (Use SQLite Fallback - 30 seconds)**

For demo purposes only - data won't persist across restarts:

**Step 1:** Remove DATABASE_URL Variable
1. Go to your APP service
2. Click **"Variables"** tab
3. Find `DATABASE_URL`
4. Click the **trash icon** to delete it entirely
5. Save

**Step 2:** Wait for Redeploy
- App will use SQLite fallback: `sqlite:///./clinical_copilot.db`
- Works for demo but data is lost on restart
- Good enough for hackathon presentation!

---

## 🧪 VERIFICATION STEPS

After applying any fix, wait for redeploy and check:

### 1. Railway Logs (Real-Time)
Go to: Your APP service → Logs tab

**Look for these SUCCESS indicators:**
```
✅ INFO:     Initialising database tables...
✅ INFO:     Loading ML models into memory...
✅ INFO:     CNN model loaded from ml/registry/cnn_pneumonia.h5
✅ INFO:     ANN model loaded from ml/registry/ann_heart_risk.h5
✅ INFO:     Text model loaded from ml/registry/text_triage.h5
✅ INFO:     All available models loaded successfully
✅ INFO:     Clinical AI Co-Pilot API is ready
✅ INFO:     Application startup complete.
✅ INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

**If you see these ERROR indicators:**
```
❌ sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
❌ Error: Model not loaded
❌ ModuleNotFoundError
❌ ConnectionRefusedError
```
→ Still broken, try next option

---

### 2. Healthcheck Status
Go to: Your APP service → Deployments tab

**Should show:**
- ✅ **Status:** Active (green)
- ✅ **Health:** Passing
- ✅ **Healthcheck endpoint:** `/health` responding

---

### 3. Test Endpoints

**Get your deployment URL:**
Railway dashboard → Your APP service → Settings → Domains → Copy URL

**Test health endpoint:**
```bash
curl https://your-app.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

**If you get:**
```
Connection refused
502 Bad Gateway
504 Gateway Timeout
```
→ App is still crashing, check logs

---

### 4. Test a Real Prediction

**Tabular prediction (easiest to test):**
```bash
curl -X POST https://your-app.up.railway.app/api/v1/predict/tabular \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "sex": 1,
    "cp": 2,
    "trestbps": 130,
    "chol": 250,
    "fbs": 0,
    "restecg": 1,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 1.5,
    "slope": 1,
    "ca": 0,
    "thal": 2
  }'
```

**Expected Response:**
```json
{
  "case_id": 1,
  "prediction": "HIGH_RISK",
  "confidence": 0.8234,
  "shap_values": {...},
  "shap_chart_url": "/static/uploads/shap_xxx.png"
}
```

---

## 🔍 DEBUGGING GUIDE

### Issue: Can't Find Database Service Name

**Solution:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link to project
railway login
railway link

# List all services
railway status
```

Output will show all services with their names.

---

### Issue: Variable Not Saving

**Symptoms:** You update DATABASE_URL but it doesn't change

**Solution:**
1. Hard refresh browser (Ctrl+Shift+R)
2. Try in incognito/private window
3. Use Railway CLI:
   ```bash
   railway variables set DATABASE_URL='${{copilot-db.DATABASE_URL}}'
   ```

---

### Issue: Database Service Doesn't Exist

**Symptoms:** You don't have a PostgreSQL service at all

**Solution - Add PostgreSQL:**
1. In Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait for provisioning (1-2 minutes)
5. Note the service name (likely `postgres`)
6. Update app's DATABASE_URL to `${{postgres.DATABASE_URL}}`

---

### Issue: Models Not Loading

**Symptoms:** Logs show "Model not loaded" or "FileNotFoundError"

**Possible Causes:**
1. Models not in git repository
2. Wrong model paths in environment variables
3. Build context excludes `ml/registry/`

**Solution:**
```bash
# Check models are in git
git ls-tree -r HEAD ml/registry/

# Should show 8 files:
# .gitkeep
# cnn_pneumonia.h5 (~26MB)
# ann_heart_risk.h5 (~76KB)
# text_triage.h5 (~4MB)
# + 4 .pkl files
```

If missing, see `DEPLOYMENT_FIX.md` to add them.

---

### Issue: App Starts but Healthcheck Still Fails

**Symptoms:** Logs show "Application startup complete" but health endpoint times out

**Solution 1:** Check healthcheck path
1. Railway dashboard → APP service → Settings
2. **Healthcheck Path:** should be `/health` (not `/health/` or `/healthz`)
3. **Healthcheck Timeout:** increase to 300 seconds

**Solution 2:** Check PORT binding
Your Dockerfile uses: `CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}`

Railway sets `$PORT` automatically - no action needed unless you override it.

---

## ⏱️ EXPECTED TIMELINES

**Option 1 (Fix DB reference):**
- Find database name: 1 min
- Update variable: 30 sec
- Redeploy: 5-8 min
- Test: 1 min
- **Total: ~10 min**

**Option 2 (Raw connection string):**
- Copy DB URL: 30 sec
- Paste in app: 30 sec
- Redeploy: 5-8 min
- Test: 1 min
- **Total: ~8 min**

**Option 3 (SQLite fallback):**
- Delete DATABASE_URL: 30 sec
- Redeploy: 5-8 min
- Test: 1 min
- **Total: ~7 min**

---

## 🎯 WHICH OPTION TO CHOOSE?

### Choose Option 1 if:
✅ You have 10+ minutes before presentation  
✅ You want proper production setup  
✅ You need persistent database  

### Choose Option 2 if:
✅ You need it working in 8 minutes  
✅ Database credentials won't change  
✅ You're okay with manual updates  

### Choose Option 3 if:
✅ You need it working in 7 minutes (FASTEST)  
✅ Demo only - don't care about data persistence  
✅ Nuclear option for emergency  

---

## 📸 VISUAL GUIDE (Screenshots)

### Finding Database Service Name:
```
Railway Dashboard
├── Your Project
│   ├── [APP] clinical-ai-copilot ← Your app (failing)
│   └── [DATABASE] copilot-db ← This is the name you need!
```

### Updating DATABASE_URL:
```
APP Service → Variables
┌─────────────────────────────────────────┐
│ DATABASE_URL                            │
│                                         │
│ ❌ OLD: ${{Postgres.DATABASE_URL}}      │
│ ✅ NEW: ${{copilot-db.DATABASE_URL}}    │
└─────────────────────────────────────────┘
```

---

## 🚀 QUICK CHECKLIST

Before presenting:

- [ ] DATABASE_URL variable is correct
- [ ] App logs show "Clinical AI Co-Pilot API is ready"
- [ ] `/health` returns `{"status":"ok","models_loaded":true}`
- [ ] Can POST to `/api/v1/predict/tabular` successfully
- [ ] Frontend loads at root URL
- [ ] Have screenshots as backup if live demo fails

---

## 💡 PRO TIP

If you're presenting in <10 minutes:

1. **Use Option 3 (SQLite)** - fastest to fix
2. **Take screenshots NOW** of working local version
3. **Have video backup** of full workflow
4. **Explain** "deployed version uses in-memory DB for demo speed"
5. **Show GitHub repo** with proper PostgreSQL setup

Judges care more about the **concept and implementation** than whether it's live on Railway vs running locally!

---

## 📞 STILL STUCK?

**Share these in order:**
1. Railway logs (last 50 lines from APP service)
2. List of services in your Railway project (names)
3. Your DATABASE_URL variable value (in APP service Variables tab)
4. Screenshot of any error messages

---

**Remember:** Railway assigns random service names. `copilot-db` is just an example - yours might be different!

Good luck! 🚀
