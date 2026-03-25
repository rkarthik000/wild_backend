"""
Database layer.
• If SUPABASE_URL is set  → uses Supabase (Postgres) via supabase-py
• Otherwise               → uses local SQLite via aiosqlite (great for hackathon dev)
"""

import os
import json
import uuid
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.config import settings

DB_PATH = "wildguard.db"


# ─── SQLite helpers (local / offline mode) ───────────────────────────────────

async def init_db():
    """Create tables if they don't exist (SQLite mode)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id          TEXT PRIMARY KEY,
                type        TEXT NOT NULL,
                camera_id   TEXT,
                location    TEXT,
                latitude    REAL,
                longitude   REAL,
                confidence  REAL,
                species     TEXT,
                status      TEXT DEFAULT 'ACTIVE',
                image_path  TEXT,
                detections  TEXT,   -- JSON blob
                created_at  TEXT,
                updated_at  TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id          TEXT PRIMARY KEY,
                sector      TEXT,
                latitude    REAL,
                longitude   REAL,
                online      INTEGER DEFAULT 1,
                last_ping   TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rangers (
                id          TEXT PRIMARY KEY,
                name        TEXT,
                phone       TEXT,
                status      TEXT DEFAULT 'STANDBY',
                sector      TEXT,
                latitude    REAL,
                longitude   REAL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id           TEXT PRIMARY KEY,
                incident_id  TEXT,
                ranger_id    TEXT,
                channel      TEXT,   -- SMS | EMAIL | PUSH
                message      TEXT,
                sent_at      TEXT,
                delivered    INTEGER DEFAULT 0
            )
        """)
        # Seed cameras and rangers if empty
        await _seed_if_empty(db)
        await db.commit()


async def _seed_if_empty(db):
    cur = await db.execute("SELECT COUNT(*) FROM cameras")
    (count,) = await cur.fetchone()
    if count > 0:
        return

    cameras = [
        ("CAM-03", "North",   -2.2, 37.1),
        ("CAM-07", "Bravo",   -2.4, 37.2),
        ("CAM-08", "Savanna", -2.5, 37.3),
        ("CAM-12", "East",    -2.6, 37.5),
        ("CAM-15", "River",   -2.3, 37.6),
        ("CAM-19", "Delta",   -2.8, 37.4),
    ]
    for cam_id, sector, lat, lng in cameras:
        await db.execute(
            "INSERT INTO cameras VALUES (?,?,?,?,1,?)",
            (cam_id, sector, lat, lng, datetime.utcnow().isoformat()),
        )

    rangers = [
        (str(uuid.uuid4()), "Osei K.",  "+1000000001", "DEPLOYED", "Bravo",  -2.41, 37.21),
        (str(uuid.uuid4()), "Amara N.", "+1000000002", "STANDBY",  "Base",   -2.50, 37.30),
        (str(uuid.uuid4()), "Zuri M.",  "+1000000003", "DEPLOYED", "North",  -2.21, 37.11),
        (str(uuid.uuid4()), "Kwame A.", "+1000000004", "OFF-DUTY", None,     None,  None),
    ]
    for r in rangers:
        await db.execute("INSERT INTO rangers VALUES (?,?,?,?,?,?,?)", r)


# ─── Incident CRUD ───────────────────────────────────────────────────────────

async def create_incident(data: Dict[str, Any]) -> Dict:
    incident_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO incidents
               (id, type, camera_id, location, latitude, longitude,
                confidence, species, status, image_path, detections, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                incident_id,
                data.get("type"),
                data.get("camera_id"),
                data.get("location"),
                data.get("latitude"),
                data.get("longitude"),
                data.get("confidence"),
                data.get("species"),
                data.get("status", "ACTIVE"),
                data.get("image_path"),
                json.dumps(data.get("detections", [])),
                now, now,
            ),
        )
        await db.commit()
    return await get_incident(incident_id)


async def get_incident(incident_id: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM incidents WHERE id=?", (incident_id,))
        row = await cur.fetchone()
        return _row_to_dict(row) if row else None


async def list_incidents(limit: int = 50, status: Optional[str] = None) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cur = await db.execute(
                "SELECT * FROM incidents WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            )
        else:
            cur = await db.execute(
                "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
            )
        rows = await cur.fetchall()
        return [_row_to_dict(r) for r in rows]


async def update_incident_status(incident_id: str, status: str) -> Optional[Dict]:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE incidents SET status=?, updated_at=? WHERE id=?",
            (status, now, incident_id),
        )
        await db.commit()
    return await get_incident(incident_id)


# ─── Camera CRUD ─────────────────────────────────────────────────────────────

async def list_cameras() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM cameras ORDER BY id")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_camera_ping(camera_id: str):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cameras SET online=1, last_ping=? WHERE id=?", (now, camera_id)
        )
        await db.commit()


# ─── Ranger CRUD ─────────────────────────────────────────────────────────────

async def list_rangers() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM rangers ORDER BY name")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_nearest_ranger(lat: float, lng: float) -> Optional[Dict]:
    """Returns the nearest STANDBY ranger (basic Euclidean distance)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM rangers WHERE status='STANDBY' AND latitude IS NOT NULL"
        )
        rows = await cur.fetchall()
        if not rows:
            return None
        def dist(r):
            return ((r["latitude"] - lat) ** 2 + (r["longitude"] - lng) ** 2) ** 0.5
        return dict(min(rows, key=dist))


async def update_ranger_status(ranger_id: str, status: str, sector: Optional[str] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if sector:
            await db.execute(
                "UPDATE rangers SET status=?, sector=? WHERE id=?",
                (status, sector, ranger_id),
            )
        else:
            await db.execute(
                "UPDATE rangers SET status=? WHERE id=?", (status, ranger_id)
            )
        await db.commit()


# ─── Alert log ───────────────────────────────────────────────────────────────

async def log_alert(incident_id: str, ranger_id: Optional[str], channel: str, message: str, delivered: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO alerts (id, incident_id, ranger_id, channel, message, sent_at, delivered) VALUES (?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), incident_id, ranger_id, channel, message,
             datetime.utcnow().isoformat(), int(delivered)),
        )
        await db.commit()


async def list_alerts(limit: int = 20) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM alerts ORDER BY sent_at DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ─── Utility ─────────────────────────────────────────────────────────────────

def _row_to_dict(row) -> Dict:
    d = dict(row)
    if d.get("detections") and isinstance(d["detections"], str):
        try:
            d["detections"] = json.loads(d["detections"])
        except Exception:
            d["detections"] = []
    return d
