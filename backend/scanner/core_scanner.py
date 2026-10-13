"""
Core Multi-Layer Scanner Engine
Orchestrates Layers 1 through 7 to produce a consolidated scan report.
"""

from typing import Dict, Any
import hashlib
from backend.scanner.layer1_extension import ExtensionAnalyzer
from backend.scanner.layer2_magic_header import MagicHeaderAnalyzer
from backend.scanner.layer3_footer import FooterAnalyzer
from backend.scanner.layer4_mime import MimeAnalyzer
from backend.scanner.layer5_entropy import EntropyAnalyzer
from backend.scanner.layer6_byte_dist import ByteDistributionAnalyzer
from backend.scanner.layer7_structure import StructuralAnalyzer

class MultiLayerScanner:
    @classmethod
    def scan_file_bytes(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # Layer 1: Extension Normalization
        l1 = ExtensionAnalyzer.analyze(filename)
        declared_ext = l1["declared_extension"]

        # Layer 2: Magic-Byte Header Analysis
        l2 = MagicHeaderAnalyzer.analyze(file_bytes)
        header_type = l2["detected_header_type"]

        # Layer 3: Format-Aware Footer Verification
        l3 = FooterAnalyzer.analyze(file_bytes, header_type)

        # Layer 4: MIME Discrepancy Engine
        l4 = MimeAnalyzer.analyze(file_bytes, declared_ext, header_type)

        # Layer 5: Shannon Entropy Breakdown
        l5 = EntropyAnalyzer.analyze(file_bytes)

        # Layer 6: Byte Frequency Distribution
        l6 = ByteDistributionAnalyzer.analyze(file_bytes)

        # Layer 7: Deep Format Structural Parsing
        l7 = StructuralAnalyzer.analyze(file_bytes, declared_ext, header_type)

        # Consolidated Detection Result
        detected_type = header_type
        if detected_type == "UNKNOWN" and l3["detected_footer_type"] != "NONE":
            detected_type = l3["detected_footer_type"]
        if detected_type == "ZIP" and l7.get("zip_office_structure") and l7["zip_office_structure"].get("is_valid_office"):
            detected_type = declared_ext.replace(".", "").upper()

        return {
            "filename": filename,
            "file_size": file_size,
            "sha256": sha256,
            "declared_extension": declared_ext,
            "detected_type": detected_type,
            "layer1_extension": l1,
            "layer2_header": l2,
            "layer3_footer": l3,
            "layer4_mime": l4,
            "layer5_entropy": l5,
            "layer6_byte_dist": l6,
            "layer7_structure": l7
        }
