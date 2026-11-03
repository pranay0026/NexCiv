import base64
import io
from PIL import Image
from typing import Optional, Tuple

def compute_dhash_hamming_distance(hash1: str, hash2: str) -> int:
    """
    Computes Hamming distance between two 16-character hex dHash strings.
    0 = identical image
    <= 5 = near identical (crop, compression, color shift)
    > 12 = completely different images
    """
    if not hash1 or not hash2 or len(hash1) != 16 or len(hash2) != 16:
        return 64
    
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        xor_val = val1 ^ val2
        return bin(xor_val).count('1')
    except Exception:
        return 64

def calculate_image_evidence_similarity(hash1: Optional[str], hash2: Optional[str]) -> Tuple[float, int, str]:
    """
    Evaluates visual evidence similarity based on dHash perceptual distance.
    Returns: (visual_score 0.0-1.0, hamming_distance, explanation)
    """
    if not hash1 or not hash2:
        # Absence of image evidence is not evidence of absence
        return 0.5, 64, "Image evidence missing on one or both submissions (neutral)"
    
    dist = compute_dhash_hamming_distance(hash1, hash2)
    if dist <= 2:
        return 1.0, dist, f"Exact or nearly identical photograph submitted (Hamming dist: {dist})"
    elif dist <= 6:
        return 0.85, dist, f"Very high visual similarity / same scene angle (Hamming dist: {dist})"
    elif dist <= 12:
        return 0.4, dist, f"Moderate visual resemblance (Hamming dist: {dist})"
    else:
        return 0.05, dist, f"Completely distinct visual evidence (Hamming dist: {dist})"
