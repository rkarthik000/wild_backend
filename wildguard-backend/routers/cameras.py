"""
GET  /api/cameras            — List all cameras + online status
POST /api/cameras/{id}/ping  — Camera heartbeat (marks as online)
"""

from fastapi import APIRouter
from typing import List

from core import database as db
from models.schemas import CameraOut

router = APIRouter()


@router.get("", response_model=List[CameraOut])
async def list_cameras():
    cameras = await db.list_cameras()
    return [
        {**c, "online": bool(c["online"])}
        for c in cameras
    ]


@router.post("/{camera_id}/ping")
async def camera_ping(camera_id: str):
    """Called by each camera device on a heartbeat interval (e.g. every 30s)."""
    await db.update_camera_ping(camera_id)
    return {"status": "ok", "camera_id": camera_id}
