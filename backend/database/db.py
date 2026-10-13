"""
SQLite Database Connection and Data Access Object (DAO) for BrowserShield-X.
"""

import sqlite3
import json
import datetime
from typing import List, Optional, Dict, Any
from backend.config import DATABASE_PATH
from backend.database.models import ScanHistoryRecord, QuarantineRecord

class Database:
    def __init__(self, db_path: str = str(DATABASE_PATH)):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                declared_extension TEXT NOT NULL,
                detected_mime TEXT NOT NULL,
                detected_type TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_category TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasons_json TEXT NOT NULL,
                features_json TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                scanned_from TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quarantine_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quarantine_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                original_path TEXT NOT NULL,
                quarantine_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                declared_extension TEXT NOT NULL,
                detected_type TEXT NOT NULL,
                risk_score REAL NOT NULL,
                reasons_json TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                status TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            );
            """)
            conn.commit()

    def insert_scan(self, record: ScanHistoryRecord) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scan_history (
                    timestamp, filename, file_size_bytes, declared_extension,
                    detected_mime, detected_type, risk_score, risk_category,
                    decision, confidence, reasons_json, features_json, sha256_hash, scanned_from
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.timestamp, record.filename, record.file_size_bytes, record.declared_extension,
                record.detected_mime, record.detected_type, record.risk_score, record.risk_category,
                record.decision, record.confidence, record.reasons_json, record.features_json,
                record.sha256_hash, record.scanned_from
            ))
            conn.commit()
            return cursor.lastrowid

    def get_scans(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_history ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                rec = dict(r)
                rec['reasons'] = json.loads(rec['reasons_json']) if rec.get('reasons_json') else []
                rec['features'] = json.loads(rec['features_json']) if rec.get('features_json') else {}
                result.append(rec)
            return result

    def get_scan_by_id(self, scan_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_history WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            if row:
                rec = dict(row)
                rec['reasons'] = json.loads(rec['reasons_json']) if rec.get('reasons_json') else []
                rec['features'] = json.loads(rec['features_json']) if rec.get('features_json') else {}
                return rec
            return None

    def insert_quarantine(self, record: QuarantineRecord) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quarantine_vault (
                    quarantine_id, timestamp, original_path, quarantine_path,
                    filename, declared_extension, detected_type, risk_score,
                    reasons_json, sha256_hash, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.quarantine_id, record.timestamp, record.original_path, record.quarantine_path,
                record.filename, record.declared_extension, record.detected_type, record.risk_score,
                record.reasons_json, record.sha256_hash, record.status
            ))
            conn.commit()
            return cursor.lastrowid

    def get_quarantine_records(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quarantine_vault ORDER BY id DESC")
            rows = cursor.fetchall()
            result = []
            for r in rows:
                rec = dict(r)
                rec['reasons'] = json.loads(rec['reasons_json']) if rec.get('reasons_json') else []
                result.append(rec)
            return result

    def update_quarantine_status(self, quarantine_id: str, new_status: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE quarantine_vault SET status = ? WHERE quarantine_id = ?", (new_status, quarantine_id))
            conn.commit()

    def get_quarantine_by_id(self, quarantine_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quarantine_vault WHERE quarantine_id = ?", (quarantine_id,))
            row = cursor.fetchone()
            if row:
                rec = dict(row)
                rec['reasons'] = json.loads(rec['reasons_json']) if rec.get('reasons_json') else []
                return rec
            return None

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value_json FROM system_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return default

    def set_setting(self, key: str, value: Any):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO system_settings (key, value_json) VALUES (?, ?)", (key, json.dumps(value)))
            conn.commit()

# Singleton DB instance
db_instance = Database()
