# 🚀 Deploy Clinical AI Co-Pilot NOW

**Quick deployment guide - Choose your platform and follow the steps!**

---

## ✅ What's Ready

Your project is now **deployment-ready** with:
- ✅ Optimized Dockerfile
- ✅ Railway configuration (`railway.json`)
- ✅ Render blueprint (`render.yaml`)
- ✅ Docker ignore file (`.dockerignore`)
- ✅ Trained ML models in `ml/registry/`
- ✅ Complete modular UI
- ✅ Health check endpoint

---

## 🎯 Recommended: Railway (5 Minutes)

### **Why Railway?**
- Fastest deployment (literally 5 minutes)
- Free tier available
- Auto HTTPS
- Perfect for hackathon demos

### **Steps**

#### **1. Push to GitHub** (if not already)
```bash
# In your project directory
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### **2. Sign Up for Railway**
1. Go to: https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway

#### **3. Create New Project**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `mlops-hackathon`
4. Railway will auto-detect your Dockerfile ✅

#### **4. Add PostgreSQL**
1. In your project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Database will be created and linked automatically ✅

#### **5. Set Environment Variables**
Click on your service (web) → "Variables" tab → "RAW Editor":

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_random_secure_key_here_min_32_chars
DATABASE_URL=${{Postgres.DATABASE_URL}}
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### **6. Deploy!**
- Railway will automatically start building
- Watch the deployment logs
- Wait 3-5 minutes
- You'll get a URL like: `https://mlops-hackathon-production.up.railway.app`

#### **7. Access Your App**
Click "Generate Domain" in Railway dashboard, then:
```
https://your-custom-domain.up.railway.app
```

Login with: `clinician` / `demo2026`

---

## 🔧 Alternative: Render (10 Minutes)

### **Steps**

#### **1. Sign Up**
- Go to: https://render.com
- Sign up with GitHub

#### **2. Deploy from render.yaml**
1. Dashboard → "New" → "Blueprint"
2. Connect your GitHub repo
3. Select `render.yaml`
4. Click "Apply"

#### **3. Set Secrets**
In the web service created:
- Go to "Environment"
- Add `GROQ_API_KEY` (your key)
- `SECRET_KEY` is auto-generated ✅

#### **4. Wait for Deployment**
- First build takes ~10 minutes
- Access at: `https://clinical-ai-copilot.onrender.com`

---

## 🤗 Alternative: Hugging Face Spaces

### **Quick Deploy**

#### **1. Create Account**
- Go to: https://huggingface.co/join
- Sign up (free)

#### **2. Create New Space**
1. Click profile → "New Space"
2. Name: `clinical-ai-copilot`
3. SDK: **Docker**
4. Hardware: CPU basic (free)
5. Click "Create Space"

#### **3. Push Code**
```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/clinical-ai-copilot
cd clinical-ai-copilot

# Copy your project
cp -r /path/to/mlops-hackathon/* .

# For Hugging Face, update Dockerfile port to 7860
# Edit Dockerfile, change last line to:
# CMD uvicorn api.main:app --host 0.0.0.0 --port 7860

# Commit and push
git add .
git commit -m "Deploy to Hugging Face"
git push
```

#### **4. Add Secrets**
In Space settings → "Repository secrets":
```
GROQ_API_KEY=your_key
SECRET_KEY=your_secret
DATABASE_URL=sqlite:///./clinical_copilot.db
```

#### **5. Wait & Access**
- Build takes ~5 minutes
- Access at: `https://huggingface.co/spaces/YOUR_USERNAME/clinical-ai-copilot`

---

## 🐳 Alternative: Docker Compose (Your Own Server)

### **If you have a VPS (DigitalOcean, AWS EC2, etc.)**

#### **1. SSH to Your Server**
```bash
ssh user@your-server-ip
```

