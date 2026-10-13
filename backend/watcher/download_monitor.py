"""
Point-of-Download Watcher Service
Monitors downloads directory using watchdog.
Ignores transient download extensions (.crdownload, .part, .tmp).
Automatically triggers multi-layer scan and auto-quarantines high-risk files upon download completion.
"""

import os
import time
import datetime
import json
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from backend.config import DOWNLOADS_WATCH_DIR, TRANSIENT_EXTENSIONS
from backend.scanner.core_scanner import MultiLayerScanner
from backend.feature_extractor.extractor import FeatureExtractor
from backend.rules.rule_engine import RuleEngine
from backend.ml.pipeline import ml_pipeline_instance
from backend.risk_engine.scorer import RiskScorer
from backend.quarantine.manager import QuarantineManager
from backend.database.db import db_instance
from backend.database.models import ScanHistoryRecord

class DownloadFileHandler(FileSystemEventHandler):
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir

    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)

    def _handle_event(self, filepath: str):
        p = Path(filepath)
        ext = p.suffix.lower()

        # Ignore transient download files
        if ext in TRANSIENT_EXTENSIONS:
            return

        # Ensure file is completely written & stable
        if not self._wait_for_file_stability(filepath):
            return

        # Perform Scan
        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()

            if len(file_bytes) == 0:
                return

            scan_res = MultiLayerScanner.scan_file_bytes(file_bytes, p.name)
            features = FeatureExtractor.extract_features(scan_res)
            reasons, rule_score = RuleEngine.evaluate(scan_res)
            ml_prob, confidence, model_used = ml_pipeline_instance.predict_probability(features)
            risk_score, category, decision, breakdown = RiskScorer.calculate_risk(scan_res, rule_score, ml_prob)

            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Save Scan Record to DB
            record = ScanHistoryRecord(
                id=None,
                timestamp=timestamp,
                filename=p.name,
                file_size_bytes=len(file_bytes),
                declared_extension=scan_res["declared_extension"],
                detected_mime=scan_res["layer4_mime"]["detected_mime"],
                detected_type=scan_res["detected_type"],
                risk_score=risk_score,
                risk_category=category,
                decision=decision,
                confidence=confidence,
                reasons_json=json.dumps(reasons),
                features_json=json.dumps(features),
                sha256_hash=scan_res["sha256"],
                scanned_from="watcher"
            )
            db_instance.insert_scan(record)

            # Auto-quarantine if Risk is High or Critical (score >= 60.0)
            if decision in ["BLOCK", "QUARANTINE"]:
                QuarantineManager.quarantine_file(
                    file_bytes=file_bytes,
                    original_filename=p.name,
                    original_filepath=filepath,
                    declared_ext=scan_res["declared_extension"],
                    detected_type=scan_res["detected_type"],
                    risk_score=risk_score,
                    reasons=reasons,
                    sha256_hash=scan_res["sha256"]
                )

        except Exception as e:
            print(f"[Watcher Error] Failed to scan {filepath}: {e}")

    def _wait_for_file_stability(self, filepath: str, retries: int = 5, delay: float = 0.5) -> bool:
        last_size = -1
        for _ in range(retries):
            try:
                if os.path.exists(filepath):
                    current_size = os.path.getsize(filepath)
                    if current_size > 0 and current_size == last_size:
                        return True
                    last_size = current_size
            except Exception:
                pass
            time.sleep(delay)
        return last_size > 0

class DownloadMonitorService:
    def __init__(self, watch_dir: str = str(DOWNLOADS_WATCH_DIR)):
        self.watch_dir = watch_dir
        self.observer = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            os.makedirs(self.watch_dir, exist_ok=True)
            event_handler = DownloadFileHandler(self.watch_dir)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.watch_dir, recursive=False)
            self.observer.start()
            self.is_running = True
            print(f"[DownloadMonitor] Watching directory: {self.watch_dir}")

    def stop(self):
        if self.is_running and self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            print("[DownloadMonitor] Watcher stopped.")

# Singleton Monitor Service
download_monitor_instance = DownloadMonitorService()
