# 🚀 OPS-FRONTEND QUICK START GUIDE

**Ready to implement immediately!** Backend APIs are 100% working.

---

## ⚡ IMMEDIATE SETUP (30 minutes)

### **Step 1: Initialize Project**
```bash
# Navigate to project root
cd D:/my-projects/ConvergeAI

# Create new Vite + React project
npm create vite@latest ops-frontend -- --template react
cd ops-frontend

# Install core dependencies
npm install

# Install additional dependencies (matching customer-frontend)
npm install react-router-dom axios
npm install @tanstack/react-query @tanstack/react-table
npm install tailwindcss @tailwindcss/forms @tailwindcss/typography
npm install class-variance-authority clsx tailwind-merge
npm install lucide-react framer-motion
npm install react-hook-form @hookform/resolvers zod
npm install recharts date-fns

# Install dev dependencies
npm install -D @types/node
```

### **Step 2: Configure TailwindCSS**
```bash
# Initialize Tailwind
npx tailwindcss init -p

# Update tailwind.config.js (copy from customer-frontend)
# Update src/index.css (copy from customer-frontend)
```

### **Step 3: Create Folder Structure**
```bash
# Create all required folders
mkdir -p src/api src/components/common src/components/layout
mkdir -p src/components/dashboard src/components/priority-queue
mkdir -p src/components/alerts src/components/staff src/components/ui
mkdir -p src/context src/hooks src/pages src/services src/utils
```

---

## 📁 FOLDER STRUCTURE TO CREATE

```
ops-frontend/src/
├── api/
│   ├── axiosConfig.js      # Centralized axios for ops APIs
│   ├── errorHandler.js     # Error handling utilities
│   ├── urls.js            # API endpoint URLs
│   └── index.js           # Main API exports
├── components/
│   ├── common/            # Shared components (Button, Modal, etc.)
│   ├── layout/            # Layout components
│   │   ├── Sidebar.jsx    # Main navigation sidebar
│   │   ├── Header.jsx     # Top header with user menu
│   │   └── MainLayout.jsx # Main layout wrapper
│   ├── dashboard/         # Dashboard components
│   │   ├── MetricCard.jsx # Individual metric display
│   │   ├── MetricChart.jsx # Chart components
│   │   └── DashboardGrid.jsx # Dashboard layout
│   ├── priority-queue/    # Priority queue components
│   │   ├── PriorityTable.jsx # Main data table
│   │   ├── FilterBar.jsx  # Filtering controls
│   │   └── ItemDetail.jsx # Item detail modal
│   ├── alerts/            # Alert components
│   │   ├── AlertBell.jsx  # Header notification icon
│   │   ├── AlertList.jsx  # Alert management page
│   │   └── AlertModal.jsx # Alert detail modal
│   ├── staff/             # Staff management components
│   │   ├── StaffTable.jsx # Staff list table
│   │   ├── StaffDetail.jsx # Staff detail view
│   │   └── RoleManager.jsx # Role management
│   └── ui/                # shadcn/ui components
├── context/
│   ├── AuthContext.jsx    # Staff authentication
│   ├── AlertContext.jsx   # Real-time alerts
│   └── ThemeContext.jsx   # Theme management
├── hooks/
│   ├── useAuth.js         # Authentication hook
│   ├── useMetrics.js      # Dashboard metrics
│   ├── usePriorityQueue.js # Priority queue data
│   ├── useAlerts.js       # Alert management
│   └── useStaff.js        # Staff management
├── pages/
│   ├── LoginPage.jsx      # Staff login
│   ├── Dashboard.jsx      # Main dashboard
│   ├── PriorityQueue.jsx  # Priority queue page
│   ├── Alerts.jsx         # Alert management
│   ├── Staff.jsx          # Staff management
│   └── Config.jsx         # Configuration
├── services/
│   ├── api.js             # Main API service
│   ├── authService.js     # Authentication
│   ├── metricsService.js  # Metrics
│   ├── priorityQueueService.js # Priority queue
│   ├── alertService.js    # Alerts
│   └── staffService.js    # Staff management
└── utils/
    ├── formatters.js      # Data formatting
    ├── validators.js      # Form validation
    ├── constants.js       # App constants
    └── permissions.js     # Permission utilities
```

