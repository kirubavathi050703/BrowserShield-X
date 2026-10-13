"""
API Router for Quarantine Management
Provides listing, restoring, and deleting quarantined files.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from backend.database.db import db_instance
from backend.quarantine.manager import QuarantineManager

router = APIRouter(prefix="/api/quarantine", tags=["Quarantine Manager"])

@router.get("")
def get_quarantined_files():
    records = db_instance.get_quarantine_records()
    return {"total": len(records), "records": records}

@router.post("/{quarantine_id}/restore")
def restore_quarantined_file(quarantine_id: str, restore_dir: Optional[str] = Body(None, embed=True)):
    success = QuarantineManager.restore_file(quarantine_id, restore_dir=restore_dir)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to restore file. File might not exist or is already processed.")
    return {"status": "success", "message": f"File {quarantine_id} successfully restored."}

@router.delete("/{quarantine_id}")
def delete_quarantined_file(quarantine_id: str):
    success = QuarantineManager.delete_file(quarantine_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete file from quarantine vault.")
    return {"status": "success", "message": f"File {quarantine_id} permanently deleted."}
