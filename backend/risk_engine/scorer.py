"""
Risk Engine Module
Computes multi-factor dynamic risk score R in [0, 100] using configurable weights.
Categorizes risk into LOW, MEDIUM, HIGH, CRITICAL and yields final decision (ALLOW, REVIEW, BLOCK).
"""

from typing import Dict, Any, Tuple, List
from backend.config import DEFAULT_RISK_WEIGHTS, RISK_THRESHOLDS
from backend.database.db import db_instance

class RiskScorer:
    @classmethod
    def calculate_risk(cls, scan_result: Dict[str, Any], rule_score: float, ml_probability: float) -> Tuple[float, str, str, Dict[str, float]]:
        # Fetch dynamic weights from DB settings or use defaults
        weights = db_instance.get_setting("risk_weights", DEFAULT_RISK_WEIGHTS)
        
        w_rule = weights.get("rule_engine", 0.35)
        w_ml = weights.get("ml_prediction", 0.35)
        w_struct = weights.get("structural_anomaly", 0.15)
        w_mime = weights.get("mime_mismatch", 0.15)

        l4 = scan_result["layer4_mime"]
        l7 = scan_result["layer7_structure"]

        # 1. MIME mismatch component (0.0 to 1.0)
        mime_score = 1.0 if l4.get("is_mime_mismatch") else 0.0
        if l4.get("mismatch_severity") == "CRITICAL":
            mime_score = 1.0
        elif l4.get("mismatch_severity") == "HIGH":
            mime_score = 0.8

        # 2. Structural anomaly component (0.0 to 1.0)
        anomaly_count = l7.get("total_structural_anomalies", 0)
        struct_score = min(anomaly_count * 0.35, 1.0)

        # 3. Weighted risk fusion
        raw_risk = (w_rule * rule_score) + (w_ml * ml_probability) + (w_struct * struct_score) + (w_mime * mime_score)
        
        # Scale to [0, 100]
        final_score = round(min(max(raw_risk * 100.0, 0.0), 100.0), 1)

        # Determine Category & Decision
        if final_score >= 80.0:
            category = "CRITICAL"
            decision = "BLOCK"
        elif final_score >= 60.0:
            category = "HIGH"
            decision = "BLOCK"
        elif final_score >= 30.0:
            category = "MEDIUM"
            decision = "REVIEW"
        else:
            category = "LOW"
            decision = "ALLOW"

        breakdown = {
            "rule_contribution": round(w_rule * rule_score * 100.0, 1),
            "ml_contribution": round(w_ml * ml_probability * 100.0, 1),
            "structural_contribution": round(w_struct * struct_score * 100.0, 1),
            "mime_contribution": round(w_mime * mime_score * 100.0, 1)
        }

        return final_score, category, decision, breakdown
