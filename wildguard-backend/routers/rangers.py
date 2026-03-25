"""
GET  /api/rangers              — List all rangers + status
POST /api/rangers/dispatch     — Manually dispatch a ranger to an incident
PATCH /api/rangers/{id}/status — Update ranger status
"""

from fastapi import APIRouter, HTTPException
from typing import List

from core import database as db
from models.schemas import RangerOut, DispatchRequest
from services import alerts as alert_svc

router = APIRouter()


@router.get("", response_model=List[RangerOut])
async def list_rangers():
    return await db.list_rangers()


@router.post("/dispatch")
async def dispatch_ranger(body: DispatchRequest):
    """
    Manually assign a ranger to an incident and send them an SMS.
    Called when the 'DISPATCH RANGER' button is clicked in the dashboard.
    """
    success = await alert_svc.send_manual_alert(body.incident_id, body.ranger_id)
    if not success:
        raise HTTPException(400, "Dispatch failed — check incident_id and ranger_id")
    return {"status": "dispatched", "ranger_id": body.ranger_id, "incident_id": body.incident_id}


@router.patch("/{ranger_id}/status")
async def update_ranger_status(ranger_id: str, status: str, sector: str = None):
    await db.update_ranger_status(ranger_id, status, sector)
    return {"status": "updated", "ranger_id": ranger_id}
