# 🎨 Clinical AI Co-Pilot - UI Structure Guide

## **Complete UI Architecture & User Flow**

---

## 📊 **UI Overview**

Your Clinical AI Co-Pilot now has a **modular architecture** with **8 focused pages**:

```
┌─────────────────────────────────────────┐
│         1. LOGIN (index.html)           │
│              ↓                          │
│    ┌─────────────────────────┐         │
│    │  2. DASHBOARD (hub)     │         │
│    └─────────────────────────┘         │
│              ↓                          │
│    ┌─────────┬─────────┬──────────┐   │
│    ↓         ↓         ↓          ↓    │
│  3. X-Ray  4. Heart  5. Symp  6. Docs  │
│              ↓                          │
│         7. Review                       │
│              ↓                          │
│         8. Reports                      │
└─────────────────────────────────────────┘
```

---

## 🗺️ **Complete Page Structure**

### **1. Login Page** (`frontend/index.html`)

#### **Purpose**
- User authentication gateway
- Entry point to the application

#### **URL**
```
http://localhost:8000/
OR
http://localhost:8000/static/frontend/index.html
```

#### **Features**
- JWT-based authentication
- Clean, centered login form
- Demo credentials displayed
- Model badges showcase
- Auto-redirect if already logged in

#### **Layout**
```
┌──────────────────────────────────────┐
│          🏥 Logo (Large)             │
│      Clinical AI Co-Pilot            │
│   Multi-modal clinical decision      │
│         support system               │
│                                      │
│   ┌─────────────────────────────┐   │
│   │ Username: [____________]    │   │
│   │ Password: [____________]    │   │
│   │ [ Sign In Button ]          │   │
│   └─────────────────────────────┘   │
│                                      │
│   Demo: clinician / demo2026        │
│                                      │
│   [CNN] [ANN] [BiLSTM] [LLM]       │
└──────────────────────────────────────┘
```

#### **User Actions**
1. Enter username and password
2. Click "Sign In"
3. On success → Redirect to Dashboard
4. On error → Show error message

#### **Demo Credentials**
```
Username: clinician
Password: demo2026
```

---

### **2. Dashboard** (`frontend/dashboard.html`)

#### **Purpose**
- Central navigation hub
- Overview of system statistics
- Quick access to all modules

#### **URL**
```
http://localhost:8000/static/frontend/dashboard.html
```

#### **Layout**
```
┌──────────────────────────────────────────────────┐
│  🏥 Clinical AI   [Dashboard][Cases][Review]    │
│                                      [User] 🟢   │
├──────────────────────────────────────────────────┤
│  Clinical AI Co-Pilot Dashboard                 │
│  Multi-modal AI-powered clinical decision       │
│                                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐│
│  │ Total   │ │Pending  │ │In Review│ │Complete││
│  │   47    │ │   12    │ │    8    │ │   27  ││
│  └─────────┘ └─────────┘ └─────────┘ └───────┘│
│                                                  │
│  Analysis Modules                                │
│  ┌──────────────────┐ ┌──────────────────┐    │
│  │ 🫁 Chest X-Ray  │ │ ❤️  Heart Risk   │    │
│  │ Pneumonia Det.  │ │ Assessment       │    │
│  │ [Launch →]      │ │ [Launch →]       │    │
│  └──────────────────┘ └──────────────────┘    │
│                                                  │
│  ┌──────────────────┐ ┌──────────────────┐    │
│  │ 💬 Symptoms     │ │ 📄 Documents     │    │
│  │ Classifier      │ │ Upload           │    │
│  │ [Launch →]      │ │ [Launch →]       │    │
│  └──────────────────┘ └──────────────────┘    │
│                                                  │
│  Recent Activity                                 │
│  • Case #47 - pending          [View]          │
│  • Case #46 - completed        [View]          │
│                                                  │
│  [➕ Create New Case]                           │
└──────────────────────────────────────────────────┘
```

#### **Components**

**A. Navigation Bar**
- Logo + App name (left)
- Menu links: Dashboard, Cases, Review, Reports
- User badge with username (right)
- Logout link

**B. Statistics Cards** (4 cards)
- **Total Cases**: Count of all cases
- **Pending**: Cases awaiting review
- **In Review**: Cases being reviewed
- **Completed**: Finalized cases

**C. Module Cards** (4 cards)
- **X-Ray Analysis**: 🫁 Blue
- **Heart Assessment**: ❤️ Coral
- **Symptom Classifier**: 💬 Purple
- **Document Upload**: 📄 Amber

