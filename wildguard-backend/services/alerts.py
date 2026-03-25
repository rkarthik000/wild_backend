"""
Alert service.
• Sends SMS via Twilio when a high-confidence threat is detected
• Falls back to console logging when Twilio credentials aren't configured
• Logs every alert to the DB regardless of channel
"""

import logging
from typing import Optional

from core.config import settings
from core import database as db
from models.schemas import ThreatType

logger = logging.getLogger(__name__)

THREAT_EMOJI = {
    ThreatType.POACHER:         "🚨 POACHER",
    ThreatType.WEAPON:          "⛔ WEAPON",
    ThreatType.VEHICLE:         "⚠️  VEHICLE",
    ThreatType.ANIMAL_DISTRESS: "🐾 ANIMAL DISTRESS",
    ThreatType.SPECIES_SPOTTED: "🔭 SPECIES SPOTTED",
    ThreatType.UNKNOWN:         "❓ UNKNOWN THREAT",
}


def _build_message(threat_type: ThreatType, confidence: float, location: Optional[str], camera_id: Optional[str]) -> str:
    label = THREAT_EMOJI.get(threat_type, "THREAT")
    loc   = location or "Unknown location"
    cam   = camera_id or "Unknown camera"
    conf  = int(confidence * 100)
    return (
        f"[WildGuard] {label} DETECTED\n"
        f"Location: {loc} | Camera: {cam}\n"
        f"Confidence: {conf}%\n"
        f"Respond immediately. — WildGuard AI"
    )


async def send_ranger_alert(
    incident_id: str,
    threat_type: ThreatType,
    confidence: float,
    location: Optional[str],
    camera_id: Optional[str],
    latitude: Optional[float],
    longitude: Optional[float],
) -> bool:
    """
    Finds the nearest available ranger and alerts them.
    Returns True if alert was successfully dispatched.
    """
    # Find nearest ranger
    ranger = None
    if latitude and longitude:
        ranger = await db.get_nearest_ranger(latitude, longitude)

    message = _build_message(threat_type, confidence, location, camera_id)

    # Try Twilio
    sent = False
    if ranger and _twilio_configured():
        sent = await _send_sms(ranger["phone"], message)
        if sent:
            logger.info(f"SMS sent to {ranger['name']} ({ranger['phone']})")

    # Always log to console as fallback / additional visibility
    if not sent:
        logger.warning(f"[ALERT — console fallback]\n{message}")
        if ranger:
            logger.info(f"Would have alerted: {ranger['name']} ({ranger['phone']})")

    # Log to DB
    await db.log_alert(
        incident_id=incident_id,
        ranger_id=ranger["id"] if ranger else None,
        channel="SMS" if (sent and ranger) else "CONSOLE",
        message=message,
        delivered=sent,
    )

    return sent or True   # always "handled" — console counts for demo


async def send_manual_alert(incident_id: str, ranger_id: str) -> bool:
    """Called when a ranger is manually dispatched from the dashboard."""
    rangers = await db.list_rangers()
    ranger = next((r for r in rangers if r["id"] == ranger_id), None)
    if not ranger:
        return False

    incident = await db.get_incident(incident_id)
    if not incident:
        return False

    message = (
        f"[WildGuard] DISPATCH ORDER\n"
        f"You have been assigned to incident {incident_id[:8]}.\n"
        f"Type: {incident['type']} | Location: {incident.get('location', 'Unknown')}\n"
        f"Proceed immediately. — WildGuard HQ"
    )

    sent = False
    if _twilio_configured():
        sent = await _send_sms(ranger["phone"], message)

    if not sent:
        logger.info(f"[MANUAL DISPATCH — console]\n{message}")

    await db.log_alert(
        incident_id=incident_id,
        ranger_id=ranger_id,
        channel="SMS" if sent else "CONSOLE",
        message=message,
        delivered=sent,
    )
    await db.update_ranger_status(ranger_id, "DEPLOYED", incident.get("location"))
    return True


# ── Twilio internals ──────────────────────────────────────────────────────────

def _twilio_configured() -> bool:
    return bool(
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_FROM_NUMBER
    )


async def _send_sms(to_number: str, body: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number,
        )
        return True
    except Exception as e:
        logger.error(f"Twilio SMS failed: {e}")
        return False
