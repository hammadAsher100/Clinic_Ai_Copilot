# 🏃 Run Clinical AI Co-Pilot Locally

Quick guide to run the app on your local Windows machine for testing before deployment.

---

## ✅ Prerequisites Check

Run these commands to verify your setup:

```powershell
# Check Python version (need 3.10+)
python --version

# Check virtual environment exists
Test-Path .venv

# Check models exist
Test-Path ml\registry\cnn_pneumonia.h5
Test-Path ml\registry\ann_heart_risk.h5
Test-Path ml\registry\text_triage.h5
```

---

## 🚀 Quick Start (2 minutes)

### Option A: Using Existing Virtual Environment

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Verify dependencies installed
pip list | Select-String -Pattern "fastapi|tensorflow"

# 3. Run the app
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Open in browser
# Go to: http://localhost:8000
```

### Option B: Fresh Setup

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🗄️ Database Configuration

### SQLite (Default - Easy for Local Testing)

Your `.env` file should have:
```bash
DATABASE_URL=sqlite:///./clinical_copilot.db
```

**Pros:**
- ✅ No setup required
- ✅ Single file database
- ✅ Perfect for testing

**Cons:**
- ❌ Data doesn't persist across containers
- ❌ Not suitable for production

### PostgreSQL (Optional - For Production-Like Testing)

If you want to test with PostgreSQL locally:

```powershell
# 1. Start PostgreSQL with Docker
docker run -d `
  --name copilot-postgres `
  -e POSTGRES_USER=user `
  -e POSTGRES_PASSWORD=password `
  -e POSTGRES_DB=copilot `
  -p 5432:5432 `
  postgres:15

# 2. Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/copilot

# 3. Run the app
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Test Your Local Setup

### 1. Health Check

Open browser or use curl:
```powershell
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "models_loaded": true
}
```

### 2. API Documentation

Go to: http://localhost:8000/docs

You'll see interactive Swagger UI with all endpoints.

### 3. Frontend

Go to: http://localhost:8000/

Should redirect to dashboard.

### 4. Test Image Prediction

```powershell
curl -X POST http://localhost:8000/api/v1/predict/image `
  -F "file=@data/raw/xray/test/NORMAL/synth_normal_0000.jpg" `
  -F "patient_name=Local Test"
```

### 5. Test Tabular Prediction

```powershell
$body = @{
  age = 45
  sex = 1
  cp = 2
  trestbps = 130
  chol = 250
  fbs = 0
  restecg = 1
  thalach = 150
  exang = 0
  oldpeak = 1.5
  slope = 1
  ca = 0
  thal = 2
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/predict/tabular `
  -H "Content-Type: application/json" `
  -d $body
```

### 6. Test Text Prediction

```powershell
$body = @{
  symptoms = "fever, cough, fatigue, difficulty breathing"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/predict/text `
  -H "Content-Type: application/json" `
  -d $body
```

---

## 📁 Directory Structure Check

Before running, ensure these exist:

```powershell
# Check data directories
Test-Path data\uploads
Test-Path data\reports

# Create if missing
New-Item -ItemType Directory -Force -Path data\uploads
New-Item -ItemType Directory -Force -Path data\reports
New-Item -ItemType Directory -Force -Path data\processed\tabular
New-Item -ItemType Directory -Force -Path data\processed\text
New-Item -ItemType Directory -Force -Path data\processed\xray
```

---

## 🐛 Common Issues & Solutions

### Issue 1: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue 2: TensorFlow Not Found

**Error:**
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solution:**
```powershell
# Install TensorFlow CPU version
pip install tensorflow-cpu==2.16.1
```

---

### Issue 3: Models Not Loading

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ml/registry/cnn_pneumonia.h5'
```

**Solution:**
```powershell
# Check models exist
ls ml\registry\*.h5

# If missing, you need to train them:
python ml/cnn/train.py
python ml/ann/train.py
python ml/text_model/train.py
```

---

### Issue 4: Port Already in Use

**Error:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

---

### Issue 5: Database Locked (SQLite)

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```powershell
# Stop all running instances
# Delete the database file
Remove-Item clinical_copilot.db