**D. Recent Activity**
- Last 5 cases created
- Status and quick view link

**E. Quick Actions**
- "Create New Case" button

#### **User Actions**
1. **View Stats**: See system overview
2. **Click Module**: Navigate to analysis page
3. **Create Case**: Start new patient case
4. **View Recent**: Check recent activity
5. **Navigate**: Use top menu

---

### **3. X-Ray Analysis** (`frontend/xray.html`)

#### **Purpose**
- Upload and analyze chest X-ray images
- Pneumonia detection with explainability

#### **URL**
```
http://localhost:8000/static/frontend/xray.html
http://localhost:8000/static/frontend/xray.html?case_id=123
```

#### **Layout**
```
┌────────────────────────────────────────────┐
│  ← Back    🫁 Chest X-Ray Analysis         │
│            [CNN · Pneumonia Detection]     │
├────────────────────────────────────────────┤
│  Case: [Select #47 ▼]  Patient: [____]    │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │  Upload X-Ray Image                │   │
│  │  📷 Drop files here or click       │   │
│  │     Multiple files supported       │   │
│  └────────────────────────────────────┘   │
│  [Preview Grid]                            │
│  [🔬 Analyze X-Ray Button]                │
│                                            │
│  Results:                                  │
│  ┌────────────────────────────────────┐   │
│  │ PNEUMONIA  ⚠️    Confidence: 87%   │   │
│  │ [Confidence Gauge]                  │   │
│  │ [Grad-CAM Heatmap Image]           │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Continue to Heart →] [Review →]         │
└────────────────────────────────────────────┘
```

#### **Features**
- **Drag-and-drop**: Upload multiple X-ray images
- **Image Preview**: See thumbnails before analysis
- **Case Linking**: Associate with existing or new case
- **CNN Inference**: MobileNetV2 model
- **Grad-CAM**: Visual explanation heatmap
- **Confidence**: Prediction certainty score
- **Navigation**: Continue to other modules

#### **Workflow**
1. Select or create case
2. Upload X-ray image(s)
3. Preview images
4. Click "Analyze"
5. View results:
   - Classification (NORMAL/PNEUMONIA)
   - Confidence score
   - Grad-CAM heatmap
6. Continue to next module or review

---

### **4. Heart Assessment** (`frontend/heart.html`)

#### **Purpose**
- Cardiovascular risk prediction
- 13 clinical feature analysis

#### **URL**
```
http://localhost:8000/static/frontend/heart.html
http://localhost:8000/static/frontend/heart.html?case_id=123
```

#### **Layout**
```
┌────────────────────────────────────────────┐
│  ← Back    ❤️  Heart Disease Risk         │
│            [ANN · 13 Clinical Features]    │
├────────────────────────────────────────────┤
│  Case: [Select #47 ▼]                     │
│                                            │
│  Clinical Features:                         │
│  ┌──────────┐ ┌──────────┐               │
│  │Age: [55] │ │Sex: [1]  │               │
│  └──────────┘ └──────────┘               │
│  ┌──────────┐ ┌──────────┐               │
│  │CP: [2]   │ │BP: [130] │               │
│  └──────────┘ └──────────┘               │
│  ... (9 more fields)                       │
│                                            │
│  [❤️  Assess Risk Button]                 │
│                                            │
│  Results:                                  │
│  ┌────────────────────────────────────┐   │
│  │ HIGH_RISK  ⚠️   Confidence: 82%    │   │
│  │ [Confidence Gauge]                  │   │
│  │ [SHAP Feature Importance Chart]    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Continue to Symptoms →] [Review →]      │
└────────────────────────────────────────────┘
```

#### **Features**
- **13 Input Fields**: Age, Sex, Chest Pain, BP, Cholesterol, etc.
- **Pre-filled Defaults**: For quick testing
- **ANN Inference**: Neural network risk assessment
- **SHAP Analysis**: Feature importance visualization
- **Risk Stratification**: HIGH_RISK or LOW_RISK
- **Confidence Score**: Prediction certainty

#### **Input Fields**
```
1. Age (years)
2. Sex (0=Female, 1=Male)
3. Chest Pain Type (0-3)
4. Resting Blood Pressure (mmHg)
5. Cholesterol (mg/dl)
6. Fasting Blood Sugar >120 (0=No, 1=Yes)
7. Resting ECG (0-2)
8. Max Heart Rate
9. Exercise Induced Angina (0=No, 1=Yes)
10. ST Depression
11. Slope (0-2)
12. Number of Major Vessels (0-3)
13. Thal (1-3)
```

