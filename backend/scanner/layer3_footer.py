"""
Layer 3: Footer / Container End Verification
Implements format-aware footer detection. Does not assume footers are strictly literal last bytes;
searches backwards within tail buffer (e.g. End of Central Directory for ZIP/Office).
"""

from typing import Dict, Any
from backend.config import FOOTER_SIGNATURES

class FooterAnalyzer:
    TAIL_BUFFER_SIZE = 4096

    @classmethod
    def analyze(cls, file_bytes: bytes, detected_header_type: str) -> Dict[str, Any]:
        if not file_bytes:
            return {
                "footer_match": False,
                "detected_footer_type": "NONE",
                "tail_bytes_hex": "",
                "footer_confidence": 0.0
            }

        tail_bytes = file_bytes[-cls.TAIL_BUFFER_SIZE:] if len(file_bytes) > cls.TAIL_BUFFER_SIZE else file_bytes
        tail_hex = tail_bytes[-16:].hex()

        footer_match = False
        detected_footer = "NONE"
        confidence = 0.0

        # PDF Footer: %%EOF
        if b"%%EOF" in tail_bytes:
            footer_match = True
            detected_footer = "PDF"
            confidence = 0.95
        # ZIP / Office Footer: End of Central Directory record (PK\x05\x06)
        elif b"PK\x05\x06" in tail_bytes:
            footer_match = True
            detected_footer = "ZIP"
            confidence = 0.95
        # PNG Footer: IEND chunk
        elif b"IEND" in tail_bytes:
            footer_match = True
            detected_footer = "PNG"
            confidence = 0.95
        # JPEG Footer: \xFF\xD9
        elif b"\xff\xd9" in tail_bytes:
            footer_match = True
            detected_footer = "JPEG"
            confidence = 0.90

        header_footer_consistent = (detected_header_type == detected_footer) if (detected_header_type != "UNKNOWN" and detected_footer != "NONE") else True

        return {
            "footer_match": footer_match,
            "detected_footer_type": detected_footer,
            "tail_bytes_hex": tail_hex,
            "footer_confidence": confidence,
            "header_footer_consistent": header_footer_consistent
        }
