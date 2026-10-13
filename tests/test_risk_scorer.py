"""
Unit tests for Risk Scoring Engine.
"""

import pytest
from backend.scanner.core_scanner import MultiLayerScanner
from backend.risk_engine.scorer import RiskScorer

def test_risk_scorer():
    pe_disguised_as_pdf = b"MZ\x90\x00\x03\x00" + (b"\x00" * 60) + b"\x80\x00\x00\x00" + (b"\x00" * 64) + b"PE\x00\x00"
    scan_res = MultiLayerScanner.scan_file_bytes(pe_disguised_as_pdf, "invoice.pdf")
    
    score, category, decision, breakdown = RiskScorer.calculate_risk(scan_res, rule_score=0.9, ml_probability=0.95)
    
    assert 0.0 <= score <= 100.0
    assert category in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert decision in ["ALLOW", "REVIEW", "BLOCK"]
    assert score >= 60.0 # High risk expected for PE disguised as PDF!
