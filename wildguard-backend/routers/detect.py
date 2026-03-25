"""
POST /api/detect/image    — Upload image, get detections + auto-create incident
POST /api/detect/url      — Detect from a public image URL (camera feed)
GET  /api/detect/demo     — Fire a mock detection (great for live demos)
"""

import io
import os
import uuid
import logging
import httpx
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Form
from typing import Optional

from core.config import settings
from core import database as db
from models.schemas import DetectionResponse, ThreatType
from services import detection as det_svc
from services import alerts as alert_svc

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image", response_model=DetectionResponse)
async def detect_from_image(
    file: UploadFile = File(...),
    camera_id: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
):
    """
    Upload an image and run YOLOv8 + species classifier.
    Automatically creates an incident and alerts rangers for high-confidence threats.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > 50 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 50 MB)")

    # Save upload
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return await _process_detection(
        image_bytes=image_bytes,
        image_path=filepath,
        camera_id=camera_id,
        location=location,
        latitude=latitude,
        longitude=longitude,
    )


@router.post("/url", response_model=DetectionResponse)
async def detect_from_url(
    image_url: str = Query(..., description="Public URL of image to analyze"),
    camera_id: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
):
    """Fetch an image from a public URL and run detection."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
            image_bytes = resp.content
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch image: {e}")

    return await _process_detection(
        image_bytes=image_bytes,
        image_path=image_url,
        camera_id=camera_id,
        location=location,
        latitude=latitude,
        longitude=longitude,
    )


@router.get("/demo", response_model=DetectionResponse)
async def demo_detection(
    camera_id: str = Query("CAM-07", description="Camera to simulate"),
    location: str = Query("Sector Bravo", description="Location name"),
):
    """
    Fires a mock detection — perfect for live demos without a real camera feed.
    Randomly cycles through threat scenarios.
    """
    # Use mock service path
    detections, species = await det_svc.run_detection(b"demo")  # triggers mock path
    top_threat, top_conf = det_svc.get_top_threat(detections)

    incident_id = None
    alert_sent  = False

    if top_threat and top_conf >= settings.CONFIDENCE_THRESHOLD:
        camera = next(
            (c for c in await db.list_cameras() if c["id"] == camera_id),
            None,
        )
        lat = camera["latitude"] if camera else -2.4
        lng = camera["longitude"] if camera else 37.2

        incident = await db.create_incident({
            "type": top_threat.value,
            "camera_id": camera_id,
            "location": location,
            "latitude": lat,
            "longitude": lng,
            "confidence": top_conf,
            "species": species,
            "status": "ACTIVE",
            "image_path": "demo",
            "detections": [d.model_dump() for d in detections],
        })
        incident_id = incident["id"]

        if top_threat.value in settings.HIGH_THREAT_TYPES and top_conf >= settings.HIGH_THREAT_CONFIDENCE:
            alert_sent = await alert_svc.send_ranger_alert(
                incident_id=incident_id,
                threat_type=top_threat,
                confidence=top_conf,
                location=location,
                camera_id=camera_id,
                latitude=lat,
                longitude=lng,
            )

    return DetectionResponse(
        detections=detections,
        top_threat=top_threat,
        top_confidence=top_conf,
        species=species,
        incident_id=incident_id,
        alert_sent=alert_sent,
    )


# ── Shared processing logic ───────────────────────────────────────────────────

async def _process_detection(
    image_bytes: bytes,
    image_path: str,
    camera_id: Optional[str],
    location: Optional[str],
    latitude: Optional[float],
    longitude: Optional[float],
) -> DetectionResponse:
    detections, species = await det_svc.run_detection(image_bytes)
    top_threat, top_conf = det_svc.get_top_threat(detections)

    incident_id = None
    alert_sent  = False

    if top_threat and top_conf >= settings.CONFIDENCE_THRESHOLD:
        # Resolve camera location if not provided
        if not latitude and camera_id:
            camera = next(
                (c for c in await db.list_cameras() if c["id"] == camera_id),
                None,
            )
            if camera:
                latitude  = camera.get("latitude")
                longitude = camera.get("longitude")

        incident = await db.create_incident({
            "type": top_threat.value,
            "camera_id": camera_id,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "confidence": top_conf,
            "species": species,
            "status": "ACTIVE",
            "image_path": image_path,
            "detections": [d.model_dump() for d in detections],
        })
        incident_id = incident["id"]
        logger.info(f"Incident created: {incident_id} ({top_threat.value} {int(top_conf*100)}%)")

        # Auto-alert for high-confidence threats
        if top_threat.value in settings.HIGH_THREAT_TYPES and top_conf >= settings.HIGH_THREAT_CONFIDENCE:
            alert_sent = await alert_svc.send_ranger_alert(
                incident_id=incident_id,
                threat_type=top_threat,
                confidence=top_conf,
                location=location,
                camera_id=camera_id,
                latitude=latitude,
                longitude=longitude,
            )

    return DetectionResponse(
        detections=detections,
        top_threat=top_threat,
        top_confidence=top_conf,
        species=species,
        incident_id=incident_id,
        alert_sent=alert_sent,
    )
