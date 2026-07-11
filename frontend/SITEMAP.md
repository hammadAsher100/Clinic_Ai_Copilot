# Clinical AI Co-Pilot — Site Navigation Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOGIN (index.html)                          │
│                    Username: clinician / demo2026                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      DASHBOARD (dashboard.html)                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Stats: Total Cases | Pending | In Review | Completed       │   │
│  │  Recent Activity Feed | Quick Case Creation                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┘
   │      │      │      │      │      │      │      │      │
   │      │      │      │      │      │      │      │      │
   ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│X-RAY ││HEART ││SYMPT-││DOCS  ││CASES ││REVIEW││REPORT││UPLOAD│
│ANALY-││RISK  ││OMS   ││UPLD  ││MGMT  ││DASH  ││MGMT  ││LEGACY│
│SIS   ││ASSES-││CLASS-││      ││      ││(HITL)││      ││      │
│      ││MENT  ││IFIER ││      ││      ││      ││      ││      │
└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘
   │      │      │      │      │      │      │      │
   │      │      │      │      │      │      │      │
   └──────┴──────┴──────┴──────┘      │      │      │
                │                      │      │      │
                ↓                      ↓      ↓      ↓
         ┌────────────┐         ┌────────────────────┐
         │  CASE FLOW │────────→│  REVIEW → REPORT   │
         │(Link Cases)│         │   (HITL Workflow)  │
         └────────────┘         └────────────────────┘
```

---

## 📍 Page Hierarchy

### **Level 1: Entry**
- `index.html` - Login & Authentication

### **Level 2: Hub**
- `dashboard.html` - Central control & navigation

### **Level 3A: Analysis Modules** (Create/Add Data)
- `xray.html` - X-Ray image analysis
- `heart.html` - Heart risk assessment
- `symptoms.html` - Symptom classification
- `documents.html` - Document extraction

### **Level 3B: Management Modules** (View/Manage)
- `cases.html` - Case listing & management
- `review.html` - HITL review workflow
- `report.html` - Report download & management

### **Level 4: Legacy**
- `upload.html` - All-in-one upload (deprecated)

---

## 🔄 User Flow Examples

### **Flow 1: New Patient Analysis**
```
Login → Dashboard → X-Ray Analysis
                    └→ [Upload X-ray]
                    └→ Heart Assessment
                       └→ [Enter vitals]
                       └→ Symptom Classifier
                          └→ [Enter symptoms]
                          └→ Review Dashboard
                             └→ [Approve/Edit]
                             └→ Generate Report
                                └→ Reports
                                   └→ [Download PDF]
```

### **Flow 2: Case Management**
```
Login → Dashboard → Cases
                    └→ [View all cases]
                    └→ [Select case]
                    └→ Review Dashboard
                       └→ [Review predictions]
                       └→ Reports
                          └→ [Download]
```

### **Flow 3: Single Module Analysis**
```
Login → Dashboard → [Select any module]
                    └→ [Analyze]
                    └→ [View results]
                    └→ Review (optional)
                    └→ Dashboard (return)
```

---

## 🎯 Cross-Module Data Flow

```
┌──────────────┐
│  Create Case │ ────┐
└──────────────┘     │
                     ↓
┌────────────────────────────────────┐
│         Case ID (Shared)           │
└────────────────────────────────────┘
     │           │           │
     ↓           ↓           ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│ X-Ray   │ │ Heart   │ │Symptoms │
│ Module  │ │ Module  │ │ Module  │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┴───────────┘
                 │
                 ↓
         ┌───────────────┐
         │ Predictions   │
         │ (Database)    │
         └───────┬───────┘
                 │
                 ↓
         ┌───────────────┐
         │ Review Module │
         │ (HITL)        │
         └───────┬───────┘
                 │
                 ↓
         ┌───────────────┐
         │ Report (PDF)  │
         └───────────────┘
```

---

## 🧭 Navigation Menu Structure

### **Desktop Menu** (All pages except login)
```
┌──────────────────────────────────────────────────────────┐
│  🏥 Clinical AI Co-Pilot                           User ●│
│  [Dashboard] [Cases] [Review] [Reports]          [Logout]│
└──────────────────────────────────────────────────────────┘
```

### **Module-Specific Navigation**
```
┌──────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                      │
│  🫁 Chest X-Ray Analysis                                  │
│  [CNN · Pneumonia Detection]                              │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Module Interconnections

### **Analysis Modules → Review**
All analysis modules feed data into the Review Dashboard:
- X-Ray results → Image modality card
- Heart results → Tabular modality card
- Symptoms results → Text modality card

### **Review → Reports**
After HITL review is complete:
- Generate Report button in Review
- Download report from Reports page
- View status of all reports

### **Cases → All Modules**
Cases page serves as a central hub:
- View all cases with status
- Launch any analysis module with case context
- Direct navigation to Review for specific case

---

## 🔐 Access Control

### **Public Pages** (No authentication required)
- `index.html` (Login page only)

### **Protected Pages** (JWT required)
- All other pages require authentication
- Auto-redirect to login if not authenticated
- Token stored in localStorage

---

## 📱 Mobile Navigation

### **Responsive Menu** (< 768px)
```
┌──────────────────────────────────┐
│  ☰  Clinical AI Co-Pilot    User│
└──────────────────────────────────┘
    ↓ (Expand)
┌──────────────────────────────────┐
│  [Dashboard]                     │
│  [Cases]                         │
│  [Review]                        │
│  [Reports]                       │
│  [Logout]                        │
└──────────────────────────────────┘
```

---

## 🎨 Visual Indicators

### **Page Status Badges**
- 🟢 Active page (teal highlight in nav)
- 🔵 Standard page (blue icon)
- 🟠 Legacy page (amber warning)

### **Case Status Colors**
- 🟡 **Pending** (amber) - Awaiting analysis
- 🔵 **In Review** (blue) - Under clinician review
- 🟢 **Completed** (teal) - Finalized with report

### **Risk Indicators**
- 🟢 **Normal/Low Risk** (teal)
- 🟡 **Moderate** (amber)
- 🔴 **High Risk/Positive** (coral)

---

## 🚦 Recommended User Paths

### **For First-Time Users**
1. Start at Dashboard
2. Read module descriptions
3. Try X-Ray Analysis with sample image
4. Explore Review Dashboard
5. Download sample report

### **For Clinical Workflow**
1. Create case from Dashboard
2. Complete all 3 analyses (X-Ray → Heart → Symptoms)
3. Review predictions in Review Dashboard
4. Generate and download report

### **For Case Management**
1. Navigate to Cases page
2. Review case statistics
3. Select case for review
4. Add additional analyses as needed

---

## 📖 Documentation Links

- **Detailed Module Docs**: `UI_MODULES.md`
- **Quick Start Guide**: `QUICK_START.md`
- **API Documentation**: `../README.md`
- **Project Context**: `../.agents/AGENTS.md`

---

**Version**: 2.0 (Modular Architecture)  
**Last Updated**: 2026-07-12
