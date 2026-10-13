"""
Layer 4: MIME / Content Type Analysis
Determines actual MIME type from file content and evaluates consistency against declared extension.
"""

import mimetypes
from typing import Dict, Any, List
from backend.config import EXPECTED_MIMES

class MimeAnalyzer:
    @classmethod
    def analyze(cls, file_bytes: bytes, declared_ext: str, header_type: str) -> Dict[str, Any]:
        declared_mime = mimetypes.guess_type("file" + declared_ext)[0] or "application/octet-stream"
        
        # Derive actual detected MIME from binary header analysis
        detected_mime = "application/octet-stream"
        if header_type == "PDF":
            detected_mime = "application/pdf"
        elif header_type == "PNG":
            detected_mime = "image/png"
        elif header_type == "JPEG":
            detected_mime = "image/jpeg"
        elif header_type == "GIF":
            detected_mime = "image/gif"
        elif header_type == "ZIP":
            if declared_ext == ".docx":
                detected_mime = EXPECTED_MIMES[".docx"][0]
            elif declared_ext == ".xlsx":
                detected_mime = EXPECTED_MIMES[".xlsx"][0]
            elif declared_ext == ".pptx":
                detected_mime = EXPECTED_MIMES[".pptx"][0]
            else:
                detected_mime = "application/zip"
        elif header_type == "PE_EXE":
            detected_mime = "application/x-msdownload"
        elif header_type == "ELF":
            detected_mime = "application/x-executable"

        # Compare against expected MIME list for the extension
        expected_list = EXPECTED_MIMES.get(declared_ext.lower(), [])
        
        is_mismatch = False
        mismatch_severity = "NONE"

        if expected_list:
            if detected_mime not in expected_list:
                is_mismatch = True
                if detected_mime in ["application/x-msdownload", "application/x-executable"]:
                    mismatch_severity = "CRITICAL"  # Executable disguised as document/image!
                else:
                    mismatch_severity = "HIGH"

        return {
            "declared_mime": declared_mime,
            "detected_mime": detected_mime,
            "is_mime_mismatch": is_mismatch,
            "mismatch_severity": mismatch_severity,
            "expected_mimes_for_extension": expected_list
        }
