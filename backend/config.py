"""
BrowserShield-X Configuration System
Defines system thresholds, risk engine weights, directory paths, and detection constants.
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
QUARANTINE_DIR = PROJECT_ROOT / "quarantine_vault"
DOWNLOADS_WATCH_DIR = PROJECT_ROOT / "test_downloads"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, QUARANTINE_DIR, DOWNLOADS_WATCH_DIR, EXPERIMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Config
DATABASE_PATH = DATA_DIR / "browsershield_x.db"

# Risk Scoring Engine Thresholds & Categories
RISK_THRESHOLDS = {
    "LOW": (0, 29),       # Decision: ALLOW
    "MEDIUM": (30, 59),   # Decision: REVIEW
    "HIGH": (60, 79),     # Decision: BLOCK / QUARANTINE
    "CRITICAL": (80, 100) # Decision: BLOCK / QUARANTINE
}

# Dynamic Risk Score Fusion Weights (Default - Configurable via Settings API)
# Sum of weights must equal 1.0
DEFAULT_RISK_WEIGHTS = {
    "rule_engine": 0.35,        # Deterministic rule findings
    "ml_prediction": 0.35,     # Machine learning probability
    "structural_anomaly": 0.15, # Deep structural violations
    "mime_mismatch": 0.15       # Extension vs MIME discrepancy
}

# Supported Ext / Magic Signature Mapping
MAGIC_SIGNATURES = {
    "PDF": [b"%PDF-"],
    "PNG": [b"\x89PNG\r\n\x1a\n"],
    "JPEG": [b"\xff\xd8\xff"],
    "GIF": [b"GIF87a", b"GIF89a"],
    "ZIP": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
    "DOCX": [b"PK\x03\x04"],
    "XLSX": [b"PK\x03\x04"],
    "PPTX": [b"PK\x03\x04"],
    "PE_EXE": [b"MZ"],
    "ELF": [b"\x7fELF"],
    "GZIP": [b"\x1f\x8b"]
}

# Footer Signatures
FOOTER_SIGNATURES = {
    "PDF": [b"%%EOF"],
    "PNG": [b"IEND\xaeB`\x82"],
    "JPEG": [b"\xff\xd9"],
    "ZIP": [b"PK\x05\x06"] # End of Central Directory
}

# MIME Types Registry
EXPECTED_MIMES = {
    ".pdf": ["application/pdf"],
    ".png": ["image/png"],
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".gif": ["image/gif"],
    ".zip": ["application/zip", "application/x-zip-compressed"],
    ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    ".xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    ".pptx": ["application/vnd.openxmlformats-officedocument.presentationml.presentation"],
    ".exe": ["application/x-msdownload", "application/x-dosexec", "application/pe-executable"],
    ".dll": ["application/x-msdownload", "application/x-dosexec"],
    ".elf": ["application/x-executable", "application/x-elf"],
}

# Temporary download extensions to ignore in Point-of-Download watcher
TRANSIENT_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download", ".opdownload"}
