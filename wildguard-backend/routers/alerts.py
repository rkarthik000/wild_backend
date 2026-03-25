"""
GET /api/alerts   — Recent alert log (shown in Rangers tab of dashboard)
"""

from fastapi import APIRouter, Query
from typing import List

from core import database as db

router = APIRouter()


@router.get("")
async def list_alerts(limit: int = Query(20, ge=1, le=100)):
    return await db.list_alerts(limit=limit)
