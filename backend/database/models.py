"""
Database models and schema definitions for SQLite persistence.
"""

from dataclasses import dataclass, asdict
from typing import Optional, List
import json
import datetime

@dataclass
class ScanHistoryRecord:
    id: Optional[int]
    timestamp: str
    filename: str
    file_size_bytes: int
    declared_extension: str
    detected_mime: str
    detected_type: str
    risk_score: float
    risk_category: str
    decision: str
    confidence: float
    reasons_json: str
    features_json: str
    sha256_hash: str
    scanned_from: str  # 'manual_upload', 'watcher', 'test_suite'

    def to_dict(self):
        d = asdict(self)
        d['reasons'] = json.loads(self.reasons_json) if self.reasons_json else []
        d['features'] = json.loads(self.features_json) if self.features_json else {}
        return d

@dataclass
class QuarantineRecord:
    id: Optional[int]
    quarantine_id: str
    timestamp: str
    original_path: str
    quarantine_path: str
    filename: str
    declared_extension: str
    detected_type: str
    risk_score: float
    reasons_json: str
    sha256_hash: str
    status: str  # 'quarantined', 'restored', 'deleted'

    def to_dict(self):
        d = asdict(self)
        d['reasons'] = json.loads(self.reasons_json) if self.reasons_json else []
        return d

@dataclass
class SystemSettingRecord:
    key: str
    value_json: str
