# NEXCIV — Andhra Pradesh Municipal Administration Grievance Redressal & Cadre Workforce System

> **Official Civic Governance Platform for the 17 Municipal Corporations of Andhra Pradesh**  
> Powered by Multimodal AI (NLP + Computer Vision), Geospatial DBSCAN Clustering, and Automated Cadre Dispatch.

---

## 🏛️ System Overview

NEXCIV is an intelligent civic complaint registration, automated priority classification, and municipal cadre management platform built for Andhra Pradesh Municipal Administration & Urban Development (MA&UD).

### Key Architectural Pillars:
1. **Citizen Grievance Redressal Portal**:
   - Geotagged multi-photo complaint filing (up to 4 evidence photos).
   - Automated AI Priority Scoring (0–100) — no manual urgency guesswork; calculated from text severity, computer vision damage analysis, and GIS hazard multiplier.
   - Dedicated Public Complaint Detail Page (`/complaint/:id`) with 4-stage live tracking, resolution proofs, receipt printing, and community endorsements.
   - Google Sign-In & credential authentication.

2. **Municipal Cadre Staff Workspace (`/employee`)**:
   - Dedicated workspace for **40 Municipal Officers & Engineers** (`EMP-101` to `EMP-140`) across 5 Engineering Wings (*Roads & Buildings*, *Drainage & Sewerage*, *Water Supply & Quality*, *Electrical & Street Lighting*, *Sanitation & Public Health*).
   - Real-time assigned task queue, resolution note entry, and before/after completion photo verification.
   - Prominent Sign Out and security controls.

3. **Separate 2-Step Department Operations Command (`/department-login` & `/department`)**:
   - **Stage 1 (Municipal Corporation Verification)**: Authenticates across all **17 Municipal Corporations** (GVMC, VMC, GMC, KMC, TMC, RMC, NMC, etc.).
   - **Stage 2 (Department Head Authorization)**: Authenticates the specific Department Wing Head or Central Supreme Commissioner.
   - Live AI Geospatial Hotspot clustering (DBSCAN + Haversine).
   - **New Employee Induction**: Department heads can register new cadre employees directly into the database, who can immediately log in.

---

## 🚀 Live Deployment Guide

### Option 1: Deploy Backend to Render (Free Tier)
1. Push this repository to your **GitHub** account.
2. Sign up / Log in to [Render](https://render.com).
3. Click **New +** &rarr; **Web Service**.
4. Connect your GitHub repository.
5. Configure the service settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Under **Environment Variables**, add:
   - `SUPABASE_URL`: *(Your Supabase project URL)*
   - `SUPABASE_KEY`: *(Your Supabase anon key)*
7. Click **Create Web Service**. Your backend will be live at `https://your-backend.onrender.com`.

---

### Option 2: Deploy Frontend to Vercel (Recommended)
1. Sign up / Log in to [Vercel](https://vercel.com).
2. Click **Add New** &rarr; **Project**, and import your GitHub repository.
3. In the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Under **Environment Variables**, add:
   - `VITE_API_URL`: `https://your-backend.onrender.com` *(your live backend URL)*
   - `VITE_SUPABASE_URL`: `https://your-project.supabase.co`
   - `VITE_SUPABASE_ANON_KEY`: `your-anon-key`
5. Click **Deploy**. Your frontend is now completely live with instant SSL and automatic client-side routing rewrites (`vercel.json`).

---

### Option 3: Deploy Frontend to Netlify
1. Log in to [Netlify](https://netlify.com).
2. Import from Git &rarr; Select repository.
3. Set **Base directory**: `frontend`, **Build command**: `npm run build`, **Publish directory**: `frontend/dist`.
4. Add the environment variables: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
5. Deploy site. (SPA redirect routing is handled automatically by `frontend/public/_redirects`).

---

## 🔑 Demo Access Credentials

| Portal | URL Route | Identifier / Selection | Password |
|---|---|---|---|
| **Citizen Grievance** | `/login` | `citizen@nexciv.org` or Google Login | `citizen@123` |
| **Municipal Employee** | `/login` (Employee Tab) | Select or type any Cadre ID (`EMP-101` to `EMP-140`) | `emp@123` |
| **Department Operations** | `/department-login` | Stage 1: Select Corporation (`GVMC`, `VMC`, `GMC`, etc.) | `admin@123` |
| | | Stage 2: Select Wing Head / Supreme Commissioner | `dept@123` or `admin@123` |

---

## 💻 Local Development Setup

### 1. Backend Setup:
```bash
# Navigate to backend directory
cd backend

# Create & activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend Swagger API documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup:
```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Run Vite dev server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing

Run the live integration test suite:
```bash
cd backend
python test_backend_live.py
```
*All 12/12 live test suites verify health, 40 cadre employees, department auth, multimodal classification, complaint filing, work queue math, and spatial clustering.*
