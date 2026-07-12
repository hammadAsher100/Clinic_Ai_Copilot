# 🚂 Railway Deployment Guide - Clinical AI Co-Pilot

**Quick deployment for your hackathon demo in under 10 minutes!**

---

## ✅ Prerequisites Checklist

Before starting, ensure:
- [x] Your Dockerfile has `libgl1` (not `libgl1-mesa-glx`) - ✅ **FIXED**
- [x] Models are committed to git (in `ml/registry/`) - ✅ **DONE**
- [x] GitHub repository is up to date
- [ ] You have a Railway account (free tier works!)
- [ ] You have a Groq API key (optional but recommended)

---

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up for Railway (2 minutes)

1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Sign in with GitHub (easiest option)
4. Authorize Railway to access your repositories

---

### Step 2: Create New Project (1 minute)

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `hammadAsher100/smit-hackathon`
4. Railway will auto-detect your `Dockerfile`

**Important:** Railway automatically detects:
- ✅ `Dockerfile` (uses Docker build)
- ✅ `railway.json` (build configuration)
- ✅ Port from Dockerfile `EXPOSE` or environment variable

---

### Step 3: Configure Environment Variables (3 minutes)

In the Railway dashboard, go to **Variables** tab and add:

#### Required Variables:

```bash
# Database (Railway provides PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Model Paths (default values)
MODEL_REGISTRY_PATH=ml/registry
CNN_MODEL_PATH=ml/registry/cnn_pneumonia.h5
ANN_MODEL_PATH=ml/registry/ann_heart_risk.h5
TEXT_MODEL_PATH=ml/registry/text_triage.h5
TEXT_TOKENIZER_PATH=ml/registry/tokenizer.pkl

# File Storage
UPLOAD_DIR=data/uploads
REPORTS_DIR=data/reports
```

#### Optional (Recommended for LLM):

```bash
# Groq API for LLM Narrative Generation
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-70b-versatile
```

**How to get Groq API Key:**
1. Go to: https://console.groq.com
2. Sign up (free tier available)
3. Go to API Keys section
4. Create new key
5. Copy and paste into Railway

---

### Step 4: Add PostgreSQL Database (2 minutes)

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will automatically:
   - Provision a PostgreSQL database
   - Create `DATABASE_URL` variable
   - Link it to your service

5. Update your app's `DATABASE_URL` variable:
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

---

### Step 5: Deploy! (5-8 minutes)

1. Click **"Deploy"** or push to GitHub (auto-deploys)
2. Watch the build logs in real-time
3. Railway will:
   - Clone your repository
   - Build Docker image
   - Install system dependencies (`libgl1`, `libglib2.0-0`, etc.)
   - Install Python packages (TensorFlow, FastAPI, etc.)
   - Load your trained models from `ml/registry/`
   - Start the FastAPI server

**Expected Build Time:** 5-8 minutes (first build), 2-3 minutes (subsequent)

---

### Step 6: Get Your Deployment URL (instant)

1. Once deployed, Railway provides a URL like:
   ```
   https://your-app-name.up.railway.app
   ```

2. Click **"Settings"** → **"Domains"**
3. Copy the generated domain
4. OR add a custom domain (optional)

---

## 🧪 Test Your Deployment

### Test 1: Health Check
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

### Test 2: Image Prediction (from your local machine)
```bash
curl -X POST https://your-app.up.railway.app/api/v1/predict/image \
  -F "file=@data/raw/xray/test/NORMAL/synth_normal_0000.jpg" \
  -F "patient_name=Test Patient"
```

### Test 3: Tabular Prediction
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

### Test 4: Text Prediction
```bash
curl -X POST https://your-app.up.railway.app/api/v1/predict/text \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "fever, cough, fatigue, difficulty breathing"
  }'
```

### Test 5: Frontend
Open in browser:
```
https://your-app.up.railway.app/
```

Should redirect to dashboard.

---

## 📊 Monitor Your Deployment

### Railway Dashboard Features:

1. **Deployments Tab**
   - View build history
   - Rollback to previous versions
   - See deployment status

2. **Metrics Tab**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

3. **Logs Tab**
   - Real-time application logs
   - Filter by service
   - Search logs

4. **Settings Tab**
   - Environment variables
   - Domains
   - Build settings
   - Restart service

---

## 🔧 Troubleshooting

### Issue 1: Build Fails with "Package libgl1-mesa-glx not found"

**Solution:** Already fixed! Your Dockerfile now uses `libgl1`.

Verify by checking Dockerfile line 7-8:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
```

---

### Issue 2: "Models not loaded" Error

**Possible Causes:**
1. Models not in git repository
2. Models in `.gitignore`
3. Model paths incorrect

**Solution:**
```bash
# Check models are in git
git ls-tree -r HEAD ml/registry/

