# 🚨 CRITICAL DEPLOYMENT FIXES NEEDED

## Problem 1: Docker Build Failure ✅ FIXED
**Error:** `Package 'libgl1-mesa-glx' has no installation candidate`

**Cause:** Package name changed in Debian Trixie (Python 3.10-slim base image)

**Solution:** Updated Dockerfile to use `libgl1` instead of `libgl1-mesa-glx`

---

## Problem 2: Models Not Deployed ⚠️ CRITICAL
**Error:** Models are in `.gitignore`, so they're not in your git repository!

**Cause:** 
```gitignore
ml/registry/*.h5
ml/registry/*.pkl
```

**Impact:** 
- Render builds your app but models are missing
- API will return "Model not loaded" errors
- All prediction endpoints will fail

### Solution Options:

### **Option A: Commit Models to Git (Quick Fix - 2 minutes)**

**For Hackathon Demo (models are small enough):**

1. **Check model sizes:**
   - `cnn_pneumonia.h5` = 26 MB
   - `text_triage.h5` = 4 MB
   - `ann_heart_risk.h5` = 76 KB
   - Total = ~30 MB (within GitHub 100MB file limit)

2. **Remove from .gitignore:**
   ```bash
   # Edit .gitignore and comment out these lines:
   # ml/registry/*.h5
   # ml/registry/*.pkl
   ```

3. **Commit models:**
   ```bash
   git add ml/registry/*.h5 ml/registry/*.pkl
   git commit -m "Add trained models for deployment"
   git push origin main
   ```

**Pros:** Immediate fix, works for hackathon
**Cons:** Not best practice for production (but fine for demo)

---

### **Option B: Use Render Persistent Disk (Production Approach - 15 minutes)**

1. **Update `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: clinical-ai-copilot
       env: docker
       region: oregon
       plan: free
       branch: main
       healthCheckPath: /health
       # Add disk for model storage
       disk:
         name: model-storage
         mountPath: /app/ml/registry
         sizeGB: 1
       envVars:
         - key: PYTHON_VERSION
           value: "3.10"
         - key: DATABASE_URL
           fromDatabase:
             name: copilot-db
             property: connectionString
         - key: GROQ_API_KEY
           sync: false
         - key: SECRET_KEY
           generateValue: true
         - key: ACCESS_TOKEN_EXPIRE_MINUTES
           value: "1440"
       autoDeploy: true
   ```

2. **Upload models via Render dashboard:**
   - After first deploy, SSH into Render instance
   - Upload models to `/app/ml/registry/`

**Pros:** Best practice, keeps git clean
**Cons:** Requires manual upload, more complex

---

### **Option C: Download Models at Build Time (Alternative - 10 minutes)**

**Use model hosting service (Hugging Face, Google Drive, S3):**

1. **Upload models to Hugging Face Hub or Google Drive**

2. **Update Dockerfile to download at build:**
   ```dockerfile
   # After COPY . .
   RUN python scripts/download_models.py
   ```

3. **Create `scripts/download_models.py`:**
   ```python
   import os
   import urllib.request
   from pathlib import Path
   
   REGISTRY = Path("ml/registry")
   REGISTRY.mkdir(parents=True, exist_ok=True)
   
   MODELS = {
       "cnn_pneumonia.h5": "YOUR_DOWNLOAD_URL",
       "ann_heart_risk.h5": "YOUR_DOWNLOAD_URL",
       # ... etc
   }
   
   for filename, url in MODELS.items():
       filepath = REGISTRY / filename
       if not filepath.exists():
           print(f"Downloading {filename}...")
           urllib.request.urlretrieve(url, filepath)
   ```

---

## Problem 3: GitHub Commit Mismatch

**Your local Dockerfile already has the fix, but GitHub has the old version!**

**Solution:** Commit and push the updated Dockerfile:

```bash
git add Dockerfile
git commit -m "Fix Docker build: Update package names for Debian Trixie"
git push origin main
```

---

## RECOMMENDED QUICK FIX FOR HACKATHON (5 minutes)

**For immediate deployment before presentation:**

1. **Update .gitignore** (comment out model ignores):
   ```gitignore
   # Model artifacts - TEMPORARILY ENABLED FOR DEPLOYMENT
   # ml/registry/*.h5
   # ml/registry/*.pkl
   # ml/registry/*.joblib
   ```

2. **Commit everything:**
   ```bash
   git add .gitignore Dockerfile ml/registry/
   git commit -m "Fix deployment: Add models and update Dockerfile"
   git push origin main
   ```

