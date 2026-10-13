"""
Layer 2: Magic-Byte / Header Analysis
Analyzes the first 8-16 bytes of the file.
Detects match against registered magic bytes and flags manipulated/corrupted magic bytes.
"""

from typing import Dict, Any, Optional
from backend.config import MAGIC_SIGNATURES

class MagicHeaderAnalyzer:
    @classmethod
    def analyze(cls, file_bytes: bytes) -> Dict[str, Any]:
        header_16 = file_bytes[:16]
        header_hex = header_16.hex()
        
        detected_type = "UNKNOWN"
        magic_match = False
        match_confidence = 0.0

        for fmt, sigs in MAGIC_SIGNATURES.items():
            for sig in sigs:
                if file_bytes.startswith(sig):
                    detected_type = fmt
                    magic_match = True
                    match_confidence = 1.0
                    break
            if magic_match:
                break

        # Check for partial or corrupted header signatures
        corrupted_header = False
        suspected_spoof_type = None

        if not magic_match:
            # Check if PDF header is offset by junk bytes (e.g., prepended bytes)
            if b"%PDF-" in file_bytes[:512]:
                corrupted_header = True
                suspected_spoof_type = "PDF"
                match_confidence = 0.7
            elif b"PK\x03\x04" in file_bytes[:512]:
                corrupted_header = True
                suspected_spoof_type = "ZIP"
                match_confidence = 0.7
            elif b"MZ" in file_bytes[:512]:
                corrupted_header = True
                suspected_spoof_type = "PE_EXE"
                match_confidence = 0.85

        return {
            "header_bytes_hex": header_hex,
            "detected_header_type": detected_type,
            "magic_match": magic_match,
            "match_confidence": match_confidence,
            "corrupted_header_detected": corrupted_header,
            "suspected_offset_header_type": suspected_spoof_type,
            "first_byte_zero": len(file_bytes) > 0 and file_bytes[0] == 0
        }