---

### **5. Symptom Classifier** (`frontend/symptoms.html`)

#### **Purpose**
- Natural language symptom analysis
- 24 condition classification

#### **URL**
```
http://localhost:8000/static/frontend/symptoms.html
http://localhost:8000/static/frontend/symptoms.html?case_id=123
```

#### **Layout**
```
┌────────────────────────────────────────────┐
│  ← Back    💬 Symptom Classifier           │
│            [BiLSTM · 24 Conditions]        │
├────────────────────────────────────────────┤
│  Case: [Select #47 ▼]                     │
│                                            │
│  Symptom Description:                       │
│  ┌────────────────────────────────────┐   │
│  │ Describe symptoms in natural      │   │
│  │ language...                        │   │
│  │                                    │   │
│  │ e.g., "Patient reports severe     │   │
│  │ headache, blurred vision..."      │   │
│  │                                    │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [💬 Classify Symptoms Button]            │
│                                            │
│  Results:                                  │
│  ┌────────────────────────────────────┐   │
│  │ Migraine  🎯   Confidence: 89%     │   │
│  │ [Confidence Gauge]                  │   │
│  │                                     │   │
│  │ Top 3 Conditions:                  │   │
│  │ 1. Migraine (89%)                  │   │
│  │ 2. Tension Headache (6%)           │   │
│  │ 3. Cluster Headache (3%)           │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Continue to Documents →] [Review →]     │
└────────────────────────────────────────────┘
```

#### **Features**
- **Free Text Input**: Natural language description
- **BiLSTM Model**: Deep learning text classification
- **24 Conditions**: Comprehensive disease coverage
- **Top-3 Predictions**: Differential diagnosis
- **Confidence Scores**: For each prediction

#### **Sample Conditions**
- Migraine, Diabetes, Hypertension
- Asthma, Pneumonia, Bronchitis
- Gastroenteritis, UTI, Arthritis
- Depression, Anxiety, etc. (24 total)

---

### **6. Document Upload** (`frontend/documents.html`)

#### **Purpose**
- Medical document processing
- PDF text extraction

#### **URL**
```
http://localhost:8000/static/frontend/documents.html
http://localhost:8000/static/frontend/documents.html?case_id=123
```

