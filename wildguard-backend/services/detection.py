"""
Detection service.
• Uses YOLOv8 for object detection (humans, vehicles, weapons)
• Uses a HuggingFace image classifier for species identification
• Falls back to mock results when models aren't installed (great for demos)
"""

import io
import os
import logging
from typing import List, Optional, Tuple
from PIL import Image

from core.config import settings
from models.schemas import Detection, ThreatType, BoundingBox

logger = logging.getLogger(__name__)

# ── Label → ThreatType mapping (COCO + custom) ───────────────────────────────
LABEL_MAP = {
    "person":     ThreatType.POACHER,
    "human":      ThreatType.POACHER,
    "knife":      ThreatType.WEAPON,
    "gun":        ThreatType.WEAPON,
    "rifle":      ThreatType.WEAPON,
    "car":        ThreatType.VEHICLE,
    "truck":      ThreatType.VEHICLE,
    "motorcycle": ThreatType.VEHICLE,
    "elephant":   ThreatType.SPECIES_SPOTTED,
    "rhino":      ThreatType.SPECIES_SPOTTED,
    "lion":       ThreatType.SPECIES_SPOTTED,
    "giraffe":    ThreatType.SPECIES_SPOTTED,
    "zebra":      ThreatType.SPECIES_SPOTTED,
    "bear":       ThreatType.ANIMAL_DISTRESS,
}

WILDLIFE_LABELS = {
    "elephant", "rhino", "lion", "giraffe", "zebra", "leopard",
    "cheetah", "buffalo", "hippo", "crocodile",
}

# ── Model singletons (lazy-loaded) ───────────────────────────────────────────
_yolo_model = None
_species_pipeline = None
_models_available = False


def _load_models():
    global _yolo_model, _species_pipeline, _models_available
    if _yolo_model is not None:
        return

    try:
        from ultralytics import YOLO
        _yolo_model = YOLO(settings.YOLO_MODEL)
        logger.info(f"YOLOv8 loaded: {settings.YOLO_MODEL}")
    except Exception as e:
        logger.warning(f"YOLOv8 not available ({e}) — using mock detections")
        _yolo_model = None

    try:
        from transformers import pipeline
        _species_pipeline = pipeline(
            "image-classification",
            model=settings.SPECIES_MODEL,
            top_k=3,
        )
        logger.info("Species classifier loaded")
    except Exception as e:
        logger.warning(f"Species classifier not available ({e})")
        _species_pipeline = None

    _models_available = _yolo_model is not None


# ── Public API ────────────────────────────────────────────────────────────────

async def run_detection(image_bytes: bytes) -> Tuple[List[Detection], Optional[str]]:
    """
    Returns (detections, detected_species_name | None).
    If models aren't installed, returns plausible mock results for demo.
    """
    _load_models()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if _models_available:
        detections = _run_yolo(image, image_bytes)
        species = _run_species_classifier(image, detections)
    else:
        detections, species = _mock_detections()

    return detections, species


def _run_yolo(image: Image.Image, image_bytes: bytes) -> List[Detection]:
    results = _yolo_model(image, conf=settings.CONFIDENCE_THRESHOLD)
    detections = []
    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            conf  = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            threat_type = LABEL_MAP.get(label.lower(), ThreatType.UNKNOWN)
            detections.append(Detection(
                label=label,
                confidence=round(conf, 3),
                bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                threat_type=threat_type,
            ))
    return detections


def _run_species_classifier(image: Image.Image, detections: List[Detection]) -> Optional[str]:
    if _species_pipeline is None:
        return None
    # Only run if a wildlife detection was found
    has_wildlife = any(d.threat_type == ThreatType.SPECIES_SPOTTED for d in detections)
    if not has_wildlife:
        return None
    try:
        preds = _species_pipeline(image)
        for pred in preds:
            label = pred["label"].lower()
            if any(w in label for w in WILDLIFE_LABELS):
                return pred["label"].title()
    except Exception as e:
        logger.warning(f"Species classification failed: {e}")
    return None


def _mock_detections() -> Tuple[List[Detection], Optional[str]]:
    """
    Returns a realistic mock result for demos when YOLOv8 isn't installed.
    Randomly picks from a few scenarios.
    """
    import random
    scenario = random.choice(["poacher", "vehicle", "elephant", "rhino"])

    if scenario == "poacher":
        return [Detection(
            label="person", confidence=0.94,
            bbox=BoundingBox(x1=120, y1=80, x2=280, y2=460),
            threat_type=ThreatType.POACHER,
        )], None

    if scenario == "vehicle":
        return [Detection(
            label="truck", confidence=0.87,
            bbox=BoundingBox(x1=50, y1=200, x2=500, y2=420),
            threat_type=ThreatType.VEHICLE,
        )], None

    if scenario == "elephant":
        return [Detection(
            label="elephant", confidence=0.99,
            bbox=BoundingBox(x1=30, y1=60, x2=600, y2=480),
            threat_type=ThreatType.SPECIES_SPOTTED,
        )], "African Elephant"

    # rhino
    return [Detection(
        label="rhino", confidence=0.96,
        bbox=BoundingBox(x1=100, y1=150, x2=540, y2=430),
        threat_type=ThreatType.SPECIES_SPOTTED,
    )], "Black Rhinoceros"


def get_top_threat(detections: List[Detection]) -> Tuple[Optional[ThreatType], float]:
    """Returns the highest-priority threat type and its confidence."""
    priority = [
        ThreatType.WEAPON,
        ThreatType.POACHER,
        ThreatType.VEHICLE,
        ThreatType.ANIMAL_DISTRESS,
        ThreatType.SPECIES_SPOTTED,
    ]
    for threat in priority:
        matches = [d for d in detections if d.threat_type == threat]
        if matches:
            best = max(matches, key=lambda d: d.confidence)
            return threat, best.confidence
    return None, 0.0
