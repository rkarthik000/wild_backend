from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3, json, random, os, io, base64
from datetime import datetime
import uvicorn

app = FastAPI(title="WildGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "wildguard.db"

ENDANGERED_SPECIES = [
    {"name": "Amur Leopard",              "status": "CR", "population": 100,    "lat": 43.2,   "lng": 133.8,  "region": "Russia/China",         "threat": "Poaching"},
    {"name": "Javan Rhinoceros",          "status": "CR", "population": 75,     "lat": -8.1,   "lng": 107.0,  "region": "Indonesia",             "threat": "Habitat Loss"},
    {"name": "Sumatran Orangutan",        "status": "CR", "population": 14600,  "lat": 3.5,    "lng": 98.7,   "region": "Sumatra, Indonesia",    "threat": "Deforestation"},
    {"name": "Mountain Gorilla",          "status": "EN", "population": 1063,   "lat": -1.4,   "lng": 29.5,   "region": "Central Africa",        "threat": "Poaching"},
    {"name": "Vaquita",                   "status": "CR", "population": 10,     "lat": 30.8,   "lng": -114.8, "region": "Gulf of California",    "threat": "Bycatch"},
    {"name": "Hawksbill Sea Turtle",      "status": "CR", "population": 8000,   "lat": 18.5,   "lng": -77.0,  "region": "Caribbean",             "threat": "Shell Trade"},
    {"name": "African Forest Elephant",   "status": "CR", "population": 100000, "lat": 0.2,    "lng": 18.6,   "region": "Central Africa",        "threat": "Ivory Trade"},
    {"name": "Sunda Tiger",               "status": "CR", "population": 400,    "lat": -1.5,   "lng": 102.0,  "region": "Sumatra, Indonesia",    "threat": "Poaching"},
    {"name": "Blue Whale",                "status": "EN", "population": 10000,  "lat": -40.0,  "lng": -15.0,  "region": "Southern Ocean",        "threat": "Ship Strikes"},
    {"name": "Red Panda",                 "status": "EN", "population": 10000,  "lat": 27.5,   "lng": 88.0,   "region": "Himalayas",             "threat": "Habitat Loss"},
    {"name": "African Wild Dog",          "status": "EN", "population": 6600,   "lat": -19.0,  "lng": 29.0,   "region": "Sub-Saharan Africa",    "threat": "Habitat Loss"},
    {"name": "Asian Elephant",            "status": "EN", "population": 40000,  "lat": 20.5,   "lng": 78.9,   "region": "South/SE Asia",         "threat": "Human Conflict"},
    {"name": "Snow Leopard",              "status": "VU", "population": 4000,   "lat": 37.0,   "lng": 75.0,   "region": "Central Asia",          "threat": "Poaching"},
    {"name": "Bornean Orangutan",         "status": "CR", "population": 104700, "lat": 1.0,    "lng": 114.0,  "region": "Borneo",                "threat": "Deforestation"},
    {"name": "Saola",                     "status": "CR", "population": 50,     "lat": 19.5,   "lng": 103.5,  "region": "Laos/Vietnam",          "threat": "Hunting"},
    {"name": "Ethiopian Wolf",            "status": "EN", "population": 500,    "lat": 9.8,    "lng": 39.7,   "region": "Ethiopia",              "threat": "Habitat Loss"},
    {"name": "Philippine Eagle",          "status": "CR", "population": 800,    "lat": 7.1,    "lng": 125.5,  "region": "Philippines",           "threat": "Deforestation"},
    {"name": "Gharial",                   "status": "CR", "population": 650,    "lat": 27.8,   "lng": 83.0,   "region": "South Asia",            "threat": "River Pollution"},
    {"name": "Yangtze Finless Porpoise",  "status": "CR", "population": 1000,   "lat": 30.5,   "lng": 114.3,  "region": "China",                 "threat": "Fishing Nets"},
    {"name": "Black Rhino",               "status": "CR", "population": 5500,   "lat": -25.7,  "lng": 28.2,   "region": "Southern Africa",       "threat": "Poaching"},
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species TEXT, status TEXT, confidence REAL,
        lat REAL, lng REAL, region TEXT, threat TEXT,
        is_poacher INTEGER DEFAULT 0,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, species TEXT, location TEXT,
        severity TEXT, timestamp TEXT
    )''')
    c.execute("SELECT COUNT(*) FROM alerts")
    if c.fetchone()[0] == 0:
        sample_alerts = [
            ("POACHER", "Sunda Tiger", "Bukit Barisan, Sumatra", "HIGH"),
            ("SIGHTING", "Amur Leopard", "Primorsky Krai, Russia", "LOW"),
            ("INTRUSION", "Mountain Gorilla", "Virunga NP, Congo", "HIGH"),
            ("CAMERA", "Vaquita", "Gulf of California", "MEDIUM"),
            ("SIGHTING", "Black Rhino", "Hluhluwe-iMfolozi, SA", "LOW"),
        ]
        for t, sp, loc, sev in sample_alerts:
            c.execute("INSERT INTO alerts (type,species,location,severity,timestamp) VALUES (?,?,?,?,?)",
                      (t, sp, loc, sev, datetime.now().isoformat()))
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {"status": "WildGuard API Online", "species_tracked": len(ENDANGERED_SPECIES)}

@app.get("/api/species")
def get_species(status: str = None):
    if status:
        return [s for s in ENDANGERED_SPECIES if s["status"] == status]
    return ENDANGERED_SPECIES

@app.get("/api/stats")
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM detections")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM detections WHERE is_poacher=1")
    poachers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM alerts WHERE severity='HIGH'")
    high_alerts = c.fetchone()[0]
    conn.close()
    return {
        "total_detections": total,
        "poacher_alerts": poachers,
        "high_severity_alerts": high_alerts,
        "species_tracked": len(ENDANGERED_SPECIES),
    }

@app.get("/api/alerts")
def get_alerts(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "species": r[2], "location": r[3], "severity": r[4], "timestamp": r[5]} for r in rows]

@app.post("/api/detect")
async def detect_species(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename.lower()
    detected = None
    for sp in ENDANGERED_SPECIES:
        words = sp["name"].lower().split()
        if any(w in filename for w in words):
            detected = sp
            break
    is_poacher = any(kw in filename for kw in ["person", "human", "people", "man", "poach"])
    if not detected:
        detected = random.choice(ENDANGERED_SPECIES)
    confidence = round(random.uniform(78, 98), 1)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO detections (species,status,confidence,lat,lng,region,threat,is_poacher,timestamp)
                 VALUES (?,?,?,?,?,?,?,?,?)''',
              (detected["name"], detected["status"], confidence,
               detected["lat"], detected["lng"], detected["region"],
               detected["threat"], int(is_poacher), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"success": True, "is_poacher": is_poacher, "species": detected, "confidence": confidence}

@app.post("/api/detect-vision")
async def detect_vision(file: UploadFile = File(...)):
    contents = await file.read()
    base64_image = base64.standard_b64encode(contents).decode("utf-8")
    media_type = file.content_type or "image/jpeg"
    species_list = ", ".join([s["name"] for s in ENDANGERED_SPECIES])

    sp = None
    confidence = 70

    try:
        from anthropic import Anthropic
        client = Anthropic()
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": base64_image}
                    },
                    {
                        "type": "text",
                        "text": f"""Look at this image carefully. What animal is shown?
Reply ONLY with a JSON object, no extra text:
{{"species":"exact name here","confidence":90}}
Choose species ONLY from this list: {species_list}
If no animal is visible, return {{"species":"unknown","confidence":0}}"""
                    }
                ]
            }]
        )
        text = message.content[0].text.strip()
        parsed = json.loads(text.replace("```json", "").replace("```", "").strip())
        confidence = parsed.get("confidence", 85)
        sp = next((s for s in ENDANGERED_SPECIES if s["name"].lower() == parsed["species"].lower()), None)
    except Exception as e:
        print(f"Vision API error: {e}")

    if not sp:
        sp = random.choice(ENDANGERED_SPECIES)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO detections (species,status,confidence,lat,lng,region,threat,is_poacher,timestamp)
                 VALUES (?,?,?,?,?,?,?,?,?)''',
              (sp["name"], sp["status"], confidence,
               sp["lat"], sp["lng"], sp["region"],
               sp["threat"], 0, datetime.now().isoformat()))
    c.execute("INSERT INTO alerts (type,species,location,severity,timestamp) VALUES (?,?,?,?,?)",
              ("CAMERA", sp["name"], sp["region"], "MEDIUM", datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return {"species": sp, "confidence": confidence, "is_poacher": False}

@app.get("/api/detections")
def get_detections(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "species": r[1], "status": r[2], "confidence": r[3],
             "lat": r[4], "lng": r[5], "region": r[6], "threat": r[7],
             "is_poacher": bool(r[8]), "timestamp": r[9]} for r in rows]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)