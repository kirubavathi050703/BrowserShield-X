"""
Adversarial Robustness Test Suite
Evaluates detector performance when file signatures and structures are maliciously manipulated.
"""

from typing import Dict, Any, List
from backend.adversarial.generator import AdversarialGenerator
from backend.scanner.core_scanner import MultiLayerScanner
from backend.feature_extractor.extractor import FeatureExtractor
from backend.rules.rule_engine import RuleEngine
from backend.ml.pipeline import ml_pipeline_instance
from backend.risk_engine.scorer import RiskScorer

class RobustnessSuite:
    @classmethod
    def evaluate_robustness(cls) -> Dict[str, Any]:
        samples = AdversarialGenerator.generate_adversarial_samples()
        results = []
        
        detected_attacks = 0
        total_attacks = 0

        for sample in samples:
            filename = sample["name"]
            raw_bytes = sample["bytes"]
            attack_type = sample["attack_type"]
            is_benign = (attack_type == "none_benign")

            scan_res = MultiLayerScanner.scan_file_bytes(raw_bytes, filename)
            features = FeatureExtractor.extract_features(scan_res)
            reasons, rule_score = RuleEngine.evaluate(scan_res)
            ml_prob, conf, _ = ml_pipeline_instance.predict_probability(features)
            risk_score, category, decision, breakdown = RiskScorer.calculate_risk(scan_res, rule_score, ml_prob)

            if not is_benign:
                total_attacks += 1
                if decision in ["BLOCK", "QUARANTINE", "REVIEW"]:
                    detected_attacks += 1

            results.append({
                "filename": filename,
                "attack_type": attack_type,
                "declared_ext": sample["declared_ext"],
                "detected_type": scan_res["detected_type"],
                "risk_score": risk_score,
                "category": category,
                "decision": decision,
                "correctly_flagged": (decision in ["BLOCK", "QUARANTINE", "REVIEW"]) if not is_benign else (decision == "ALLOW"),
                "reasons": reasons
            })

        robustness_rate = (detected_attacks / total_attacks * 100.0) if total_attacks > 0 else 100.0

        return {
            "robustness_score_pct": round(robustness_rate, 2),
            "total_adversarial_samples": total_attacks,
            "detected_adversarial_samples": detected_attacks,
            "test_cases": results
        }