# Restart the app (database will be recreated)
uvicorn api.main:app --reload
```

---

## 🔧 Development Mode Features

### Auto-Reload

The `--reload` flag watches for file changes and restarts automatically:

```powershell
uvicorn api.main:app --reload
```

**Great for:**
- Testing frontend changes
- Debugging API routes
- Iterating on model inference code

---

### Debug Logging

Set log level in `.env`:
```bash
LOG_LEVEL=DEBUG
```

You'll see detailed logs:
```
DEBUG:api:Request received: POST /api/v1/predict/image
DEBUG:prediction:Loading image: 2048 bytes
DEBUG:prediction:Preprocessing: resizing to 224x224
DEBUG:prediction:CNN prediction: 0.8945
DEBUG:prediction:Generating Grad-CAM...
```

---

### Hot Reload Frontend

The frontend is static files, so changes appear immediately (just refresh browser).

---

## 📊 Monitoring Local App

### View Logs

PowerShell terminal shows real-time logs:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Initialising database tables...
INFO:     Loading ML models into memory...
INFO:     CNN model loaded from ml/registry/cnn_pneumonia.h5
INFO:     ANN model loaded from ml/registry/ann_heart_risk.h5
INFO:     Text model loaded from ml/registry/text_triage.h5
INFO:     Clinical AI Co-Pilot API is ready
INFO:     Application startup complete.
```

---

### Database Inspection (SQLite)

```powershell
# Install SQLite browser
winget install DB.Browser.SQLite

# Or use CLI
sqlite3 clinical_copilot.db

# View tables
.tables

# Query cases
SELECT * FROM cases;

# Query predictions
SELECT * FROM model_predictions;

# Exit
.quit
```

---

## 🧹 Clean Up

### Stop the Server

Press `CTRL+C` in the terminal running uvicorn.

### Deactivate Virtual Environment

```powershell
deactivate
```

### Clean Database (Fresh Start)

```powershell
Remove-Item clinical_copilot.db
Remove-Item data\uploads\*
Remove-Item data\reports\*
```

---

## 🚀 Performance Tips

### Speed Up Model Loading

Models load at startup (takes ~10 seconds). To speed up:

1. **Use SSD** for model storage
2. **Keep models small** (already optimized)
3. **Disable unnecessary models** in development:

Edit `api/services/inference_service.py`:
```python
def load_all_models():
    # Comment out models you're not testing
    # load_cnn_model()
    load_ann_model()
    # load_text_model()
```

---

### Reduce Memory Usage

If running out of RAM:

```python
# In model files, add:
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')  # Disable GPU
```

---

## 🎯 Local Development Workflow

### Typical Session:

1. **Start app:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   uvicorn api.main:app --reload
   ```

2. **Open browser:**
   - Main app: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Database: SQLite Browser

3. **Make changes:**
   - Edit code in VS Code
   - App auto-reloads
   - Refresh browser

4. **Test:**
   - Use Swagger UI for API testing
   - Use frontend for full workflow
   - Check logs in terminal

5. **Commit:**
   ```powershell
   git add .
   git commit -m "Your changes"
   git push
   ```

---

## 📦 Build Docker Image Locally

Test your Docker build before deploying:

```powershell
# Build image
docker build -t clinical-ai-copilot .

# Run container
docker run -p 8000:8000 `
  -e DATABASE_URL=sqlite:///./clinical_copilot.db `
  -e SECRET_KEY=test-secret-key `
  clinical-ai-copilot

# Test
curl http://localhost:8000/health
```

---

## 🔗 Useful Commands Reference

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Deactivate venv
deactivate

# Run app
uvicorn api.main:app --reload

# Run app on different port
uvicorn api.main:app --port 8001 --reload

# Run with specific host
uvicorn api.main:app --host 127.0.0.1 --port 8000

# Check Python packages
pip list

# Update a package
pip install --upgrade fastapi

# Freeze dependencies
pip freeze > requirements.txt

# Run tests
pytest tests/ -v

# Run linting
flake8 api/ ml/

# Format code
black api/ ml/
```

---

## 🎓 Learn More

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Uvicorn Docs:** https://www.uvicorn.org
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org
- **TensorFlow Docs:** https://www.tensorflow.org

---

## ✅ Pre-Deployment Checklist

Before deploying to Railway, test locally:

- [ ] Health endpoint returns 200
- [ ] All three prediction endpoints work
- [ ] Frontend loads without errors
- [ ] Create case workflow works
- [ ] HITL review and decision saving works
- [ ] PDF report generation works
- [ ] LLM narrative generation works (if Groq key set)
- [ ] Database persists data correctly
- [ ] No errors in server logs
- [ ] Models load successfully at startup

---

**You're ready for local development! 🎉**

Run: `uvicorn api.main:app --reload` and start coding!
