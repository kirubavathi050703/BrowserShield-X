"""
Synthetic Adversarial Sample Generator
Creates adversarial test samples to evaluate detector robustness under signature manipulation.
"""

import os
from typing import Dict, Any, List, Tuple

class AdversarialGenerator:
    @classmethod
    def generate_adversarial_samples(cls) -> List[Dict[str, Any]]:
        samples = []

        # Sample 1: PE Executable with PDF Extension (Extension Spoof)
        pe_bytes = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + (b"\x00" * 60) + b"\x80\x00\x00\x00" + (b"\x00" * 64) + b"PE\x00\x00" + (b"X" * 200)
        samples.append({
            "name": "invoice_malicious.pdf",
            "bytes": pe_bytes,
            "declared_ext": ".pdf",
            "true_type": "PE_EXE",
            "attack_type": "extension_spoofing"
        })

        # Sample 2: PE Executable with Prepended Fake PDF Magic Bytes (Header Manipulation)
        fake_pdf_pe = b"%PDF-1.5\r\n" + pe_bytes
        samples.append({
            "name": "report_prepended.pdf",
            "bytes": fake_pdf_pe,
            "declared_ext": ".pdf",
            "true_type": "PE_EXE",
            "attack_type": "fake_header_prepended"
        })

        # Sample 3: Executable embedded in DOCX container with ZIP extension (Office Spoof)
        fake_office_exe = b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"[Content_Types].xml" + b"MZ\x90\x00" + b"PK\x05\x06" + (b"\x00" * 18)
        samples.append({
            "name": "document_embedded_payload.docx",
            "bytes": fake_office_exe,
            "declared_ext": ".docx",
            "true_type": "SUSPICIOUS_CONTAINER",
            "attack_type": "embedded_executable_archive"
        })

        # Sample 4: PNG Image with Corrupted Header + PE Body (Image Spoof)
        tampered_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20 + b"MZ\x90\x00" + b"PE\x00\x00" + b"IEND\xaeB`\x82"
        samples.append({
            "name": "photo_tampered.png",
            "bytes": tampered_png,
            "declared_ext": ".png",
            "true_type": "PE_EXE",
            "attack_type": "corrupted_magic_body_payload"
        })

        # Sample 5: Unknown file format with PDF magic bytes inserted (Unknown Type Spoof)
        unknown_sample = b"%PDF-1.7\n1 0 obj<<>>endobj\ntrailer<<>>" + (b"\xff\x00\xaa" * 100)
        samples.append({
            "name": "unknown_file.xyz",
            "bytes": unknown_sample,
            "declared_ext": ".xyz",
            "true_type": "CORRUPTED_PDF",
            "attack_type": "unknown_extension_spoof"
        })

        # Sample 6: Valid Benign PDF
        benign_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
        samples.append({
            "name": "legitimate_document.pdf",
            "bytes": benign_pdf,
            "declared_ext": ".pdf",
            "true_type": "PDF",
            "attack_type": "none_benign"
        })

        return samples