3. **Verify in GitHub:**
   - Go to your repo: https://github.com/hammadAsher100/smit-hackathon
   - Check `ml/registry/` has 8 files (5 .pkl, 3 .h5)
   - Check `Dockerfile` has `libgl1` not `libgl1-mesa-glx`

4. **Trigger Render redeploy:**
   - Render will auto-deploy on git push
   - OR manually trigger from Render dashboard

---

## Problem 4: Environment Variables

**Check these are set in Render dashboard:**

Required:
- `DATABASE_URL` - Auto-configured by Render database
- `SECRET_KEY` - For JWT auth (auto-generated in render.yaml)

Optional (but recommended):
- `GROQ_API_KEY` - For LLM narrative generation
- `GROQ_API_BASE_URL` - Default: https://api.groq.com/openai/v1
- `GROQ_MODEL` - Default: llama-3.1-70b-versatile

Without GROQ_API_KEY, the app will use fallback template narratives.

---

## Problem 5: Database Initialization

**Render PostgreSQL URL format:** `postgresql://user:password@host:5432/dbname`

**Your app expects:** SQLAlchemy-compatible URL

**Solution:** ✅ Already handled by `api/db/session.py`

No action needed - your code already handles PostgreSQL URLs correctly.

---

## Deployment Checklist

### Pre-Deploy
- [ ] Update `.gitignore` to include models (Option A)
- [ ] Commit updated `Dockerfile` 
- [ ] Commit models to git
- [ ] Push to GitHub

### During Deploy (Render Dashboard)
- [ ] Set `GROQ_API_KEY` in environment variables
- [ ] Verify `DATABASE_URL` is connected
- [ ] Check build logs for package installation success

### Post-Deploy
- [ ] Test `/health` endpoint
- [ ] Test `/api/v1/predict/image` with sample X-ray
- [ ] Test `/api/v1/predict/tabular` with heart disease features
- [ ] Test `/api/v1/predict/text` with symptoms
- [ ] Test frontend at root URL

---

## Quick Test Commands (After Deploy)

```bash
# 1. Health check
curl https://your-app.onrender.com/health

# 2. Test image prediction
curl -X POST https://your-app.onrender.com/api/v1/predict/image \
  -F "file=@data/raw/xray/test/NORMAL/synth_normal_0000.jpg" \
  -F "patient_name=Test Patient"

# 3. Test tabular prediction  
curl -X POST https://your-app.onrender.com/api/v1/predict/tabular \
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

---

## Expected Timeline

- **Option A (Quick Fix):** 5 minutes
  - Edit .gitignore: 1 min
  - Git commit/push: 2 min
  - Render build: 5-8 min
  - Testing: 2 min
  - **Total: ~15 minutes**

- **Option B (Persistent Disk):** 20-30 minutes
  - Update render.yaml: 5 min
  - Deploy + provision disk: 10 min
  - SSH and upload models: 10 min
  - Testing: 5 min

- **Option C (Download at Build):** 15-20 minutes
  - Upload to model host: 5 min
  - Write download script: 5 min
  - Test locally: 5 min
  - Deploy: 8 min

---

## Common Errors After Fix

### Error: "Model not loaded"
**Cause:** Models didn't commit to git or download script failed
**Fix:** Check GitHub repo has model files, or check build logs

### Error: "Database connection failed"
**Cause:** DATABASE_URL not set or malformed
**Fix:** Check Render environment variables, verify PostgreSQL is running

### Error: "GROQ API error"
**Cause:** Invalid or missing GROQ_API_KEY
**Fix:** Add key in Render dashboard, or app will use fallback templates

### Error: 502 Bad Gateway
**Cause:** App crashed during startup (likely model loading)
**Fix:** Check Render logs for stack trace, verify all dependencies installed

---

## Support Resources

- **Render Logs:** Dashboard → Logs tab (real-time streaming)
- **Render Shell:** Dashboard → Shell tab (SSH into container)
- **Database:** Dashboard → Databases → copilot-db → Connect
- **Your Repo:** https://github.com/hammadAsher100/smit-hackathon

---

## Post-Hackathon Production Improvements

After the hackathon, consider:

1. **Model Versioning:** Use MLflow Model Registry or DVC
2. **CI/CD:** Automate model training → registry → deployment
3. **Monitoring:** Add model performance tracking (accuracy drift)
4. **Caching:** Cache model predictions for identical inputs
5. **Rate Limiting:** Protect API from abuse
6. **Authentication:** Enable JWT token requirement
7. **Logging:** Centralized logging (CloudWatch, DataDog)
8. **Backup:** Automated database backups

---

**NEXT STEP:** Follow "Option A: Quick Fix" above to get deployed in 15 minutes! 🚀
