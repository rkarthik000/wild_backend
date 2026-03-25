# WildGuard AI — Backend

FastAPI backend for real-time wildlife threat detection & ranger alert system.

## Quick Start (< 5 minutes)

```bash
# 1. Clone / enter the directory
cd wildguard-backend

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (all optional — works without keys)
cp .env.example .env
# Edit .env and add Twilio / Supabase keys if you have them

# 5. Run the server
python main.py
# → http://localhost:8000
# → http://localhost:8000/docs   (Swagger UI — test every endpoint here)
```

The server runs in **local mode** (SQLite + console alerts) with no keys needed.
Add Twilio + Supabase keys in `.env` to unlock SMS alerts and cloud DB.

---

## API Endpoints

### Detection
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/detect/image` | Upload image → detections + auto-incident |
| `POST` | `/api/detect/url` | Detect from public image URL |
| `GET`  | `/api/detect/demo` | Fire a mock detection (demo mode) |

### Incidents
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/incidents` | List incidents (filter by `?status=ACTIVE`) |
| `GET`  | `/api/incidents/stats` | Dashboard stat card counts |
| `GET`  | `/api/incidents/{id}` | Single incident |
| `PATCH`| `/api/incidents/{id}` | Update status (`RESOLVED`, `RESPONDED`, etc.) |

### Cameras
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/cameras` | List cameras + online status |
| `POST` | `/api/cameras/{id}/ping` | Camera heartbeat |

### Rangers
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/rangers` | List rangers + deployment status |
| `POST` | `/api/rangers/dispatch` | Dispatch ranger to incident (sends SMS) |
| `PATCH`| `/api/rangers/{id}/status` | Update ranger status |

### Alerts
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/alerts` | Recent alert log |

---

## Connecting to the React Dashboard

Replace the static data in `wildguard-dashboard.jsx` with live API calls:

```js
// Fetch live incidents
const res = await fetch("http://localhost:8000/api/incidents?status=ACTIVE");
const incidents = await res.json();

// Fire demo detection
await fetch("http://localhost:8000/api/detect/demo?camera_id=CAM-07&location=Sector+Bravo");

// Resolve an incident
await fetch(`http://localhost:8000/api/incidents/${id}`, {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ status: "RESOLVED" }),
});
```

For real-time updates (live incident feed), subscribe to Supabase:
```js
supabase
  .channel("incidents")
  .on("postgres_changes", { event: "INSERT", schema: "public", table: "incidents" },
    (payload) => setIncidents(prev => [payload.new, ...prev]))
  .subscribe();
```

---

## Architecture

```
POST /api/detect/image
        │
        ▼
  services/detection.py
  ├── YOLOv8 (object detection)
  │     └── person → POACHER
  │         truck  → VEHICLE
  │         knife  → WEAPON
  └── HuggingFace (species ID)
            └── elephant → "African Elephant"
        │
        ▼
  core/database.py  (SQLite | Supabase)
  └── incidents table
        │
        ▼
  services/alerts.py
  ├── Twilio SMS → nearest ranger
  └── console fallback
```

## Deploying to Railway (1-click)

```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway up
```

Set your `.env` variables in the Railway dashboard under Settings → Variables.
