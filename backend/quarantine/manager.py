"""
Quarantine Vault Manager
Isolates flagged files safely into quarantine storage.
Strips extension, appends .quarantined, computes SHA-256 hash, and maintains DB audit trail.
Provides secure restore and permanent deletion actions.
"""

import os
import shutil
import uuid
import datetime
import json
from pathlib import Path
from typing import Dict, Any, Optional

from backend.config import QUARANTINE_DIR
from backend.database.db import db_instance
from backend.database.models import QuarantineRecord

class QuarantineManager:
    @classmethod
    def quarantine_file(cls, file_bytes: bytes, original_filename: str, original_filepath: str, declared_ext: str, detected_type: str, risk_score: float, reasons: list, sha256_hash: str) -> Dict[str, Any]:
        quarantine_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Safe stored filename in vault: <quarantine_id>.quarantined
        target_name = f"{quarantine_id}.quarantined"
        target_path = Path(QUARANTINE_DIR) / target_name

        # Write file bytes to vault
        with open(target_path, "wb") as f:
            f.write(file_bytes)

        # Set read-only permissions on Windows/Linux
        try:
            os.chmod(target_path, 0o400)
        except Exception:
            pass

        record = QuarantineRecord(
            id=None,
            quarantine_id=quarantine_id,
            timestamp=timestamp,
            original_path=original_filepath,
            quarantine_path=str(target_path),
            filename=original_filename,
            declared_extension=declared_ext,
            detected_type=detected_type,
            risk_score=risk_score,
            reasons_json=json.dumps(reasons),
            sha256_hash=sha256_hash,
            status="quarantined"
        )

        db_instance.insert_quarantine(record)
        return record.to_dict()

    @classmethod
    def restore_file(cls, quarantine_id: str, restore_dir: Optional[str] = None) -> bool:
        record = db_instance.get_quarantine_by_id(quarantine_id)
        if not record or record["status"] != "quarantined":
            return False

        q_path = Path(record["quarantine_path"])
        if not q_path.exists():
            return False

        target_dir = Path(restore_dir) if restore_dir else Path(record["original_path"]).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_path = target_dir / f"restored_{record['filename']}"

        # Make writable before copying
        try:
            os.chmod(q_path, 0o600)
        except Exception:
            pass

        shutil.copy2(q_path, dest_path)
        db_instance.update_quarantine_status(quarantine_id, "restored")
        return True

    @classmethod
    def delete_file(cls, quarantine_id: str) -> bool:
        record = db_instance.get_quarantine_by_id(quarantine_id)
        if not record:
            return False

        q_path = Path(record["quarantine_path"])
        if q_path.exists():
            try:
                os.chmod(q_path, 0o600)
                os.remove(q_path)
            except Exception:
                pass

        db_instance.update_quarantine_status(quarantine_id, "deleted")
        return True
