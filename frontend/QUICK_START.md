# Quick Start Guide — Clinical AI Co-Pilot

## 🚀 Getting Started

### 1. **Login**
- Navigate to `http://localhost:8000`
- Use demo credentials:
  - **Username**: `clinician`
  - **Password**: `demo2026`

### 2. **Dashboard**
- View system overview and statistics
- Access all modules from the central dashboard

---

## 📋 Module Quick Access

| Module | URL | Purpose |
|--------|-----|---------|
| **Dashboard** | `/static/frontend/dashboard.html` | Central hub & overview |
| **X-Ray Analysis** | `/static/frontend/xray.html` | Chest X-ray pneumonia detection |
| **Heart Assessment** | `/static/frontend/heart.html` | Cardiovascular risk prediction |
| **Symptom Classifier** | `/static/frontend/symptoms.html` | NLP-based symptom analysis |
| **Document Upload** | `/static/frontend/documents.html` | PDF text extraction |
| **Case Management** | `/static/frontend/cases.html` | View/manage all cases |
| **Review** | `/static/frontend/review.html` | HITL review workflow |
| **Reports** | `/static/frontend/report.html` | Download generated reports |

---

## 🎯 Common Workflows

### **Quick X-Ray Analysis**
```
1. Dashboard → Click "Chest X-Ray Analysis"
2. Upload image (drag & drop or click)
3. Click "Analyze X-Ray"
4. View results with Grad-CAM heatmap
5. Optional: Continue to Heart or Symptoms
```

### **Complete Patient Assessment**
```
1. Dashboard → Click "Create New Case"
2. Enter patient name
3. X-Ray Analysis → Upload & analyze
4. Heart Assessment → Enter vitals & analyze
5. Symptom Classifier → Enter symptoms & classify
6. Review Dashboard → Approve/edit predictions
7. Generate Report → Download PDF
```

### **Review Existing Case**
```
1. Dashboard → Click "Cases" or "Case Management"
2. Find case in table
3. Click "Review"
4. Review predictions with explainability
5. Approve/Reject/Edit each modality
6. Generate report when complete
```

---

## 🎨 Navigation

### **Main Menu** (Available on all pages)
- **Dashboard**: Home & overview
- **Cases**: Manage all clinical cases
- **Review**: HITL review workflow
- **Reports**: Download generated reports

### **Back Navigation**
- Each analysis module has a `←` back button to return to Dashboard
- Case ID is preserved across modules via URL parameters

---

## 💡 Tips & Tricks

### **Case Management**
- Create a case once, use across all modules
- Case ID is auto-generated and displayed
- Cases can be selected from dropdown in each module

### **File Uploads**
- **X-Ray**: Supports multiple images (JPG, PNG)
- **Documents**: Supports multiple PDFs
- Drag & drop for faster uploads
- Preview before analysis

### **Results**
- Confidence gauges show prediction certainty
- Grad-CAM highlights X-ray regions of interest
- SHAP shows feature importance for heart risk
- Top-3 shows differential diagnosis for symptoms

### **Workflow Optimization**
- Start with X-Ray → Continue to Heart → Then Symptoms
- Each module offers "Continue to..." buttons
- Review all at once in Review Dashboard

---

## 🔧 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + D` | Go to Dashboard |
| `Alt + C` | Go to Cases |
| `Alt + R` | Go to Review |
| `Enter` | Submit forms |

---

## ⚠️ Common Issues

### **"Not authenticated" error**
- Solution: Login again at `/static/frontend/index.html`

### **"Case not found"**
- Solution: Create a new case from Dashboard or any module

### **"Model not loaded"**
- Solution: Check backend is running and models are in `ml/registry/`

### **File upload fails**
- Solution: Check file size (< 10MB) and format (JPG/PNG for X-ray, PDF for docs)

---

## 📱 Mobile Usage

All modules are mobile-responsive:
- Vertical layouts on narrow screens
- Touch-friendly buttons and controls
- Swipe gestures for navigation
- Optimized for tablets and phones

---

## 🆘 Need Help?

- **Technical Issues**: Check browser console (F12)
- **API Errors**: Check backend logs
- **Module Documentation**: See `UI_MODULES.md`
- **Project Context**: See `.agents/AGENTS.md`

---

**Happy Analyzing! 🏥**