---

## 🔧 KEY FILES TO CREATE FIRST

### **1. Environment Variables (.env.local)**
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1/ops
VITE_WS_URL=ws://localhost:8000/ws/ops
VITE_APP_NAME=ConvergeAI Operations
VITE_APP_VERSION=1.0.0
```

### **2. API Configuration (src/api/urls.js)**
```javascript
// API endpoint URLs for ops frontend
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/ops';

export const API_ENDPOINTS = {
  // Authentication
  AUTH_LOGIN: '/auth/login',
  AUTH_LOGOUT: '/auth/logout',
  AUTH_REFRESH: '/auth/refresh',
  AUTH_ME: '/auth/me',
  
  // Dashboard & Metrics
  DASHBOARD_METRICS: '/dashboard/metrics',
  PRIORITY_QUEUE: '/dashboard/priority-queue',
  
  // Individual Metrics
  METRICS_BOOKINGS: '/metrics/bookings',
  METRICS_COMPLAINTS: '/metrics/complaints',
  METRICS_SLA: '/metrics/sla',
  METRICS_REVENUE: '/metrics/revenue',
  METRICS_REALTIME: '/metrics/realtime',
  
  // Operations
  COMPLAINTS: '/complaints',
  USERS: '/users',
  CONFIG: '/config',
};
```

### **3. Axios Configuration (src/api/axiosConfig.js)**
```javascript
// Copy and adapt from customer-frontend/src/api/axiosConfig.js
// Change base URL to ops endpoints
// Adapt error handling for staff-specific errors
// Add ops-specific request/response interceptors
```

### **4. Main App Component (src/App.jsx)**
```javascript
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";
import { AlertProvider } from "./context/AlertContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import PriorityQueue from "./pages/PriorityQueue";
import Alerts from "./pages/Alerts";
import Staff from "./pages/Staff";
import Config from "./pages/Config";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AlertProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/priority-queue" element={
                <ProtectedRoute>
                  <PriorityQueue />
                </ProtectedRoute>
              } />
              <Route path="/alerts" element={
                <ProtectedRoute>
                  <Alerts />
                </ProtectedRoute>
              } />
              <Route path="/staff" element={
                <ProtectedRoute>
                  <Staff />
                </ProtectedRoute>
              } />
              <Route path="/config" element={
                <ProtectedRoute>
                  <Config />
                </ProtectedRoute>
              } />
            </Routes>
          </Router>
        </AlertProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

## 🎯 FIRST MILESTONE (Day 1)

**Goal:** Working staff login and basic dashboard layout

### **Tasks:**
1. ✅ Project initialization and dependencies
2. ✅ Folder structure creation
3. ✅ Environment configuration
4. ✅ Basic routing setup
5. ✅ Staff login page (copy/adapt from customer-frontend)
6. ✅ AuthContext for staff authentication
7. ✅ Protected routes with role checking
8. ✅ Basic layout with sidebar and header

### **Success Criteria:**
- Staff can login with backend API
- Protected routes work correctly
- Basic layout renders properly
- Navigation between pages works

---

## 📋 BACKEND API REFERENCE

**All endpoints are working and tested:**

### **Authentication:**
- `POST /api/v1/ops/auth/login` - Staff login
- `GET /api/v1/ops/auth/me` - Get staff profile
- `POST /api/v1/ops/auth/logout` - Staff logout

### **Dashboard:**
- `GET /api/v1/ops/dashboard/metrics` - All metrics
- `GET /api/v1/ops/dashboard/priority-queue` - Priority items

### **Operations:**
- `GET /api/v1/ops/complaints` - List complaints
- `GET /api/v1/ops/complaints/{id}` - Get complaint
- `PUT /api/v1/ops/complaints/{id}` - Update complaint
- `GET /api/v1/ops/users` - List staff users

**Backend server running on:** `http://localhost:8000`

---

## 🚀 READY TO START!

**Everything is prepared for immediate implementation:**
- ✅ Backend APIs are 100% working
- ✅ Architecture plan is complete
- ✅ Task breakdown is ready
- ✅ Technical specifications are defined
- ✅ Reference patterns from customer-frontend

**Start with:** `npm create vite@latest ops-frontend -- --template react`
