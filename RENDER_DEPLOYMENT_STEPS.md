# 🚀 Render Deployment - Step-by-Step Guide

## **Complete Deployment Process for Render**

---

## 📋 **Prerequisites**

Before you start:
- [ ] GitHub account with your code pushed
- [ ] GROQ API key (get from https://console.groq.com)
- [ ] 15-20 minutes of time

---

## 🎯 **Step-by-Step Deployment**

### **Step 1: Prepare Your Repository**

#### **1.1 Commit All Changes**
```bash
cd d:\Projects\Hackathon\mlops-hackathon

# Check what files need to be committed
git status

# Add all files
git add .

# Commit with message
git commit -m "Ready for Render deployment with modular UI"

# Push to GitHub
git push origin main
```

**Verify**: Go to your GitHub repo and confirm all files are there, especially:
- ✅ `render.yaml`
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `frontend/` folder with all HTML files
- ✅ `ml/registry/` folder with model files

---

### **Step 2: Sign Up for Render**

#### **2.1 Create Account**
1. Go to: **https://render.com**
2. Click "**Get Started**" (top right)
3. Choose "**Sign Up with GitHub**"
4. Authorize Render to access your GitHub repositories
5. Confirm your email address

#### **2.2 Complete Profile**
- You'll be taken to the Render Dashboard
- No credit card required for free tier ✅

---

### **Step 3: Deploy Using Blueprint (Easiest Method)**

#### **3.1 Create Blueprint**
1. In Render Dashboard, click "**New +**" (top right)
2. Select "**Blueprint**"
3. Click "**Connect GitHub**" if not already connected
4. Find and select your `mlops-hackathon` repository
5. Render will auto-detect `render.yaml` ✅
6. Click "**Apply**"

#### **3.2 Review Services**
Render will show you what it's creating:
- ✅ Web Service: `clinical-ai-copilot`
- ✅ PostgreSQL Database: `copilot-db`

Click "**Apply** to proceed

---

### **Step 4: Configure Environment Variables**

#### **4.1 Get Your GROQ API Key**
```bash
# If you don't have one:
# 1. Go to https://console.groq.com
# 2. Sign up (free)
# 3. Go to "API Keys" section
# 4. Click "Create API Key"
# 5. Copy the key (starts with "gsk_...")
```

#### **4.2 Add Environment Variables**
1. In Render Dashboard, click on your **web service** (`clinical-ai-copilot`)
2. Go to "**Environment**" tab (left sidebar)
3. Click "**Add Environment Variable**"

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `GROQ_API_KEY` | `gsk_your_actual_key_here` | Your Groq API key |
| `SECRET_KEY` | (auto-generated) ✅ | Leave as is |
| `DATABASE_URL` | (auto-filled from database) ✅ | Leave as is |

**Note**: `SECRET_KEY` and `DATABASE_URL` are automatically set by Render through the blueprint.

#### **4.3 Save Changes**
Click "**Save Changes**" at the bottom

---

### **Step 5: Monitor Deployment**

#### **5.1 Watch Build Logs**
1. Stay on your web service page
2. Go to "**Logs**" tab
3. You'll see the build process:
   ```
   ==> Building...
   ==> Installing system dependencies...
   ==> Installing Python packages...
   ==> Building Docker image...
   ==> Starting deployment...
   ```

#### **5.2 Wait for Completion**
- **First deployment**: 10-15 minutes (downloading dependencies)
- **Subsequent deployments**: 5-7 minutes
- Status will change from "Building" → "Live" 🟢

#### **5.3 Check Build Progress**
Look for these log messages:
```
✅ Dependencies installed
✅ Loading ML models...
✅ CNN model loaded
✅ ANN model loaded
✅ Text model loaded
✅ Application startup complete
✅ Uvicorn running
```

---

### **Step 6: Access Your Deployed Application**

#### **6.1 Get Your URL**
1. In your web service dashboard
2. Look at the top - you'll see your URL:
   ```
   https://clinical-ai-copilot.onrender.com
   ```
3. Click on the URL or copy it

#### **6.2 Test the Deployment**
1. Open the URL in your browser
2. You should see the **login page**
3. Use credentials:
   - **Username**: `clinician`
   - **Password**: `demo2026`

#### **6.3 Verify Everything Works**
After login, you should see the **Dashboard** with:
- ✅ Statistics cards (cases, pending, completed)
- ✅ Module cards (X-Ray, Heart, Symptoms, Documents)
- ✅ Navigation menu at top
- ✅ Recent activity section

---

### **Step 7: Test All Features**

#### **7.1 Create a Test Case**
1. Click "**Create New Case**" button
2. Enter patient name (e.g., "Test Patient")
3. Choose to start with X-Ray Analysis

#### **7.2 Test X-Ray Module**
1. Navigate to X-Ray Analysis
2. Upload a test image (any chest X-ray image)
3. Click "Analyze"
4. Verify you see:
   - ✅ Prediction result (NORMAL/PNEUMONIA)
   - ✅ Confidence score
   - ✅ Grad-CAM heatmap (if available)

#### **7.3 Test Heart Assessment**
1. Navigate to Heart Assessment
2. Use pre-filled values or modify them
3. Click "Assess Risk"
4. Verify you see:
   - ✅ Risk level (HIGH_RISK/LOW_RISK)
   - ✅ Confidence gauge
   - ✅ SHAP chart (feature importance)

#### **7.4 Test Symptom Classifier**
1. Navigate to Symptom Classifier
2. Enter symptoms (e.g., "headache, fever, cough")
3. Click "Classify Symptoms"
4. Verify you see:
   - ✅ Primary condition
   - ✅ Confidence score
   - ✅ Top-3 differential diagnoses

#### **7.5 Test Complete Workflow**
1. Complete all analyses for one case
2. Go to **Review Dashboard**
3. Select your case
4. Review all predictions
5. Click "Generate Report"
6. Download the PDF report

---

## 🔧 **Troubleshooting**

### **Issue: Build Failed**

**Check Logs**:
1. Go to "Logs" tab
2. Scroll to find the error message
3. Common issues:

| Error | Solution |
|-------|----------|
| "No space left on device" | Render free tier disk limit. Remove large unused files |
| "Requirements installation failed" | Check `requirements.txt` for compatibility |
| "Model file not found" | Ensure `ml/registry/` has all model files committed |
| "Port already in use" | This shouldn't happen on Render (auto-handled) |

**Fix and Redeploy**:
```bash
# Fix the issue in your code
git add .
git commit -m "Fix deployment issue"
git push origin main

# Render will auto-redeploy
```

---

### **Issue: Models Not Loading**

**Symptoms**: "Model loading failed" in logs

**Solution**:
```bash
# Verify models exist
ls -lh ml/registry/

# Should see:
# cnn_pneumonia.h5 (~26 MB)
# ann_heart_risk.h5 (~77 KB)
# text_triage.h5 (~4 MB)

# If missing, train models first or download them
```

---

### **Issue: Database Connection Error**

**Symptoms**: "Could not connect to database"

**Solution**:
1. Go to your PostgreSQL database in Render
2. Check it's "Available" (green status)
3. Verify `DATABASE_URL` environment variable is set
4. Wait for database to fully initialize (1-2 minutes)

---

### **Issue: 404 Error on Frontend Pages**

**Symptoms**: Login works but dashboard returns 404

**Solution**:
1. Check `frontend/` folder exists in repo
2. Verify all HTML files are committed
3. Check `api/main.py` has correct static file mounting:
   ```python
   app.mount("/static/frontend", StaticFiles(directory=str(frontend_dir), html=True))
   ```

---

## 🎨 **Custom Domain (Optional)**

### **Add Your Own Domain**

#### **Step 1: Get a Domain**
- Buy from: Namecheap, Google Domains, GoDaddy, etc.

#### **Step 2: Configure in Render**
1. Go to your web service
2. Click "**Settings**" tab
3. Scroll to "**Custom Domain**"
4. Click "**Add Custom Domain**"
5. Enter your domain (e.g., `clinicalai.yourdomain.com`)
6. Click "Add"

#### **Step 3: Update DNS**
Render will show you DNS records to add:
1. Go to your domain provider
2. Add the CNAME record:
   ```
   Type: CNAME
   Name: clinicalai (or @ for root)
   Value: clinical-ai-copilot.onrender.com
   ```
3. Wait 5-60 minutes for DNS propagation

#### **Step 4: Enable HTTPS**
- Render automatically provisions SSL certificate
- Your site will be accessible at `https://yourdomain.com`

---

## 📊 **Monitoring & Maintenance**

### **Monitor Your App**

#### **View Logs**
```
Dashboard → Your Service → Logs tab
```
- Real-time logs
- Error tracking
- Request monitoring

#### **Check Metrics**
```
Dashboard → Your Service → Metrics tab
```
- CPU usage
- Memory usage
- Request rate
- Response times

#### **Set Up Alerts (Optional)**
1. Go to "Settings" tab
2. Scroll to "Health Check Path"
3. Set to `/health`
4. Render will ping this endpoint
5. Get notified if app goes down

---

### **Database Management**

#### **Access Database**
1. Go to your PostgreSQL database in Render
2. Note the connection string
3. Use any PostgreSQL client:
   ```bash
   psql "postgresql://user:pass@hostname/dbname"
   ```

#### **View Data**
```sql
-- See all cases
SELECT * FROM cases;

-- See predictions
SELECT * FROM model_predictions;

-- See HITL decisions
SELECT * FROM hitl_decisions;
```

#### **Backup Database**
```bash
pg_dump "postgresql://user:pass@hostname/dbname" > backup.sql
```

---

## 🔄 **Updating Your App**

### **Deploy Updates**

#### **Method 1: Auto-Deploy (Recommended)**
```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push origin main

# Render automatically detects changes and redeploys
```

#### **Method 2: Manual Deploy**
1. Go to your web service in Render
2. Click "**Manual Deploy**" → "**Deploy latest commit**"

---

### **Rollback to Previous Version**
1. Go to "Events" tab
2. Find the previous successful deployment
3. Click "**Rollback**"

---

## 💰 **Cost Considerations**

### **Free Tier Limits**
- ✅ 750 hours/month (enough for always-on)
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ PostgreSQL database included
- ⚠️ Sleeps after 15 min inactivity (cold starts)

### **Upgrade Options (If Needed)**
| Plan | Cost | Benefits |
|------|------|----------|
| **Free** | $0 | Good for demos, cold starts |
| **Starter** | $7/month | No cold starts, 512 MB RAM |
| **Standard** | $25/month | 2 GB RAM, better performance |

**Recommendation**: Free tier is perfect for hackathon demo!

---

## ✅ **Post-Deployment Checklist**

After deployment, verify:

- [ ] App accessible at Render URL
- [ ] Login works (clinician/demo2026)
- [ ] Dashboard loads with statistics
- [ ] All 6 module pages work
- [ ] Can create new case
- [ ] X-Ray analysis works
- [ ] Heart assessment works
- [ ] Symptom classifier works
- [ ] Review dashboard loads
- [ ] Can generate PDF report
- [ ] Database storing data correctly
- [ ] No errors in Render logs

---

## 🎉 **Success!**

Your Clinical AI Co-Pilot is now deployed on Render!

### **Share Your App**
- URL: `https://clinical-ai-copilot.onrender.com`
- Credentials: `clinician` / `demo2026`
- Demo case: Create → Analyze → Review → Report

### **Next Steps**
1. Share URL with your team
2. Test all features thoroughly
3. Prepare demo for judges
4. Monitor logs for any issues
5. Consider custom domain (optional)

---

## 📞 **Need Help?**

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Project Docs**: Check `DEPLOYMENT_GUIDE.md`
- **UI Guide**: Check `UI_STRUCTURE_GUIDE.md` (next section)

---

**Deployment complete! Now let's understand the UI structure...** 👇
