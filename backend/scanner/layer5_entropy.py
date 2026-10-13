"""
Layer 5: Shannon Entropy Analysis
Calculates global Shannon entropy, head/body/tail entropy breakdown, and block entropy variance
to detect packing, encryption, compression, or high-randomness payloads.
"""

import math
from typing import Dict, Any, List

class EntropyAnalyzer:
    BLOCK_SIZE = 512

    @classmethod
    def calculate_entropy(cls, data: bytes) -> float:
        if not data:
            return 0.0
        length = len(data)
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @classmethod
    def analyze(cls, file_bytes: bytes) -> Dict[str, Any]:
        if not file_bytes:
            return {
                "global_entropy": 0.0,
                "head_entropy": 0.0,
                "body_entropy": 0.0,
                "tail_entropy": 0.0,
                "min_block_entropy": 0.0,
                "max_block_entropy": 0.0,
                "block_entropy_variance": 0.0,
                "is_high_entropy_packed": False
            }

        global_ent = cls.calculate_entropy(file_bytes)
        
        # Segment analysis
        head_ent = cls.calculate_entropy(file_bytes[:1024])
        tail_ent = cls.calculate_entropy(file_bytes[-1024:])
        body_ent = cls.calculate_entropy(file_bytes[1024:-1024]) if len(file_bytes) > 2048 else global_ent

        # Block entropy analysis
        block_entropies: List[float] = []
        for i in range(0, len(file_bytes), cls.BLOCK_SIZE):
            block = file_bytes[i:i + cls.BLOCK_SIZE]
            if len(block) >= 64:
                block_entropies.append(cls.calculate_entropy(block))

        min_ent = min(block_entropies) if block_entropies else global_ent
        max_ent = max(block_entropies) if block_entropies else global_ent

        if block_entropies:
            mean_b = sum(block_entropies) / len(block_entropies)
            var_b = sum((x - mean_b) ** 2 for x in block_entropies) / len(block_entropies)
        else:
            var_b = 0.0

        # Flag unusually high entropy (e.g. > 7.5 out of 8.0 indicates packed/encrypted code or compression)
        is_high_entropy = global_ent >= 7.5

        return {
            "global_entropy": global_ent,
            "head_entropy": head_ent,
            "body_entropy": body_ent,
            "tail_entropy": tail_ent,
            "min_block_entropy": round(min_ent, 4),
            "max_block_entropy": round(max_ent, 4),
            "block_entropy_variance": round(var_b, 6),
            "is_high_entropy_packed": is_high_entropy
        }
