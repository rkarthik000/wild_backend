# WildGuard v3 — Setup Guide

## File Placement

```
your-project/
├── wildguard-frontend/
│   └── src/
│       ├── App.jsx               ← Replace with provided App.jsx
│       ├── LoginPage.jsx         ← NEW: paste LoginPage.jsx here
│       └── WildGuardDashboard.jsx ← Replace with new version
└── wildguard-backend/
    ├── main.py
    └── requirements.txt
```

---

## Frontend Setup

```bash
cd wildguard-frontend
npm install
npm run dev
```

Open: http://localhost:5173

### Login Credentials
| Email                      | Password    | Role           |
|----------------------------|-------------|----------------|
| ranger@wildguard.io        | ranger123   | Field Ranger   |
| admin@wildguard.io         | admin123    | Administrator  |
| analyst@wildguard.io       | analyst123  | Data Analyst   |

---

## Backend Setup (Optional — frontend works standalone)

```bash
cd wildguard-backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

---

## Key API Endpoints

| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| GET    | /api/species       | All 20 endangered species          |
| GET    | /api/stats         | Dashboard statistics               |
| GET    | /api/alerts        | Recent alerts                      |
| POST   | /api/detect        | Upload image for AI detection      |
| GET    | /api/detections    | Detection history                  |

---

## Features

### Login Page
- Clean dark auth UI
- 3 demo user roles
- Click credential rows to auto-fill

### Live Map Tab
- Real Leaflet map (CartoDB dark tiles)
- All 20 endangered species pinned with emoji markers
- Color-coded by IUCN status (Red=CR, Orange=EN, Yellow=VU)
- Filter sidebar: All / Critical / Endangered / Vulnerable
- Click any species → map flies to location with popup
- Click map marker → shows species info overlay

### Species Tab
- Cards for all 20 species
- IUCN status badges, population bars
- Click card → jumps to map location

### AI Detect Tab
- Drag & drop or click to upload camera trap images
- Species detection (by filename → real YOLOv8 if backend running)
- Poacher detection for human images
- Auto-adds to alerts feed

### Alerts Tab
- Real-time feed (new alert every ~8 seconds)
- Severity levels: HIGH / MEDIUM / LOW
- Types: POACHER / SIGHTING / CAMERA / DRONE / INTRUSION

---

## Windows PowerShell Fix (if needed)
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
