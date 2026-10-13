"""
Feature Extractor Module
Converts raw file bytes and multi-layer scanner outputs into a 42-dimensional numerical feature vector.
"""

import math
import numpy as np
from typing import Dict, Any, List

class FeatureExtractor:
    FEATURE_NAMES = [
        "file_size", "log_file_size", "global_entropy", "head_entropy", "body_entropy",
        "tail_entropy", "min_block_entropy", "max_block_entropy", "block_entropy_variance",
        "is_high_entropy_packed", "magic_match", "match_confidence", "corrupted_header_detected",
        "first_byte_zero", "footer_match", "footer_confidence", "header_footer_consistent",
        "is_mime_mismatch", "zero_byte_ratio", "printable_ascii_ratio", "high_bit_ratio",
        "byte_mean", "byte_std", "chi_square_uniformity",
        "hist_bin_0", "hist_bin_1", "hist_bin_2", "hist_bin_3",
        "hist_bin_4", "hist_bin_5", "hist_bin_6", "hist_bin_7",
        "hist_bin_8", "hist_bin_9", "hist_bin_10", "hist_bin_11",
        "hist_bin_12", "hist_bin_13", "hist_bin_14", "hist_bin_15",
        "has_double_extension", "total_structural_anomalies"
    ]

    @classmethod
    def extract_features(cls, scan_result: Dict[str, Any]) -> List[float]:
        l1 = scan_result["layer1_extension"]
        l2 = scan_result["layer2_header"]
        l3 = scan_result["layer3_footer"]
        l4 = scan_result["layer4_mime"]
        l5 = scan_result["layer5_entropy"]
        l6 = scan_result["layer6_byte_dist"]
        l7 = scan_result["layer7_structure"]

        file_size = scan_result["file_size"]
        log_size = math.log10(file_size + 1)

        # Normalize 16-bin histogram
        hist_raw = l6.get("top_byte_histogram", [0] * 16)
        hist_norm = [(x / file_size) if file_size > 0 else 0.0 for x in hist_raw]

        vec = [
            float(file_size),
            float(log_size),
            float(l5.get("global_entropy", 0.0)),
            float(l5.get("head_entropy", 0.0)),
            float(l5.get("body_entropy", 0.0)),
            float(l5.get("tail_entropy", 0.0)),
            float(l5.get("min_block_entropy", 0.0)),
            float(l5.get("max_block_entropy", 0.0)),
            float(l5.get("block_entropy_variance", 0.0)),
            1.0 if l5.get("is_high_entropy_packed") else 0.0,
            1.0 if l2.get("magic_match") else 0.0,
            float(l2.get("match_confidence", 0.0)),
            1.0 if l2.get("corrupted_header_detected") else 0.0,
            1.0 if l2.get("first_byte_zero") else 0.0,
            1.0 if l3.get("footer_match") else 0.0,
            float(l3.get("footer_confidence", 0.0)),
            1.0 if l3.get("header_footer_consistent") else 0.0,
            1.0 if l4.get("is_mime_mismatch") else 0.0,
            float(l6.get("zero_byte_ratio", 0.0)),
            float(l6.get("printable_ascii_ratio", 0.0)),
            float(l6.get("high_bit_ratio", 0.0)),
            float(l6.get("byte_mean", 0.0)),
            float(l6.get("byte_std", 0.0)),
            float(l6.get("chi_square_uniformity", 0.0))
        ]

        vec.extend(hist_norm)
        vec.append(1.0 if l1.get("has_double_extension") else 0.0)
        vec.append(float(l7.get("total_structural_anomalies", 0)))

        return vec

    @classmethod
    def extract_numpy(cls, scan_result: Dict[str, Any]) -> np.ndarray:
        return np.array(cls.extract_features(scan_result), dtype=np.float32)
