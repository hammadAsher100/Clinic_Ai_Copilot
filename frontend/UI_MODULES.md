# Clinical AI Co-Pilot — Modular UI Architecture

## Overview

The frontend has been redesigned with a **modular architecture**, separating each functionality into dedicated pages for better user experience, maintainability, and scalability.

---

## 🎯 Module Structure

### **1. Dashboard** (`dashboard.html`)
**Purpose**: Central hub and overview page

**Features**:
- Quick statistics (total cases, pending review, completed, reports generated)
- Analysis module cards with descriptions and launch buttons
- Recent activity feed
- Quick case creation
- Navigation to all other modules

**Entry Point**: Root URL (`/`) redirects here after login

---

### **2. X-Ray Analysis** (`xray.html`)
**Purpose**: Dedicated chest X-ray pneumonia detection module

**Features**:
- Drag-and-drop file upload with multi-file support
- Image preview grid
- Real-time analysis with Grad-CAM heatmap generation
- Case association (existing or new)
- Model information panel
- Results visualization with confidence gauges
- Navigation to other analysis modules

**Model**: CNN (MobileNetV2) for binary classification (NORMAL/PNEUMONIA)

---

### **3. Heart Risk Assessment** (`heart.html`)
**Purpose**: Dedicated cardiovascular risk prediction module

**Features**:
- 13 clinical feature input form (age, sex, chest pain, BP, cholesterol, etc.)
- Pre-filled default values for quick testing
- SHAP explainability charts
- Confidence visualization
- Case association
- Model architecture information

**Model**: ANN with SHAP feature importance analysis

---

### **4. Symptom Classifier** (`symptoms.html`)
**Purpose**: Dedicated natural language symptom analysis module

**Features**:
- Large text area for symptom description
- Top-3 condition predictions
- Confidence scores for each prediction
- 24 disease category classification
- Sample condition badges
- Case association

**Model**: BiLSTM for text classification across 24 conditions

---

### **5. Document Upload** (`documents.html`)
**Purpose**: Medical document processing and text extraction

**Features**:
- Multi-file PDF upload
- Text extraction and field parsing
- Raw text preview with collapsible sections
- Support for clinical notes, discharge summaries, lab reports
- Case association
- Extraction results display

**Technology**: PDF parsing with pdfplumber

---

### **6. Case Management** (`cases.html`)
**Purpose**: Centralized case tracking and management

**Features**:
- Case statistics dashboard
- Sortable case table with status indicators
- Quick case creation
- Direct navigation to review dashboard
- Add analysis to existing cases
- Status badges (pending, in_review, completed)

**Functionality**: CRUD operations for clinical cases

---

### **7. Review Dashboard** (`review.html`)
**Purpose**: Human-in-the-loop (HITL) review workflow

**Features**:
- Case selector dropdown
- Multi-modal prediction cards with explainability
- Approve/Reject/Edit actions for each modality
- LLM-generated clinical narrative
- Confidence gauges and SHAP/Grad-CAM visualizations
- Report generation trigger

**Workflow**: Clinician review and validation of AI predictions

---

### **8. Reports** (`report.html`)
**Purpose**: Generated report management and download

**Features**:
- Case-based report lookup
- Download PDF reports
- Report regeneration
- Complete case listing with status
- Timestamp tracking

**Output**: PDF clinical reports with all findings

---

### **9. Login** (`index.html`)
**Purpose**: Authentication gateway

**Features**:
- JWT-based authentication
- Demo credentials display
- Model badges showcase
- Auto-redirect if already authenticated

**Demo Credentials**:
- Username: `clinician`
- Password: `demo2026`

---

### **10. Upload (Legacy)** (`upload.html`)
**Purpose**: Original all-in-one upload page (kept for backward compatibility)

**Status**: Marked as legacy; new users should use modular pages

**Note**: This page combines all upload functionalities but is less focused than the modular approach

---

## 🎨 Design System

### **Color Palette**
- **Primary**: Teal (`#00d4aa`) - Success, Normal results
- **Secondary**: Blue (`#4e8cff`) - X-Ray module, Information
- **Warning**: Amber (`#ffb347`) - Documents, Moderate risk
- **Danger**: Coral (`#ff6b6b`) - High risk, Pneumonia
- **Accent**: Purple (`#a78bfa`) - Symptoms module

### **Component Library**
- **Cards**: Glassmorphism style with blur effects
- **Buttons**: Primary (gradient), Secondary (outlined), Danger, Success
- **Badges**: Status indicators with color coding
- **Progress Bars**: Confidence visualization
- **Gauges**: Semicircle confidence meters
- **Charts**: Vanilla JS Canvas-based (SHAP, Top-3 conditions)

### **Typography**
- **Font**: Inter (Google Fonts)
- **Headings**: 700 weight
- **Body**: 400 weight
- **Monospace**: For code/data display

---

## 🔄 Navigation Flow

