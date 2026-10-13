"""
API Router for Scan History & Security Reports
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from backend.database.db import db_instance

router = APIRouter(prefix="/api/history", tags=["History & Reports"])

@router.get("")
def get_scan_history(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    scans = db_instance.get_scans(limit=limit, offset=offset)
    return {"total": len(scans), "scans": scans}

@router.get("/{scan_id}")
def get_scan_report(scan_id: int):
    scan = db_instance.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan ID {scan_id} not found.")
    return scan
