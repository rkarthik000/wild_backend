"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ThreatType(str, Enum):
    POACHER        = "POACHER"
    WEAPON         = "WEAPON"
    VEHICLE        = "VEHICLE"
    ANIMAL_DISTRESS = "ANIMAL_DISTRESS"
    SPECIES_SPOTTED = "SPECIES_SPOTTED"
    UNKNOWN        = "UNKNOWN"


class IncidentStatus(str, Enum):
    ACTIVE    = "ACTIVE"
    RESPONDED = "RESPONDED"
    RESOLVED  = "RESOLVED"
    LOGGED    = "LOGGED"


class RangerStatus(str, Enum):
    STANDBY  = "STANDBY"
    DEPLOYED = "DEPLOYED"
    OFF_DUTY = "OFF-DUTY"


# ── Detection ─────────────────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox
    threat_type: ThreatType = ThreatType.UNKNOWN


class DetectionResponse(BaseModel):
    detections: List[Detection]
    top_threat: Optional[ThreatType]
    top_confidence: float
    species: Optional[str]
    incident_id: Optional[str]   # set if an incident was auto-created
    alert_sent: bool


# ── Incidents ─────────────────────────────────────────────────────────────────

class IncidentBase(BaseModel):
    type: ThreatType
    camera_id: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: float
    species: Optional[str] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentOut(IncidentBase):
    id: str
    status: IncidentStatus
    image_path: Optional[str] = None
    detections: List[Any] = []
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: IncidentStatus


# ── Cameras ───────────────────────────────────────────────────────────────────

class CameraOut(BaseModel):
    id: str
    sector: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    online: bool
    last_ping: Optional[str]


# ── Rangers ───────────────────────────────────────────────────────────────────

class RangerOut(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    status: str
    sector: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class DispatchRequest(BaseModel):
    incident_id: str
    ranger_id: str


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: str
    incident_id: Optional[str]
    ranger_id: Optional[str]
    channel: str
    message: str
    sent_at: str
    delivered: bool
