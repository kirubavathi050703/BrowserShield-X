"""
API Router for File Scanning
Handles single file upload scans, path scans, and detailed security report generation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import Dict, Any, Optional
import datetime
import json

from backend.scanner.core_scanner import MultiLayerScanner
from backend.feature_extractor.extractor import FeatureExtractor
from backend.rules.rule_engine import RuleEngine
from backend.ml.pipeline import ml_pipeline_instance
from backend.risk_engine.scorer import RiskScorer
from backend.explainability.explainer import ExplainabilityEngine
from backend.quarantine.manager import QuarantineManager
from backend.database.db import db_instance
from backend.database.models import ScanHistoryRecord

router = APIRouter(prefix="/api/scan", tags=["Scan Engine"])

@router.post("/file")
async def scan_uploaded_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown_file"
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    scan_res = MultiLayerScanner.scan_file_bytes(file_bytes, filename)
    features = FeatureExtractor.extract_features(scan_res)
    reasons, rule_score = RuleEngine.evaluate(scan_res)
    ml_prob, confidence, model_used = ml_pipeline_instance.predict_probability(features)
    risk_score, category, decision, breakdown = RiskScorer.calculate_risk(scan_res, rule_score, ml_prob)
    
    explanation = ExplainabilityEngine.generate_explanation_report(
        scan_res, risk_score, decision, reasons, features
    )

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Log into Database
    record = ScanHistoryRecord(
        id=None,
        timestamp=timestamp,
        filename=filename,
        file_size_bytes=len(file_bytes),
        declared_extension=scan_res["declared_extension"],
        detected_mime=scan_res["layer4_mime"]["detected_mime"],
        detected_type=scan_res["detected_type"],
        risk_score=risk_score,
        risk_category=category,
        decision=decision,
        confidence=confidence,
        reasons_json=json.dumps(reasons),
        features_json=json.dumps(features),
        sha256_hash=scan_res["sha256"],
        scanned_from="manual_upload"
    )
    scan_id = db_instance.insert_scan(record)

    quarantine_info = None
    if decision in ["BLOCK", "QUARANTINE"]:
        quarantine_info = QuarantineManager.quarantine_file(
            file_bytes=file_bytes,
            original_filename=filename,
            original_filepath=f"/uploads/{filename}",
            declared_ext=scan_res["declared_extension"],
            detected_type=scan_res["detected_type"],
            risk_score=risk_score,
            reasons=reasons,
            sha256_hash=scan_res["sha256"]
        )

    return {
        "scan_id": scan_id,
        "filename": filename,
        "file_size": len(file_bytes),
        "sha256": scan_res["sha256"],
        "declared_extension": scan_res["declared_extension"],
        "detected_type": scan_res["detected_type"],
        "detected_mime": scan_res["layer4_mime"]["detected_mime"],
        "risk_score": risk_score,
        "risk_category": category,
        "decision": decision,
        "ml_probability": ml_prob,
        "ml_confidence": confidence,
        "model_used": model_used,
        "reasons": reasons,
        "risk_breakdown": breakdown,
        "explanation": explanation,
        "quarantine_info": quarantine_info,
        "multi_layer_details": scan_res
    }
