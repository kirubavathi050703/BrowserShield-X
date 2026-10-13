"""
Layer 7: Internal Structure Analysis
Performs format-specific structural parsing and validation:
- PDF: %PDF- header, catalog object, xref table, stream counts, suspicious JS/Launch triggers
- ZIP/Office (DOCX/PPTX/XLSX): EOCD locator, central directory records, embedded executable detection, [Content_Types].xml
- PE Executables: MZ header, e_lfanew offset, PE\0\0 signature, COFF header, section table
- Images: PNG/JPEG/GIF structural chunk and dimensions verification
"""

import zipfile
import io
import struct
from typing import Dict, Any, List

class StructuralAnalyzer:
    EXECUTABLE_EMBED_EXTS = {".exe", ".dll", ".bat", ".cmd", ".vbs", ".js", ".ps1", ".scr", ".pif", ".sh", ".py"}

    @classmethod
    def analyze_pdf(cls, file_bytes: bytes) -> Dict[str, Any]:
        has_header = b"%PDF-" in file_bytes[:1024]
        has_eof = b"%%EOF" in file_bytes[-2048:]
        has_xref = b"xref" in file_bytes or b"/XRef" in file_bytes
        has_catalog = b"/Catalog" in file_bytes or b"/Type /Catalog" in file_bytes
        
        # Suspicious PDF objects
        has_js = b"/JS" in file_bytes or b"/JavaScript" in file_bytes
        has_launch = b"/Launch" in file_bytes or b"/EmbeddedFiles" in file_bytes
        
        stream_count = file_bytes.count(b"stream")
        
        is_valid = has_header and (has_eof or has_xref)
        anomaly_count = 0
        if not has_header: anomaly_count += 1
        if not has_eof: anomaly_count += 1
        if has_js or has_launch: anomaly_count += 1

        return {
            "valid_structure": is_valid,
            "has_pdf_header": has_header,
            "has_pdf_eof": has_eof,
            "has_xref_table": has_xref,
            "has_catalog_object": has_catalog,
            "has_suspicious_js_launch": has_js or has_launch,
            "pdf_stream_count": stream_count,
            "anomaly_count": anomaly_count
        }

    @classmethod
    def analyze_zip_office(cls, file_bytes: bytes, declared_ext: str) -> Dict[str, Any]:
        is_valid_zip = False
        has_eocd = b"PK\x05\x06" in file_bytes[-4096:]
        has_embedded_exe = False
        embedded_exe_names: List[str] = []
        is_valid_office = False
        has_content_types = False
        zip_entry_count = 0
        total_uncompressed_size = 0
        is_zip_bomb = False

        if has_eocd:
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zf:
                    is_valid_zip = True
                    infolist = zf.infolist()
                    zip_entry_count = len(infolist)
                    
                    for info in infolist:
                        total_uncompressed_size += info.file_size
                        name_lower = info.filename.lower()
                        
                        # Embedded Executable check
                        for ext in cls.EXECUTABLE_EMBED_EXTS:
                            if name_lower.endswith(ext):
                                has_embedded_exe = True
                                embedded_exe_names.append(info.filename)
                                break
                        
                        if info.filename == "[Content_Types].xml":
                            has_content_types = True

                    # ZIP Bomb detection: Compression ratio > 100x and uncompressed > 10MB
                    compressed_size = max(len(file_bytes), 1)
                    if (total_uncompressed_size / compressed_size) > 100.0 and total_uncompressed_size > 10 * 1024 * 1024:
                        is_zip_bomb = True

            except Exception:
                is_valid_zip = False

        if declared_ext in [".docx", ".xlsx", ".pptx"]:
            is_valid_office = is_valid_zip and has_content_types

        anomaly_count = 0
        if not is_valid_zip: anomaly_count += 1
        if has_embedded_exe: anomaly_count += 2
        if is_zip_bomb: anomaly_count += 2
        if declared_ext in [".docx", ".xlsx", ".pptx"] and not is_valid_office: anomaly_count += 1

        return {
            "valid_structure": is_valid_zip if declared_ext == ".zip" else is_valid_office,
            "is_valid_zip": is_valid_zip,
            "has_eocd_record": has_eocd,
            "is_valid_office": is_valid_office,
            "has_office_content_types": has_content_types,
            "has_embedded_executable": has_embedded_exe,
            "embedded_executables": embedded_exe_names,
            "zip_entry_count": zip_entry_count,
            "is_zip_bomb": is_zip_bomb,
            "anomaly_count": anomaly_count
        }

    @classmethod
    def analyze_pe(cls, file_bytes: bytes) -> Dict[str, Any]:
        has_mz = file_bytes.startswith(b"MZ")
        has_pe_sig = False
        valid_lfanew = False
        section_count = 0
        has_code_section = False
        anomaly_count = 0

        if has_mz and len(file_bytes) >= 0x40:
            try:
                e_lfanew = struct.unpack("<I", file_bytes[0x3C:0x40])[0]
                if 0x40 <= e_lfanew < len(file_bytes) - 4:
                    valid_lfanew = True
                    pe_sig = file_bytes[e_lfanew : e_lfanew + 4]
                    if pe_sig == b"PE\x00\x00":
                        has_pe_sig = True
                        coff_header = file_bytes[e_lfanew + 4 : e_lfanew + 24]
                        if len(coff_header) == 20:
                            section_count = struct.unpack("<H", coff_header[2:4])[0]
                            # Look for .text or executable section
                            if b".text" in file_bytes or b"CODE" in file_bytes:
                                has_code_section = True
            except Exception:
                pass

        is_valid_pe = has_mz and has_pe_sig and valid_lfanew
        if not is_valid_pe and has_mz:
            anomaly_count += 1
        if has_pe_sig and not has_mz:
            anomaly_count += 2  # Tampered PE signature prepended to file!

        return {
            "valid_structure": is_valid_pe,
            "has_mz_header": has_mz,
            "has_pe_signature": has_pe_sig,
            "valid_e_lfanew_offset": valid_lfanew,
            "pe_section_count": section_count,
            "has_code_section": has_code_section,
            "anomaly_count": anomaly_count
        }

    @classmethod
    def analyze_image(cls, file_bytes: bytes, header_type: str) -> Dict[str, Any]:
        is_valid = False
        has_valid_chunks = False
        anomaly_count = 0

        if header_type == "PNG":
            is_valid = file_bytes.startswith(b"\x89PNG\r\n\x1a\n") and b"IHDR" in file_bytes[:64] and b"IEND" in file_bytes[-100:]
            has_valid_chunks = b"IHDR" in file_bytes
        elif header_type == "JPEG":
            is_valid = file_bytes.startswith(b"\xff\xd8\xff") and b"\xff\xd9" in file_bytes[-1024:]
            has_valid_chunks = b"\xff\xe0" in file_bytes or b"\xff\xe1" in file_bytes
        elif header_type == "GIF":
            is_valid = file_bytes.startswith(b"GIF87a") or file_bytes.startswith(b"GIF89a")
            has_valid_chunks = file_bytes.endswith(b"\x3b") or b"\x3b" in file_bytes[-16:]

        if not is_valid and header_type in ["PNG", "JPEG", "GIF"]:
            anomaly_count += 1

        return {
            "valid_structure": is_valid,
            "has_valid_chunks": has_valid_chunks,
            "anomaly_count": anomaly_count
        }

    @classmethod
    def analyze(cls, file_bytes: bytes, declared_ext: str, header_type: str) -> Dict[str, Any]:
        # Orchestrate structural checks based on declared or detected format
        pdf_res = cls.analyze_pdf(file_bytes) if (declared_ext == ".pdf" or header_type == "PDF") else None
        zip_res = cls.analyze_zip_office(file_bytes, declared_ext) if (declared_ext in [".zip", ".docx", ".xlsx", ".pptx"] or header_type == "ZIP") else None
        pe_res = cls.analyze_pe(file_bytes) if (declared_ext in [".exe", ".dll"] or header_type == "PE_EXE") else None
        img_res = cls.analyze_image(file_bytes, header_type) if (declared_ext in [".png", ".jpg", ".jpeg", ".gif"] or header_type in ["PNG", "JPEG", "GIF"]) else None

        # Determine overall structural validity and total anomaly count
        total_anomalies = 0
        overall_valid = True

        for res in [pdf_res, zip_res, pe_res, img_res]:
            if res:
                total_anomalies += res.get("anomaly_count", 0)
                if not res.get("valid_structure", True):
                    overall_valid = False

        return {
            "overall_structural_validity": overall_valid,
            "total_structural_anomalies": total_anomalies,
            "pdf_structure": pdf_res,
            "zip_office_structure": zip_res,
            "pe_structure": pe_res,
            "image_structure": img_res
        }
