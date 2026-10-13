"""
Explainable AI (XAI) Module
Provides SHAP values and feature attributions for model predictions.
Generates top influential feature breakdowns for every scanned file.
"""

import numpy as np
from typing import Dict, Any, List
from backend.feature_extractor.extractor import FeatureExtractor
from backend.ml.pipeline import ml_pipeline_instance

class ExplainabilityEngine:
    @classmethod
    def get_feature_contributions(cls, feature_vector: List[float]) -> List[Dict[str, Any]]:
        names = FeatureExtractor.FEATURE_NAMES
        vals = feature_vector
        rf = ml_pipeline_instance.rf_model

        # Calculate approximate SHAP / Feature importances
        if hasattr(rf, "feature_importances_") and len(rf.feature_importances_) == len(names):
            importances = rf.feature_importances_
        else:
            importances = np.ones(len(names)) / len(names)

        # Scale importances by actual feature value magnitude
        contributions = []
        for name, val, imp in zip(names, vals, importances):
            impact = val * imp
            contributions.append({
                "feature": name,
                "value": round(float(val), 4),
                "importance": round(float(imp), 4),
                "impact_score": round(float(impact), 4)
            })

        # Sort by highest absolute impact score
        contributions.sort(key=lambda x: abs(x["impact_score"]), reverse=True)
        return contributions[:8] # Top 8 most influential features

    @classmethod
    def generate_explanation_report(cls, scan_result: Dict[str, Any], risk_score: float, decision: str, reasons: List[str], feature_vector: List[float]) -> Dict[str, Any]:
        top_features = cls.get_feature_contributions(feature_vector)
        
        l1 = scan_result["layer1_extension"]
        l4 = scan_result["layer4_mime"]
        
        declared = l1["declared_extension"]
        detected = scan_result["detected_type"]

        summary = ""
        if decision in ["BLOCK", "QUARANTINE"]:
            summary = f"The file claims to be a {declared.upper()} but binary structure and content analysis identify it as {detected}. {len(reasons)} security anomaly flags were raised."
        elif decision == "REVIEW":
            summary = f"The file claims to be a {declared.upper()}. Content analysis detected potential structural inconsistencies requiring manual verification."
        else:
            summary = f"The file's declared extension ({declared}) matches its binary structure, magic bytes, and MIME signatures cleanly."

        return {
            "summary": summary,
            "decision": decision,
            "risk_score": risk_score,
            "reasons": reasons,
            "top_influential_features": top_features
        }