#### **Layout**
```
┌────────────────────────────────────────────┐
│  ← Back    📄 Medical Document Upload      │
│            [PDF Parser · Text Extraction]  │
├────────────────────────────────────────────┤
│  Case: [Select #47 ▼]                     │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │  📁 Drop PDF documents here        │   │
│  │     Clinical notes, discharge      │   │
│  │     summaries, lab reports         │   │
│  └────────────────────────────────────┘   │
│  Selected: sample_report.pdf               │
│                                            │
│  [📄 Extract & Process Button]            │
│                                            │
│  Results:                                  │
│  ┌────────────────────────────────────┐   │
│  │ ✓ 3 pages extracted                │   │
│  │                                     │   │
│  │ ▼ View Raw Text                    │   │
│  │   Patient Name: John Doe...        │   │
│  │   Diagnosis: ...                   │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

#### **Features**
- **Multi-file Upload**: Process multiple PDFs
- **Text Extraction**: Using pdfplumber
- **Structured Fields**: Extract key information
- **Raw Text Preview**: Collapsible section
- **Page Count**: Number of pages processed

---

### **7. Review Dashboard (HITL)** (`frontend/review.html`)

#### **Purpose**
- Human-in-the-loop review workflow
- Approve/reject/edit AI predictions

#### **URL**
```
http://localhost:8000/static/frontend/review.html
http://localhost:8000/static/frontend/review.html?case_id=123
```

#### **Layout**
```
┌──────────────────────────────────────────────────┐
│  HITL Review Dashboard                           │
│  Case: [Select #47 ▼]                          │
├──────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │
│  │ 🫁 X-Ray     │ │ ❤️  Heart    │ │💬 Sympt │ │
│  │ PNEUMONIA    │ │ HIGH_RISK    │ │Migraine │ │
│  │ [87% conf]   │ │ [82% conf]   │ │[89% co] │ │
│  │ [Gauge]      │ │ [Gauge]      │ │[Gauge]  │ │
│  │ [Grad-CAM]   │ │ [SHAP Chart] │ │[Top-3]  │ │
│  │              │ │              │ │         │ │
│  │ [✓Approve]   │ │ [✓Approve]   │ │[✓Appro]│ │
│  │ [✗Reject]    │ │ [✗Reject]    │ │[✗Rejec]│ │
│  │ [✎Edit]      │ │ [✎Edit]      │ │[✎Edit] │ │
│  └──────────────┘ └──────────────┘ └─────────┘ │
│                                                  │
│  🤖 AI-Generated Clinical Narrative              │
│  ┌────────────────────────────────────────────┐ │
│  │ Patient presents with chest X-ray showing  │ │
│  │ findings consistent with pneumonia...      │ │
│  │ Heart disease risk assessment indicates... │ │
│  │ Symptom analysis suggests...               │ │
│  └────────────────────────────────────────────┘ │
│  [🔄 Regenerate Narrative]                      │
│                                                  │
│  [📄 Generate Report Button]                    │
└──────────────────────────────────────────────────┘
```

#### **Features**
- **Multi-Modal Cards**: One card per analysis type
- **Explainability**: Grad-CAM, SHAP, Top-3
- **Confidence Gauges**: Visual certainty indicators
- **HITL Actions**: Approve, Reject, Edit buttons
- **LLM Narrative**: AI-generated clinical summary
- **Report Generation**: Create final PDF

#### **Workflow**
1. Select case to review
2. View all predictions with explainability
3. For each modality:
   - Approve if correct
   - Reject if incorrect
   - Edit to modify value
4. Review/edit AI narrative
5. Generate final report

---

### **8. Reports** (`frontend/report.html`)

#### **Purpose**
- View and download generated reports
- Track report status

#### **URL**
```
http://localhost:8000/static/frontend/report.html
http://localhost:8000/static/frontend/report.html?case_id=123
```

#### **Layout**
```
┌────────────────────────────────────────────┐
│  Reports                                    │
│  Case: [Select #47 ▼]                     │
├────────────────────────────────────────────┤
│  ┌────────────────────────────────────┐   │
│  │  ✅ Report Ready                   │   │
│  │                                     │   │
│  │  Generated: 2026-07-12 10:30 AM   │   │
│  │                                     │   │
│  │  [⬇️  Download PDF Report]         │   │
│  │  [🔄 Regenerate Report]            │   │
│  └────────────────────────────────────┘   │
│                                            │
│  All Cases:                                 │
│  ┌────────────────────────────────────┐   │
│  │ ID  Status    Created    [Actions] │   │
│  │ #47 complete  12/07/26   [Review]  │   │
│  │ #46 complete  11/07/26   [Review]  │   │
│  │ #45 pending   10/07/26   [Review]  │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

#### **Features**
- **Report Status**: Check if report exists
- **Download Link**: Get PDF report
- **Regenerate**: Create new version
- **Cases Table**: View all cases
- **Quick Navigation**: Jump to review

---

## 🎨 **Design System**

### **Color Palette**

```css
/* Primary Colors */
--accent-teal:    #00d4aa  /* Success, Normal, Primary */
--accent-blue:    #4e8cff  /* Info, X-Ray */
--accent-coral:   #ff6b6b  /* Danger, High Risk */
--accent-amber:   #ffb347  /* Warning, Documents */
--accent-purple:  #a78bfa  /* Symptoms */

/* Backgrounds */
--bg-deep:        #060a1a  /* Page background */
--bg-primary:     #0a0e27  /* Content background */
--bg-surface:     #111633  /* Card background */
--bg-elevated:    #1a2040  /* Elevated elements */
```

### **Typography**

```css
/* Font */
font-family: 'Inter', sans-serif

/* Weights */
300 - Light
400 - Regular
500 - Medium
600 - Semi-bold
700 - Bold
800 - Extra-bold
```

### **Component Patterns**

#### **Cards**
```css
.card {
  background: glassmorphism effect
  border-radius: 12px
  padding: 24px
  border: 1px solid rgba(255,255,255,0.08)
  backdrop-filter: blur(16px)
}
```

#### **Buttons**
```css
.btn-primary {
  background: linear-gradient(135deg, teal, green)
  color: white
  border-radius: 8px
  padding: 10px 20px
}

.btn-secondary {
  background: elevated
  border: 1px solid subtle
  color: primary text
}
```

#### **Badges**
```css
.badge {
  display: inline-flex
  padding: 4px 10px
  border-radius: 24px
  font-size: 0.75rem
  font-weight: 600
  text-transform: uppercase
}

.badge-teal   { background: rgba(0, 212, 170, 0.15) }
.badge-coral  { background: rgba(255, 107, 107, 0.15) }
```

---

## 🔄 **User Flow Examples**

### **Flow 1: Complete New Case**

```
1. Login (index.html)
   ↓
2. Dashboard (dashboard.html)
   → Click "Create New Case"
   ↓
3. X-Ray Analysis (xray.html)
   → Upload image
   → Analyze
   ↓
4. Heart Assessment (heart.html)
   → Enter vitals
   → Assess Risk
   ↓
5. Symptom Classifier (symptoms.html)
   → Enter symptoms
   → Classify
   ↓
6. Review Dashboard (review.html)
   → Approve/Edit predictions
   → Generate Report
   ↓
7. Reports (report.html)
   → Download PDF
```

### **Flow 2: Quick Single Analysis**

```
1. Login
   ↓
2. Dashboard
   → Click "Chest X-Ray Analysis"
   ↓
3. X-Ray Analysis
   → Upload image
   → View results
   → [Done]
```

### **Flow 3: Case Management**

```
1. Dashboard
   → Click "Cases"
   ↓
2. Case Management (cases.html)
   → View all cases
   → Select case #47
   ↓
3. Review Dashboard
   → Review predictions
   → Generate report
```

---

## 📱 **Responsive Behavior**

### **Desktop (>768px)**
- Multi-column grid layouts (2-4 columns)
- Horizontal navigation bar
- Side-by-side content
- Large preview images

### **Tablet (768px)**
- 2-column layouts
- Responsive navigation
- Stacked module cards
- Medium-sized controls

### **Mobile (<768px)**
- Single-column layouts
- Hamburger menu (if implemented)
- Vertical stacking
- Touch-optimized buttons (44px min)
- Mobile-friendly file uploads

---

## 🎯 **Key UI Features**

### **Navigation**
- ✅ Persistent top nav bar
- ✅ Active page highlighting
- ✅ User badge with status dot
- ✅ Logout functionality

### **Case Management**
- ✅ Case ID in URL parameters
- ✅ Case dropdown in all modules
- ✅ Auto case creation
- ✅ Case persistence across modules

### **Visual Feedback**
- ✅ Loading spinners
- ✅ Toast notifications
- ✅ Progress bars
- ✅ Confidence gauges
- ✅ Status badges

### **Interactivity**
- ✅ Drag-and-drop file upload
- ✅ Preview before upload
- ✅ Hover effects
- ✅ Smooth transitions
- ✅ Animations

---

## 📖 **For Users/Judges**

### **Demo Script**

**1. Login** (30 seconds)
```
"Let me show you our Clinical AI Co-Pilot system.
First, we login with our demo credentials..."
```

**2. Dashboard** (1 minute)
```
"Here's our dashboard - you can see we have 47 total cases,
with 12 pending review. The system has 4 main analysis modules:
X-Ray, Heart Risk, Symptoms, and Document processing."
```

**3. X-Ray Analysis** (2 minutes)
```
"Let's analyze a chest X-ray. I'll upload this image...
[Upload] The CNN model analyzes it and... 
[Results] It detected pneumonia with 87% confidence.
Notice the Grad-CAM heatmap showing where the model focused."
```

**4. Heart Assessment** (2 minutes)
```
"Now let's assess cardiovascular risk. I'll enter the patient's
clinical features... [Enter data] The ANN model calculates...
[Results] High risk detected. The SHAP chart shows which
features contributed most to this prediction."
```

**5. Review & Report** (2 minutes)
```
"In the review dashboard, clinicians can see all predictions,
approve or edit them, and generate a comprehensive PDF report
with all findings and explainability visualizations."
```

---

## ✅ **UI Checklist for Judges**

When demoing, show:

- [ ] **Modern Design**: Dark glassmorphism aesthetic
- [ ] **Modular Architecture**: Separate focused pages
- [ ] **Multi-Modal**: 3 different AI models integrated
- [ ] **Explainability**: Grad-CAM, SHAP, Top-3
- [ ] **HITL Workflow**: Human review and approval
- [ ] **Complete Pipeline**: Upload → Analyze → Review → Report
- [ ] **Professional UX**: Smooth, intuitive, responsive

---

## 📞 **Need Help?**

- **Complete Docs**: Check `frontend/README.md`
- **Navigation**: Check `frontend/SITEMAP.md`
- **Quick Start**: Check `frontend/QUICK_START.md`
- **Before/After**: Check `frontend/BEFORE_AFTER.md`

---

**Your UI is ready to showcase! 🎉**
