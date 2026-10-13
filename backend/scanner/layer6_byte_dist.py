"""
Layer 6: Byte Distribution Analysis
Extracts 256-bin byte frequency histogram and key statistical metrics:
- Mean byte value
- Byte value standard deviation
- Zero-byte ratio (0x00 frequency)
- Printable ASCII ratio (0x20 - 0x7E)
- High-bit byte ratio (0x80 - 0xFF)
- Chi-Square test against uniform byte distribution
"""

import math
from typing import Dict, Any, List

class ByteDistributionAnalyzer:
    @classmethod
    def analyze(cls, file_bytes: bytes) -> Dict[str, Any]:
        if not file_bytes:
            return {
                "zero_byte_ratio": 0.0,
                "printable_ascii_ratio": 0.0,
                "high_bit_ratio": 0.0,
                "byte_mean": 0.0,
                "byte_std": 0.0,
                "chi_square_uniformity": 0.0,
                "top_byte_histogram": [0] * 16
            }

        length = len(file_bytes)
        counts = [0] * 256
        for b in file_bytes:
            counts[b] += 1

        zero_bytes = counts[0]
        printable_bytes = sum(counts[32:127]) + counts[9] + counts[10] + counts[13] # ASCII printable + space/tab/newline
        high_bit_bytes = sum(counts[128:256])

        zero_ratio = round(zero_bytes / length, 4)
        printable_ratio = round(printable_bytes / length, 4)
        high_bit_ratio = round(high_bit_bytes / length, 4)

        # Statistical metrics
        mean = sum(i * counts[i] for i in range(256)) / length
        variance = sum(counts[i] * ((i - mean) ** 2) for i in range(256)) / length
        std = math.sqrt(variance)

        # Chi-Square calculation against uniform distribution (E_i = length / 256)
        expected = length / 256.0
        chi_square = sum(((counts[i] - expected) ** 2) / expected for i in range(256))

        # Downsample histogram to 16 bins for compact reporting/feature representation
        histogram_16 = [sum(counts[i * 16 : (i + 1) * 16]) for i in range(16)]

        return {
            "zero_byte_ratio": zero_ratio,
            "printable_ascii_ratio": printable_ratio,
            "high_bit_ratio": high_bit_ratio,
            "byte_mean": round(mean, 2),
            "byte_std": round(std, 2),
            "chi_square_uniformity": round(chi_square, 2),
            "top_byte_histogram": histogram_16
        }
