"""
Unit tests for 42-dimensional feature extraction.
"""

import pytest
from backend.scanner.core_scanner import MultiLayerScanner
from backend.feature_extractor.extractor import FeatureExtractor

def test_feature_extractor():
    raw_bytes = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\ntrailer\n%%EOF\n"
    scan_res = MultiLayerScanner.scan_file_bytes(raw_bytes, "test.pdf")
    features = FeatureExtractor.extract_features(scan_res)
    
    assert len(features) == 42
    assert all(isinstance(x, (int, float)) for x in features)
    assert not any(x != x for x in features) # No NaNs
