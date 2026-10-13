"""
Layer 1: Extension Analysis & Normalization
Extracts and normalizes declared file extension.
Detects potential extension spoofing tricks such as double extensions (.pdf.exe) or hidden extensions.
"""

from pathlib import Path
from typing import Dict, Any, List

class ExtensionAnalyzer:
    DOUBLE_EXT_TARGETS = {".exe", ".bat", ".cmd", ".vbs", ".js", ".ps1", ".scr", ".dll"}

    @classmethod
    def analyze(cls, filename: str) -> Dict[str, Any]:
        p = Path(filename)
        raw_ext = p.suffix.lower()
        parts = [part.lower() for part in filename.split(".") if part]
        
        has_double_ext = False
        secondary_ext = ""
        declared_ext = raw_ext

        if len(parts) > 2:
            # Check for tricks like invoice.pdf.exe or report.docx.scr
            last_ext = "." + parts[-1]
            penultimate_ext = "." + parts[-2]
            if last_ext in cls.DOUBLE_EXT_TARGETS:
                has_double_ext = True
                secondary_ext = penultimate_ext
                declared_ext = last_ext

        if not declared_ext and len(parts) > 1:
            declared_ext = "." + parts[-1]

        return {
            "declared_extension": declared_ext if declared_ext else ".unknown",
            "raw_filename": filename,
            "has_double_extension": has_double_ext,
            "secondary_extension": secondary_ext,
            "is_known_extension": declared_ext in [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".docx", ".xlsx", ".pptx", ".exe", ".dll", ".elf"]
        }
