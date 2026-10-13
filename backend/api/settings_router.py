"""
API Router for System Settings & Risk Weight Configuration
"""

from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from backend.config import DEFAULT_RISK_WEIGHTS
from backend.database.db import db_instance

router = APIRouter(prefix="/api/settings", tags=["System Settings"])

@router.get("")
def get_system_settings():
    weights = db_instance.get_setting("risk_weights", DEFAULT_RISK_WEIGHTS)
    return {
        "risk_weights": weights,
        "default_risk_weights": DEFAULT_RISK_WEIGHTS
    }

@router.post("/risk-weights")
def update_risk_weights(weights: Dict[str, float] = Body(...)):
    required_keys = {"rule_engine", "ml_prediction", "structural_anomaly", "mime_mismatch"}
    if not required_keys.issubset(weights.keys()):
        raise HTTPException(status_code=400, detail=f"Missing required weight keys: {required_keys}")

    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        raise HTTPException(status_code=400, detail=f"Sum of weights must equal 1.0 (current sum: {total:.2f})")

    db_instance.set_setting("risk_weights", weights)
    return {"status": "success", "message": "Risk weights updated successfully.", "risk_weights": weights}