```
Login (index.html)
    ↓
Dashboard (dashboard.html)
    ├─→ X-Ray Analysis (xray.html)
    ├─→ Heart Assessment (heart.html)
    ├─→ Symptom Classifier (symptoms.html)
    ├─→ Document Upload (documents.html)
    ├─→ Case Management (cases.html)
    ├─→ Review Dashboard (review.html)
    └─→ Reports (report.html)
```

### **Cross-Module Navigation**
- Each analysis module can create OR link to existing cases
- After completing an analysis, users can:
  - Continue to another analysis module
  - Go directly to review
  - Return to dashboard
- Case ID is passed via URL parameters (`?case_id=123`)

---

## 📱 Responsive Design

All modules are fully responsive with:
- **Desktop**: Multi-column grid layouts
- **Tablet**: 2-column grids, collapsible sections
- **Mobile**: Single-column stacked layout

Media query breakpoint: `768px`

---

## 🔐 Authentication

All pages (except `index.html`) include auth guards:
```javascript
if (!isAuthenticated()) window.location.href = '/static/frontend/index.html';
```

Token management handled in `api.js`:
- `getToken()` - Retrieve JWT from localStorage
- `setToken(token)` - Store JWT
- `clearToken()` - Logout
- `isAuthenticated()` - Check auth status

---

## 🛠️ API Integration

All modules use centralized API client (`api.js`):

**Key Functions**:
- `createCase(name, age, sex)` - Create new case
- `listCases()` - Get all cases
- `predictImage(file, caseId)` - X-ray analysis
- `predictTabular(features)` - Heart risk assessment
- `predictText(symptoms, caseId)` - Symptom classification
- `uploadPDF(file, caseId)` - Document extraction
- `getCaseReview(caseId)` - HITL review data
- `submitDecision(caseId, modality, action)` - Submit review
- `generateReport(caseId)` - Generate PDF report

---

## 📊 Chart Utilities

Vanilla JavaScript charts (`charts.js`):

- `renderSHAPChart(containerId, shapValues)` - Feature importance bars
- `renderConfidenceGauge(containerId, confidence, label)` - Semicircle gauge
- `renderTop3Conditions(containerId, top3)` - Ranked condition list

**No external chart libraries** - all Canvas-based for lightweight performance

---

## 🎯 User Workflow Examples

### **Workflow 1: Complete Case Analysis**
1. Login → Dashboard
2. Create new case
3. Upload chest X-ray → X-Ray Analysis
4. Continue to Heart Assessment
5. Continue to Symptom Classifier
6. Review Dashboard → Approve/Edit predictions
7. Generate Report
8. Download PDF from Reports page

### **Workflow 2: Single-Modality Quick Analysis**
1. Login → Dashboard
2. Click "Chest X-Ray Analysis"
3. Upload image (auto-creates case)
4. View results with Grad-CAM
5. Proceed to Review for validation

### **Workflow 3: Case Management**
1. Login → Cases
2. View all cases with status
3. Select case → Add Analysis
4. Choose module (X-Ray/Heart/Symptoms)
5. Complete analysis
6. Return to Case Management

---

## 🚀 Benefits of Modular Architecture

### **User Experience**
- ✅ Clear, focused interfaces per functionality
- ✅ Reduced cognitive load
- ✅ Faster task completion
- ✅ Better mobile experience

### **Development**
- ✅ Easier to maintain and debug
- ✅ Modular testing
- ✅ Parallel development possible
- ✅ Clear separation of concerns

### **Scalability**
- ✅ Easy to add new modules
- ✅ Independent module updates
- ✅ Reusable components across modules

---

## 📝 File Structure

```
frontend/
├── index.html              # Login page
├── dashboard.html          # Central hub (NEW)
├── xray.html              # X-Ray analysis module (NEW)
├── heart.html             # Heart risk module (NEW)
├── symptoms.html          # Symptom classifier module (NEW)
├── documents.html         # Document upload module (NEW)
├── cases.html             # Case management (NEW)
├── review.html            # HITL review dashboard (UPDATED)
├── report.html            # Report management (UPDATED)
├── upload.html            # Legacy all-in-one page (DEPRECATED)
├── css/
│   └── styles.css         # Global design system
└── js/
    ├── api.js             # API client & utilities
    └── charts.js          # Chart rendering functions
```

---

## 🎓 Next Steps for Enhancement

### **Potential Additions**
1. **User Profile Module** - User settings and preferences
2. **Analytics Dashboard** - Usage statistics and model performance
3. **Notification Center** - Real-time alerts and updates
4. **Patient History** - Complete patient record view
5. **Batch Processing** - Multiple file/case processing
6. **Export Module** - Data export in various formats

### **Technical Improvements**
1. Add loading skeletons for better perceived performance
2. Implement offline mode with service workers
3. Add print-friendly report views
4. Enhance accessibility (ARIA labels, keyboard navigation)
5. Add dark/light theme toggle

---

## 📞 Support

For issues or questions regarding the modular UI:
- Check the AGENTS.md file for project context
- Review API documentation in README.md
- Examine component structure in styles.css

**Version**: 2.0 (Modular Architecture)  
**Last Updated**: 2026-07-12
