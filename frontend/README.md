# Clinical AI Co-Pilot — Frontend Documentation

**Version**: 2.0 (Modular Architecture)  
**Last Updated**: 2026-07-12

---

## 📚 Documentation Index

### **Quick Access**
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- 🗺️ **[Site Navigation Map](SITEMAP.md)** - Visual navigation structure
- 📊 **[Before & After](BEFORE_AFTER.md)** - See the transformation
- ✅ **[Testing Checklist](TESTING_CHECKLIST.md)** - Comprehensive QA guide

### **Detailed Documentation**
- 📖 **[UI Modules Guide](UI_MODULES.md)** - Complete architecture documentation
- 📝 **[Enhancement Summary](../ENHANCEMENT_SUMMARY.md)** - What changed and why

---

## 🎯 What's New in v2.0

### **Modular Architecture**
The frontend has been completely redesigned with **8 focused modules** instead of one monolithic upload page:

1. **Dashboard** - Central hub with stats and navigation
2. **X-Ray Analysis** - Dedicated chest X-ray module
3. **Heart Assessment** - Dedicated cardiovascular risk module
4. **Symptom Classifier** - Dedicated symptom analysis module
5. **Document Upload** - Dedicated PDF extraction module
6. **Case Management** - Centralized case tracking
7. **Review Dashboard** - Enhanced HITL workflow
8. **Reports** - Enhanced report management

---

## 🗂️ File Structure

```
frontend/
├── README.md                    # This file
├── index.html                   # Login page
├── dashboard.html               # Central hub ⭐ NEW
├── xray.html                    # X-Ray module ⭐ NEW
├── heart.html                   # Heart module ⭐ NEW
├── symptoms.html                # Symptoms module ⭐ NEW
├── documents.html               # Documents module ⭐ NEW
├── cases.html                   # Case management ⭐ NEW
├── review.html                  # HITL review (enhanced)
├── report.html                  # Reports (enhanced)
├── upload.html                  # Legacy all-in-one (deprecated)
│
├── css/
│   └── styles.css               # Global design system
│
├── js/
│   ├── api.js                   # API client & utilities
│   └── charts.js                # Chart rendering functions
│
└── [Documentation Files]
    ├── QUICK_START.md           # Quick reference guide
    ├── UI_MODULES.md            # Module architecture docs
    ├── SITEMAP.md               # Navigation map
    ├── BEFORE_AFTER.md          # Comparison guide
    └── TESTING_CHECKLIST.md     # QA checklist
```

---

## 🚀 Getting Started

### **1. Start the Backend**
```bash
# From project root
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **2. Open Your Browser**
```
http://localhost:8000
```

### **3. Login**
- **Username**: `clinician`
- **Password**: `demo2026`

### **4. Explore**
- You'll land on the **Dashboard**
- Click any module card to begin
- Create a case and try each analysis module

---

## 🎨 Design System

### **Color Palette**
- **Teal** (`#00d4aa`) - Primary, Success, Normal results
- **Blue** (`#4e8cff`) - Secondary, X-Ray module
- **Coral** (`#ff6b6b`) - Danger, High risk, Positive findings
- **Amber** (`#ffb347`) - Warning, Documents module
- **Purple** (`#a78bfa`) - Symptoms module

### **Typography**
- **Font**: Inter (Google Fonts)
- **Weights**: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (extrabold)

### **Components**
- **Cards**: Glassmorphism with backdrop blur
- **Buttons**: Gradient primary, outlined secondary
- **Badges**: Status indicators with color coding
- **Charts**: Vanilla JavaScript Canvas (no libraries)

---

## 🔄 Module Overview

### **Dashboard** (`dashboard.html`)
**Central control hub**
- Real-time statistics
- Module navigation cards
- Recent activity feed
- Quick case creation

### **X-Ray Analysis** (`xray.html`)
**Pneumonia detection**
- Multi-file upload with preview
- CNN (MobileNetV2) inference
- Grad-CAM explainability
- Confidence visualization

### **Heart Assessment** (`heart.html`)
**Cardiovascular risk prediction**
- 13 clinical feature inputs
- ANN inference
- SHAP feature importance
- Risk stratification

### **Symptom Classifier** (`symptoms.html`)
**Natural language analysis**
- Free-text symptom description
- BiLSTM inference
- 24 condition classification
- Top-3 differential diagnosis

### **Document Upload** (`documents.html`)
**PDF text extraction**
- Multi-file PDF upload
- Text parsing with pdfplumber
- Structured field extraction
- Raw text preview

### **Case Management** (`cases.html`)
**Case tracking & organization**
- Complete case listing
- Status-based filtering
- Quick navigation to review
- Case statistics dashboard

### **Review Dashboard** (`review.html`)
**Human-in-the-loop workflow**
- Multi-modal prediction review
- Approve/Reject/Edit actions
- Explainability visualizations
- LLM narrative generation

### **Reports** (`report.html`)
**PDF report management**
- Report status checking
- PDF download links
- Report regeneration
- Complete case listing

---

## 🛠️ Technology Stack

### **Frontend**
- HTML5 (semantic markup)
- CSS3 (custom design system, no framework)
- Vanilla JavaScript (no React/Vue/Angular)
- Canvas API (for charts)

