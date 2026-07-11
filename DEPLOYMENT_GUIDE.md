# Clinical AI Co-Pilot — Production Deployment Guide

**Last Updated**: 2026-07-12  
**Version**: 2.0

---

## 🎯 Recommended Deployment Options

Based on your project structure, here are the **best deployment options** ranked by ease and suitability:

### **🥇 Option 1: Railway (EASIEST - Recommended for Quick Demo)**
- ✅ **Best for**: Hackathon demos, quick deployment
- ⏱️ **Setup Time**: 5-10 minutes
- 💰 **Cost**: Free tier available ($5/month for hobby)
- 🚀 **Difficulty**: ⭐ Very Easy

### **🥈 Option 2: Render (BEST FOR PRODUCTION)**
- ✅ **Best for**: Production deployment, reliable hosting
- ⏱️ **Setup Time**: 10-15 minutes
- 💰 **Cost**: Free tier available (with limitations)
- 🚀 **Difficulty**: ⭐⭐ Easy

### **🥉 Option 3: Hugging Face Spaces**
- ✅ **Best for**: ML demo showcases
- ⏱️ **Setup Time**: 15-20 minutes
- 💰 **Cost**: Free (with GPU options)
- 🚀 **Difficulty**: ⭐⭐ Easy

### **Option 4: AWS/GCP/Azure (Enterprise)**
- ✅ **Best for**: Enterprise production, scalability
- ⏱️ **Setup Time**: 1-2 hours
- 💰 **Cost**: Pay-as-you-go (varies)
- 🚀 **Difficulty**: ⭐⭐⭐⭐ Advanced

---

## 🚀 Quick Deploy: Railway (5 Minutes)

### **Why Railway?**
- ✅ Automatic Docker deployment
- ✅ Free SSL certificates
- ✅ PostgreSQL database included
- ✅ Environment variable management
- ✅ GitHub integration
- ✅ Fast deployment (< 5 min)

### **Step-by-Step Guide**

#### **1. Prepare Your Repository**
```bash
# Make sure your code is committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### **2. Sign Up for Railway**
- Go to: https://railway.app
- Sign up with GitHub (easiest)
- No credit card required for starter tier

#### **3. Create New Project**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `mlops-hackathon` repository
4. Railway will auto-detect Dockerfile ✅

#### **4. Add PostgreSQL Database**
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will create database automatically
3. Database URL will be auto-configured

#### **5. Set Environment Variables**
Click on your service → "Variables" tab:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled by Railway
SECRET_KEY=generate_random_secure_key_here

# Model paths (use defaults)
MODEL_REGISTRY_PATH=ml/registry
```

#### **6. Deploy!**
- Railway will automatically build and deploy
- Wait 3-5 minutes for first deployment
- You'll get a URL like: `https://your-app.up.railway.app`

#### **7. Access Your App**
```
https://your-app.up.railway.app
```

### **Railway Configuration File** (Optional)
Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

---

## 🔧 Detailed Deploy: Render (Production-Ready)

### **Why Render?**
- ✅ Free tier with PostgreSQL
- ✅ Auto-deploy from GitHub
- ✅ Custom domains
- ✅ Background workers support
- ✅ Better for production

### **Step-by-Step Guide**

#### **1. Sign Up**
- Go to: https://render.com
- Sign up with GitHub

#### **2. Create Web Service**
1. Dashboard → "New" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name**: `clinical-ai-copilot`
   - **Region**: Choose closest to users
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Build Command**: (Auto-detected from Dockerfile)
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

#### **3. Create PostgreSQL Database**
1. Dashboard → "New" → "PostgreSQL"
2. Name: `copilot-db`
3. Database Name: `copilot`
4. Copy the "Internal Database URL"

#### **4. Environment Variables**
In your web service, add:
```env
DATABASE_URL=<paste_internal_database_url>
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key_here
PYTHON_VERSION=3.10
```

#### **5. Deploy**
- Click "Create Web Service"
- Wait 10-15 minutes for first build
- Access at: `https://your-service.onrender.com`

### **Render Blueprint** (Optional)
Create `render.yaml`:
```yaml
services:
  - type: web
    name: clinical-ai-copilot
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
      - key: DATABASE_URL
        fromDatabase:
          name: copilot-db
          property: connectionString
      - key: GROQ_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health

databases:
  - name: copilot-db
    databaseName: copilot
    user: copilot_user
    plan: free
```

---

## 🤗 Deploy to Hugging Face Spaces

### **Why Hugging Face?**
- ✅ Perfect for ML demos
- ✅ Free hosting
- ✅ GPU options available
- ✅ Great for showcasing

### **Setup**

#### **1. Create Hugging Face Account**
- Go to: https://huggingface.co
- Sign up (free)

#### **2. Create New Space**
1. Click "New Space"
2. Name: `clinical-ai-copilot`
3. SDK: "Docker"
4. Hardware: "CPU basic" (free) or "GPU" (paid)