# Should show:
# ml/registry/cnn_pneumonia.h5
# ml/registry/ann_heart_risk.h5
# ml/registry/text_triage.h5
# ml/registry/*.pkl files
```

If models are missing, see `DEPLOYMENT_FIX.md`.

---

### Issue 3: Database Connection Error

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Verify PostgreSQL is added to project
2. Check `DATABASE_URL` variable is set to `${{Postgres.DATABASE_URL}}`
3. Restart the service

---

### Issue 4: Port Binding Error

**Symptoms:**
```
Error: Address already in use
```

**Solution:**
Railway automatically sets `$PORT` environment variable. Your app uses:
```dockerfile
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

No action needed - Railway handles this automatically.

---

### Issue 5: Out of Memory

**Symptoms:**
```
Killed (OOM)
```

**Solution:**
1. Railway free tier: 512MB RAM
2. Your models total: ~30MB
3. TensorFlow overhead: ~300MB
4. Should fit, but upgrade to Hobby plan ($5/month) if needed

---

### Issue 6: Slow First Request

**Expected:** First prediction after deployment may take 5-10 seconds (model loading).

**Solution:** Models are loaded at startup, not per-request. Subsequent requests are fast (<1s).

---

## 🎯 Post-Deployment Checklist

After successful deployment:

- [ ] Health endpoint returns `{"models_loaded": true}`
- [ ] Test image prediction with sample X-ray
- [ ] Test tabular prediction with sample data
- [ ] Test text prediction with sample symptoms
- [ ] Frontend loads and displays dashboard
- [ ] Create a test case and review in HITL interface
- [ ] Generate a PDF report
- [ ] Add deployment URL to your presentation
- [ ] Share demo link with hackathon judges

---

## 💰 Cost Estimates

### Railway Pricing:

**Free Tier (Trial):**
- $5 of free credits
- 512MB RAM
- 1 vCPU
- 500 hours/month
- **Perfect for hackathon demo!**

**Hobby Plan: $5/month**
- $5 credit/month
- 8GB RAM
- 8 vCPUs
- Unlimited hours
- Custom domains

**For Hackathon:** Free tier is sufficient!

---

## 🔗 Useful Railway Commands (CLI)

Install Railway CLI:
```bash
npm install -g @railway/cli
```

Login:
```bash
railway login
```

Link to project:
```bash
railway link
```

View logs:
```bash
railway logs
```

Deploy:
```bash
railway up
```

---

## 📝 Environment Variables Quick Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | (Railway) | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | - | JWT secret (32+ chars) |
| `GROQ_API_KEY` | ❌ | - | For LLM narratives |
| `MODEL_REGISTRY_PATH` | ❌ | `ml/registry` | Model storage path |
| `UPLOAD_DIR` | ❌ | `data/uploads` | File uploads |
| `REPORTS_DIR` | ❌ | `data/reports` | PDF reports |

---

## 🚀 Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Sign up Railway | 2 min | ⚠️ TODO |
| Create project | 1 min | ⚠️ TODO |
| Configure variables | 3 min | ⚠️ TODO |
| Add PostgreSQL | 2 min | ⚠️ TODO |
| First build | 8 min | ⚠️ TODO |
| Test endpoints | 2 min | ⚠️ TODO |
| **Total** | **~18 min** | |

---

## 🎬 Demo Preparation

Before your hackathon presentation:

1. **Prepare test data:**
   - Sample X-ray image
   - Sample clinical metrics
   - Sample symptom text

2. **Create demo case:**
   - Upload all three modalities
   - Show predictions with explainability
   - Demonstrate HITL review
   - Generate final report

3. **Test workflow:**
   - Run through entire workflow once
   - Ensure all endpoints respond quickly
   - Check PDF generation works

4. **Backup plan:**
   - Screenshot key pages
   - Record video demo (in case of internet issues)
   - Have local deployment running

---

## 🔗 Helpful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app
- **Your GitHub Repo:** https://github.com/hammadAsher100/smit-hackathon
- **Groq Console:** https://console.groq.com
- **Railway Status:** https://railway.app/status

---

## 📧 Support

**Railway Support:**
- Discord: https://discord.gg/railway
- Email: team@railway.app

**Common Issues:**
- Check `RAILWAY_DEPLOYMENT_GUIDE.md` (this file)
- See `DEPLOYMENT_FIX.md` for model-related issues
- Check Railway logs for error messages

---

## ✅ Success Criteria

Your deployment is ready when:

1. ✅ Health endpoint returns `models_loaded: true`
2. ✅ All three prediction endpoints work
3. ✅ Frontend loads without errors
4. ✅ Database persists cases and predictions
5. ✅ HITL workflow records decisions
6. ✅ PDF reports generate successfully
7. ✅ Response times < 2 seconds per prediction

---

## 🎉 You're Ready!

Once deployed, your demo URL will be:
```
https://[your-app-name].up.railway.app
```

**Add this to:**
- Your presentation (Slide 10)
- Your README
- Your hackathon submission
- Your GitHub repo description

**Good luck with your hackathon! 🚀**

---

*Last updated: July 12, 2026*
