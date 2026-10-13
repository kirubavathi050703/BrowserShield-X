"""
Rule Engine Module
Evaluates deterministic security rules and anomaly patterns.
Produces a list of rule findings and a normalized rule anomaly score (0.0 to 1.0).
"""

from typing import Dict, Any, List, Tuple

class RuleEngine:
    @classmethod
    def evaluate(cls, scan_result: Dict[str, Any]) -> Tuple[List[str], float]:
        reasons: List[str] = []
        rule_score = 0.0

        l1 = scan_result["layer1_extension"]
        l2 = scan_result["layer2_header"]
        l3 = scan_result["layer3_footer"]
        l4 = scan_result["layer4_mime"]
        l5 = scan_result["layer5_entropy"]
        l7 = scan_result["layer7_structure"]

        declared_ext = l1["declared_extension"]
        detected_type = scan_result["detected_type"]

        # Rule 1: Double Extension Trick (e.g. invoice.pdf.exe)
        if l1.get("has_double_extension"):
            reasons.append(f"✗ Suspicious double extension detected ({l1['secondary_extension']}{declared_ext})")
            rule_score += 0.40

        # Rule 2: Executable disguised as document/image (MIME Critical Mismatch)
        if l4.get("is_mime_mismatch") and l4.get("mismatch_severity") == "CRITICAL":
            reasons.append(f"✗ CRITICAL MISMATCH: File claims to be {declared_ext.upper()} but content is executable ({l4['detected_mime']})")
            rule_score += 0.60
        elif l4.get("is_mime_mismatch"):
            reasons.append(f"✗ MIME mismatch: Declared {l4['declared_mime']} vs content {l4['detected_mime']}")
            rule_score += 0.25

        # Rule 3: Corrupted or tampered magic bytes
        if l2.get("corrupted_header_detected"):
            reasons.append(f"✗ Tampered magic bytes: Header signature offset or corrupted ({l2.get('suspected_offset_header_type')})")
            rule_score += 0.35
        elif not l2.get("magic_match") and l1.get("is_known_extension"):
            reasons.append(f"✗ Header mismatch: {declared_ext.upper()} header magic bytes missing")
            rule_score += 0.30

        # Rule 4: Embedded Executable inside Office / Zip archive
        zip_struct = l7.get("zip_office_structure")
        if zip_struct and zip_struct.get("has_embedded_executable"):
            exe_names = ", ".join(zip_struct.get("embedded_executables", []))
            reasons.append(f"✗ SUSPICIOUS ARCHIVE: Embedded executable file(s) found inside container ({exe_names})")
            rule_score += 0.50

        # Rule 5: Zip Bomb detection
        if zip_struct and zip_struct.get("is_zip_bomb"):
            reasons.append("✗ CRITICAL ARCHIVE: Extremely high compression ratio detected (potential Zip Bomb)")
            rule_score += 0.70

        # Rule 6: Inconsistent Header and Footer
        if not l3.get("header_footer_consistent"):
            reasons.append(f"✗ Structural conflict: Header indicates {l2['detected_header_type']} but footer indicates {l3['detected_footer_type']}")
            rule_score += 0.30

        # Rule 7: High Entropy packed payload
        if l5.get("is_high_entropy_packed"):
            reasons.append(f"✓ High entropy content detected ({l5['global_entropy']:.2f}/8.0 - packed or encrypted stream)")
            rule_score += 0.15

        # Rule 8: PDF suspicious JS or Launch streams
        pdf_struct = l7.get("pdf_structure")
        if pdf_struct and pdf_struct.get("has_suspicious_js_launch"):
            reasons.append("✗ PDF Security Risk: Contains embedded JavaScript or Launch action streams")
            rule_score += 0.40

        # Positive indicator if extension matches detected type perfectly
        if not reasons and l2.get("magic_match") and not l4.get("is_mime_mismatch"):
            reasons.append(f"✓ Declared extension ({declared_ext}) matches magic bytes and MIME structure")

        normalized_score = min(rule_score, 1.0)
        return reasons, round(normalized_score, 4)
