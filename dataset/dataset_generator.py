"""
Dataset Generator Module
Generates synthetic benign, spoofed, and adversarial file samples for training, validation, and benchmarking.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from backend.scanner.core_scanner import MultiLayerScanner
from backend.feature_extractor.extractor import FeatureExtractor
from backend.adversarial.generator import AdversarialGenerator

class DatasetGenerator:
    @classmethod
    def generate_full_dataset(cls, num_samples_per_cat: int = 40) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        X_list = []
        y_list = []
        meta_list = []

        # 1. Benign Samples (Label = 0)
        benign_templates = [
            ("%PDF-1.5\n1 0 obj<< /Type /Catalog >>endobj\ntrailer<<>>\n%%EOF\n", "doc_{}.pdf"),
            ("\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + "A" * 50 + "IEND\xaeB`\x82", "img_{}.png"),
            ("\xff\xd8\xff\xe0\x00\x10JFIF" + "B" * 50 + "\xff\xd9", "photo_{}.jpg"),
            ("PK\x03\x04\x14\x00\x00\x00\x08\x00" + "[Content_Types].xml" + "C" * 40 + "PK\x05\x06" + "\x00" * 18, "report_{}.docx"),
            ("PK\x03\x04\x14\x00\x00\x00\x08\x00" + "D" * 60 + "PK\x05\x06" + "\x00" * 18, "archive_{}.zip"),
        ]

        for idx in range(num_samples_per_cat):
            tmpl, name_pattern = benign_templates[idx % len(benign_templates)]
            raw_bytes = (tmpl + f"\n// sample index {idx}").encode("latin1", errors="ignore")
            filename = name_pattern.format(idx)
            
            scan_res = MultiLayerScanner.scan_file_bytes(raw_bytes, filename)
            vec = FeatureExtractor.extract_features(scan_res)
            
            X_list.append(vec)
            y_list.append(0)
            meta_list.append({"filename": filename, "type": "benign", "label": 0})

        # 2. Extension Spoofed / Malicious Samples (Label = 1)
        pe_raw = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + (b"\x00" * 60) + b"\x80\x00\x00\x00" + (b"\x00" * 64) + b"PE\x00\x00" + (b"X" * 150)
        spoofed_templates = [
            (pe_raw, "invoice_{}.pdf", ".pdf"),
            (pe_raw, "chart_{}.png", ".png"),
            (pe_raw, "statement_{}.docx", ".docx"),
            (b"%PDF-1.4\nMZ\x90\x00PE\x00\x00", "prepended_{}.pdf", ".pdf"),
            (b"PK\x03\x04[Content_Types].xml\x00payload.exe\x00MZ\x90\x00PK\x05\x06\x00" * 2, "trojan_{}.docx", ".docx")
        ]

        for idx in range(num_samples_per_cat):
            tmpl_bytes, name_pattern, decl_ext = spoofed_templates[idx % len(spoofed_templates)]
            raw_bytes = tmpl_bytes + f"\n// spoof index {idx}".encode()
            filename = name_pattern.format(idx)

            scan_res = MultiLayerScanner.scan_file_bytes(raw_bytes, filename)
            vec = FeatureExtractor.extract_features(scan_res)

            X_list.append(vec)
            y_list.append(1)
            meta_list.append({"filename": filename, "type": "spoofed", "label": 1})

        # 3. Adversarial Samples (Label = 1)
        adv_samples = AdversarialGenerator.generate_adversarial_samples()
        for adv in adv_samples:
            scan_res = MultiLayerScanner.scan_file_bytes(adv["bytes"], adv["name"])
            vec = FeatureExtractor.extract_features(scan_res)
            lbl = 0 if adv["attack_type"] == "none_benign" else 1
            X_list.append(vec)
            y_list.append(lbl)
            meta_list.append({"filename": adv["name"], "type": "adversarial", "label": lbl})

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        return X, y, meta_list