#### **2. Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
```

#### **3. Clone Your Repo**
```bash
git clone https://github.com/yourusername/mlops-hackathon.git
cd mlops-hackathon
```

#### **4. Create .env File**
```bash
nano .env
```

Add:
```env
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://copilot_user:securepassword@db:5432/copilot
DB_PASSWORD=securepassword
```

#### **5. Deploy**
```bash
docker-compose up -d

# Check logs
docker-compose logs -f api

# Check status
docker-compose ps
```

#### **6. Access**
```
http://your-server-ip:8000
```

For HTTPS, configure Nginx or use Caddy:
```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Create Caddyfile
sudo nano /etc/caddy/Caddyfile
```

Add:
```
your-domain.com {
    reverse_proxy localhost:8000
}
```

```bash
sudo systemctl restart caddy
```

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] **Code is committed** to Git
- [ ] **GROQ_API_KEY** is available
- [ ] **SECRET_KEY** generated (32+ characters)
- [ ] **Models exist** in `ml/registry/`
- [ ] **.env** file NOT committed (in .gitignore)
- [ ] **Dockerfile** optimized
- [ ] **requirements.txt** up to date

---

## 🔑 Get Your GROQ API Key

If you don't have a GROQ API key yet:

1. Go to: https://console.groq.com
2. Sign up (free)
3. Go to "API Keys"
4. Click "Create API Key"
5. Copy your key
6. Use it in environment variables

**Note**: The LLM narrator will use this for generating clinical summaries.

---

## 🎯 My Recommendation

**For Hackathon/Demo**: ⭐⭐⭐⭐⭐ **Railway**
- Fastest (5 min)
- Easiest
- Free tier
- Auto HTTPS
- Perfect for showcasing

**For Production**: ⭐⭐⭐⭐ **Render**
- Reliable
- Free tier with PostgreSQL
- Production-ready
- Good for long-term hosting

**For ML Showcase**: ⭐⭐⭐⭐ **Hugging Face**
- Great visibility
- ML community
- Free hosting
- GPU options

---

## 🚀 Quick Commands Summary

### **Railway Deployment**
```bash
# 1. Push code
git push origin main

# 2. Go to railway.app, connect repo, add PostgreSQL
# 3. Set GROQ_API_KEY and SECRET_KEY
# 4. Deploy (automatic)
```

### **Render Deployment**
```bash
# 1. Push code with render.yaml
git push origin main

# 2. Go to render.com, create blueprint
# 3. Set GROQ_API_KEY
# 4. Deploy (automatic)
```

### **Local Docker**
```bash
# Build and run
docker-compose up -d

# Check
docker-compose ps
docker-compose logs -f api
```

---

## 🆘 Troubleshooting

### **"Models not found" error**
- Check `ml/registry/` has model files
- Ensure models are included in Docker image
- Check volume mounts in docker-compose

### **Database connection error**
- Verify DATABASE_URL is set
- Check database service is running
- Wait for database health check

### **Port already in use**
- Change port in docker-compose or Dockerfile
- Kill existing process on port 8000
- Use different port (e.g., 8080)

### **Build timeout**
- Model files are large (~30MB)
- Increase build timeout in platform settings
- Consider model compression or lazy loading

---

## 📞 Need Help?

**Documentation**:
- Full guide: `DEPLOYMENT_GUIDE.md`
- Architecture: `frontend/UI_MODULES.md`
- Quick start: `frontend/QUICK_START.md`

**Support**:
- Check Railway/Render logs
- Review health endpoint: `/health`
- Check browser console (F12)

---

## ✅ Post-Deployment

After deployment:

1. **Test Login**: clinician / demo2026
2. **Create Test Case**: Use dashboard
3. **Try Each Module**:
   - X-Ray analysis
   - Heart assessment
   - Symptom classifier
4. **Generate Report**: Complete workflow
5. **Share URL**: With your team/judges

---

**Ready to deploy? Pick a platform above and follow the steps!** 🚀

**My recommendation**: Start with **Railway** for the fastest deployment (5 minutes)!