### **API Integration**
- Fetch API for HTTP requests
- JWT authentication
- LocalStorage for token management

### **Charts & Visualizations**
- Custom Canvas-based rendering
- SHAP bar charts
- Confidence gauges (semicircle)
- Top-N ranking lists

---

## 📱 Responsive Design

All modules are fully responsive:

- **Desktop** (> 768px): Multi-column grid layouts
- **Tablet** (768px): 2-column layouts
- **Mobile** (< 768px): Single-column stacked layouts

Touch-friendly controls and optimized for mobile workflows.

---

## 🔐 Authentication

### **JWT-Based Auth**
- Token stored in localStorage
- Included in all API requests
- Auto-redirect on expiration

### **Auth Guard**
All pages (except login) check authentication:
```javascript
if (!isAuthenticated()) window.location.href = '/static/frontend/index.html';
```

---

## 🧪 Testing

### **Manual Testing**
Use the [Testing Checklist](TESTING_CHECKLIST.md) for comprehensive QA.

### **Browser Compatibility**
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (Desktop & iOS)
- ✅ Mobile browsers

### **Recommended Test Flow**
1. Login → Dashboard
2. Create new case
3. X-Ray Analysis → Upload & analyze
4. Heart Assessment → Enter data & analyze
5. Symptom Classifier → Enter symptoms & classify
6. Review Dashboard → Approve predictions
7. Generate Report → Download PDF

---

## 📖 API Integration

### **Core Functions** (`js/api.js`)

**Authentication**:
- `login(username, password)` - User authentication
- `getCurrentUser()` - Get current user info
- `logout()` - Clear session and redirect

**Case Management**:
- `createCase(name, age, sex)` - Create new case
- `listCases()` - Get all cases

**Predictions**:
- `predictImage(file, caseId)` - X-ray analysis
- `predictTabular(features)` - Heart risk assessment
- `predictText(symptoms, caseId)` - Symptom classification
- `uploadPDF(file, caseId)` - Document extraction

**Workflow**:
- `getCaseReview(caseId)` - Get review dashboard data
- `submitDecision(caseId, modality, action, editedValue)` - Submit HITL decision
- `summarizeCase(caseId)` - Generate LLM narrative
- `generateReport(caseId)` - Create PDF report
- `getReportStatus(caseId)` - Check report availability

### **Utilities** (`js/api.js`)
- `showToast(message, type)` - Toast notifications
- `showLoading(message)` - Loading overlay
- `hideLoading()` - Hide loading overlay

### **Charts** (`js/charts.js`)
- `renderSHAPChart(containerId, shapValues)` - SHAP bar chart
- `renderConfidenceGauge(containerId, confidence, label)` - Confidence gauge
- `renderTop3Conditions(containerId, top3)` - Ranked conditions

---

## 🔧 Development

### **Adding a New Module**

1. **Create HTML page** (e.g., `newmodule.html`)
2. **Use template structure**:
   ```html
   - Navigation bar with links
   - Case selection dropdown
   - Module-specific content
   - Results section
   - API integration script
   ```
3. **Add to dashboard** (`dashboard.html`):
   ```html
   <div class="card" onclick="location.href='/static/frontend/newmodule.html'">
     <h3>New Module</h3>
     <p>Description...</p>
     <button>Launch →</button>
   </div>
   ```
4. **Update navigation** in all pages
5. **Test thoroughly** using checklist

### **Modifying Design System**

Edit CSS variables in `css/styles.css`:
```css
:root {
  --bg-deep: #060a1a;
  --accent-teal: #00d4aa;
  /* ... more variables */
}
```

---

## 🐛 Troubleshooting

### **Module not loading**
- Check browser console for errors
- Verify backend is running
- Check network tab for failed requests

### **Authentication fails**
- Verify backend is accessible
- Check credentials (clinician/demo2026)
- Clear localStorage and retry

### **Charts not rendering**
- Verify `charts.js` is loaded
- Check container element exists
- Verify data format matches expected structure

### **Case ID not persisting**
- Check URL parameters
- Verify case creation succeeded
- Check console for errors

---

## 📞 Support

### **Issues**
- Check browser console (F12)
- Review backend logs
- Consult documentation files

### **Documentation**
- [Quick Start](QUICK_START.md) - Getting started
- [UI Modules](UI_MODULES.md) - Detailed module docs
- [Sitemap](SITEMAP.md) - Navigation structure
- [Testing](TESTING_CHECKLIST.md) - QA guide

---

## 📝 Version History

### **v2.0 (2026-07-12)** - Modular Architecture
- ✅ 6 new dedicated analysis modules
- ✅ Central dashboard with statistics
- ✅ Enhanced case management
- ✅ Improved mobile experience
- ✅ Comprehensive documentation

### **v1.0** - Initial Release
- Single upload page
- Basic review workflow
- Report generation

---

## 🎉 Credits

**Design & Development**: Clinical AI Co-Pilot Team  
**UI Architecture**: Modular SPA pattern  
**Design System**: Dark-mode glassmorphism  
**Charts**: Custom Canvas implementations

---

## 📜 License

This frontend is part of the Clinical AI Co-Pilot project.  
See repository LICENSE file for details.

---

**Ready to explore? Start with the [Quick Start Guide](QUICK_START.md)!** 🚀
