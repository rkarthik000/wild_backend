"""
GET  /api/incidents          — List all incidents (filterable by status)
GET  /api/incidents/{id}     — Get single incident
PATCH /api/incidents/{id}    — Update status (RESOLVED, RESPONDED, etc.)
GET  /api/incidents/stats    — Summary counts for dashboard stats cards
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from core import database as db
from models.schemas import IncidentOut, StatusUpdate

router = APIRouter()


@router.get("/stats")
async def incident_stats():
    """Returns summary counts used by the dashboard stat cards."""
    all_incidents = await db.list_incidents(limit=500)
    active    = [i for i in all_incidents if i["status"] == "ACTIVE"]
    resolved  = [i for i in all_incidents if i["status"] == "RESOLVED"]
    responded = [i for i in all_incidents if i["status"] == "RESPONDED"]

    cameras = await db.list_cameras()
    rangers = await db.list_rangers()

    return {
        "total_incidents":    len(all_incidents),
        "active_threats":     len(active),
        "resolved_today":     len(resolved),
        "responded":          len(responded),
        "cameras_online":     sum(1 for c in cameras if c["online"]),
        "cameras_total":      len(cameras),
        "rangers_deployed":   sum(1 for r in rangers if r["status"] == "DEPLOYED"),
        "rangers_standby":    sum(1 for r in rangers if r["status"] == "STANDBY"),
    }


@router.get("", response_model=List[IncidentOut])
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE | RESPONDED | RESOLVED | LOGGED"),
    limit:  int           = Query(50, ge=1, le=200),
):
    incidents = await db.list_incidents(limit=limit, status=status)
    return incidents


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: str):
    incident = await db.get_incident(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(incident_id: str, body: StatusUpdate):
    incident = await db.get_incident(incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    updated = await db.update_incident_status(incident_id, body.status.value)
    return updated
