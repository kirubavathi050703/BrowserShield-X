"""
Unit tests for Scanner Layers 1 through 7.
"""

import pytest
from backend.scanner.core_scanner import MultiLayerScanner
from backend.scanner.layer1_extension import ExtensionAnalyzer
from backend.scanner.layer2_magic_header import MagicHeaderAnalyzer
from backend.scanner.layer3_footer import FooterAnalyzer
from backend.scanner.layer4_mime import MimeAnalyzer
from backend.scanner.layer5_entropy import EntropyAnalyzer
from backend.scanner.layer6_byte_dist import ByteDistributionAnalyzer
from backend.scanner.layer7_structure import StructuralAnalyzer

def test_layer1_extension():
    res1 = ExtensionAnalyzer.analyze("invoice.pdf.exe")
    assert res1["has_double_extension"] is True
    assert res1["declared_extension"] == ".exe"

    res2 = ExtensionAnalyzer.analyze("document.pdf")
    assert res2["has_double_extension"] is False
    assert res2["declared_extension"] == ".pdf"

def test_layer2_magic_header():
    pdf_bytes = b"%PDF-1.5\r\n" + (b"\x00" * 100)
    res = MagicHeaderAnalyzer.analyze(pdf_bytes)
    assert res["magic_match"] is True
    assert res["detected_header_type"] == "PDF"

    tampered_bytes = b"MZ\x90\x00" + b"%PDF-1.5"
    res_tampered = MagicHeaderAnalyzer.analyze(tampered_bytes)
    assert res_tampered["detected_header_type"] == "PE_EXE"

def test_layer3_footer():
    pdf_tail = b"1 0 obj\nendobj\ntrailer\n%%EOF\n"
    res = FooterAnalyzer.analyze(pdf_tail, "PDF")
    assert res["footer_match"] is True
    assert res["detected_footer_type"] == "PDF"

def test_layer4_mime():
    res = MimeAnalyzer.analyze(b"MZ\x90\x00", ".pdf", "PE_EXE")
    assert res["is_mime_mismatch"] is True
    assert res["mismatch_severity"] == "CRITICAL"

def test_layer5_entropy():
    uniform_bytes = bytes([i % 256 for i in range(1024)])
    res = EntropyAnalyzer.analyze(uniform_bytes)
    assert res["global_entropy"] > 7.9

def test_layer6_byte_dist():
    data = b"\x00" * 100 + b"A" * 100
    res = ByteDistributionAnalyzer.analyze(data)
    assert res["zero_byte_ratio"] == 0.5
    assert res["printable_ascii_ratio"] == 0.5

def test_layer7_structure():
    pdf_bytes = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\ntrailer\n%%EOF\n"
    res = StructuralAnalyzer.analyze_pdf(pdf_bytes)
    assert res["valid_structure"] is True
    assert res["has_pdf_header"] is True

def test_full_core_scanner():
    pdf_bytes = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\ntrailer\n%%EOF\n"
    res = MultiLayerScanner.scan_file_bytes(pdf_bytes, "valid_report.pdf")
    assert res["declared_extension"] == ".pdf"
    assert res["detected_type"] == "PDF"