#### **3. Push Code to Space**
```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/clinical-ai-copilot
cd clinical-ai-copilot

# Copy your project files
cp -r /path/to/mlops-hackathon/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### **4. Add Environment Variables**
In Space settings → "Repository secrets":
```
GROQ_API_KEY=your_key
SECRET_KEY=your_secret
DATABASE_URL=sqlite:///./clinical_copilot.db
```

#### **5. Custom Dockerfile for Spaces**
Update `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads data/reports ml/registry

# Expose port
EXPOSE 7860

# Hugging Face Spaces uses port 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## ☁️ Deploy to AWS (Enterprise)

### **Option A: AWS Elastic Beanstalk** (Easier)

#### **1. Install AWS CLI & EB CLI**
```bash
pip install awscli awsebcli
aws configure
```

#### **2. Initialize Elastic Beanstalk**
```bash
cd /path/to/mlops-hackathon
eb init -p docker clinical-ai-copilot --region us-east-1
```

#### **3. Create Environment**
```bash
eb create production-env \
  --database.engine postgres \
  --database.username copilot_admin \
  --database.password <secure_password>
```

#### **4. Set Environment Variables**
```bash
eb setenv \
  GROQ_API_KEY=your_key \
  SECRET_KEY=your_secret \
  DATABASE_URL=<postgres_url_from_eb>
```

#### **5. Deploy**
```bash
eb deploy
eb open
```

### **Option B: AWS ECS + Fargate** (More Control)

#### **1. Create ECR Repository**
```bash
aws ecr create-repository --repository-name clinical-ai-copilot
```

#### **2. Build and Push Docker Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t clinical-ai-copilot .

# Tag and push
docker tag clinical-ai-copilot:latest \
  <account_id>.dkr.ecr.us-east-1.amazonaws.com/clinical-ai-copilot:latest

docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/clinical-ai-copilot:latest
```

#### **3. Create ECS Task Definition**
Create `ecs-task-definition.json`:
```json
{
  "family": "clinical-ai-copilot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account_id>.dkr.ecr.us-east-1.amazonaws.com/clinical-ai-copilot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        },
        {
          "name": "GROQ_API_KEY",
          "value": "..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clinical-ai-copilot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### **4. Create RDS PostgreSQL Database**
```bash
aws rds create-db-instance \
  --db-instance-identifier copilot-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <secure_password> \
  --allocated-storage 20
```

#### **5. Create ECS Service**
```bash
aws ecs create-service \
  --cluster clinical-copilot-cluster \
  --service-name api-service \
  --task-definition clinical-ai-copilot \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 🐳 Docker Compose Deployment (VPS/Self-Hosted)

### **Best for**: VPS (DigitalOcean, Linode, Hetzner)

#### **1. Enhanced docker-compose.yml**
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./ml/registry:/app/ml/registry
    environment:
      - DATABASE_URL=postgresql://copilot_user:${DB_PASSWORD}@db:5432/copilot
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=copilot_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=copilot
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U copilot_user -d copilot"]
      interval: 5s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api

volumes:
  pgdata:
```

#### **2. Nginx Configuration**
Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 100M;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### **3. Deploy to VPS**
```bash
# SSH into your VPS
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repo
git clone https://github.com/yourusername/mlops-hackathon.git
cd mlops-hackathon

# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_key
SECRET_KEY=your_secret
DB_PASSWORD=secure_password
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f api
```

---

## 📋 Pre-Deployment Checklist

### **Security**
- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Review API authentication
- [ ] Hide sensitive environment variables

### **Performance**
- [ ] Optimize model loading (lazy loading if needed)
- [ ] Enable gzip compression
- [ ] Set up CDN for static files (optional)
- [ ] Configure database connection pooling
- [ ] Add caching (Redis) if needed

### **Monitoring**
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Add health check endpoints
- [ ] Set up uptime monitoring
- [ ] Database backup strategy

### **Configuration**
- [ ] Set production DATABASE_URL
- [ ] Configure GROQ_API_KEY
- [ ] Update CORS allowed origins
- [ ] Set proper SECRET_KEY
- [ ] Configure file upload limits

---

## 🎯 My Top Recommendation

**For Hackathon Demo**: Use **Railway** ⭐
- Fastest deployment (5 minutes)
- Free tier sufficient
- Automatic HTTPS
- Easy to showcase

**For Production**: Use **Render** ⭐⭐
- Reliable and stable
- Good free tier
- Production-ready features
- Easy scaling

**For Portfolio/Showcase**: Use **Hugging Face Spaces** ⭐⭐
- Perfect for ML demos
- Good visibility
- Free hosting

---

## 🚀 Quick Start: Railway Deployment

Want me to help you deploy to Railway right now? I can:
1. Create the necessary configuration files
2. Optimize the Dockerfile
3. Set up environment variables
4. Guide you through the Railway deployment

Just let me know! 🎉
