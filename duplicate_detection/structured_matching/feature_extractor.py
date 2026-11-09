import math
import numpy as np
from typing import Dict, Any, List, Optional
from duplicate_detection.preprocessing.geo_utils import (
    haversine_distance_meters,
    calculate_location_similarity,
    calculate_temporal_compatibility
)
from duplicate_detection.preprocessing.image_fingerprint import (
    calculate_image_evidence_similarity
)

FEATURE_COLUMNS = [
    'semantic_similarity',
    'cross_encoder_score',
    'location_similarity',
    'haversine_distance_m',
    'temporal_compatibility',
    'temporal_hours_diff',
    'category_match',
    'complaint_type_match',
    'muni_match',
    'ward_match',
    'image_similarity',
    'has_geo_coords',
    'has_image_evidence'
]

def extract_pair_features(
    record: Dict[str, Any],
    semantic_sim: Optional[float] = None,
    cross_encoder_score: Optional[float] = None
) -> Dict[str, float]:
    """
    Extracts rich structured, multimodal and incident compatibility features
    for a single complaint pair.
    """
    # 1. Semantic and Cross-Encoder Scores (or fallback to text jaccard if missing)
    if semantic_sim is None:
        text_a = str(record.get('complaint_a', '')).lower()
        text_b = str(record.get('complaint_b', '')).lower()
        set_a = set(text_a.split())
        set_b = set(text_b.split())
        inter = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        semantic_sim = inter / union if union > 0 else 0.0

    if cross_encoder_score is None:
        cross_encoder_score = semantic_sim

    # 2. Location & Geographic Proximity
    lat_a = record.get('lat_a')
    lng_a = record.get('lng_a')
    lat_b = record.get('lat_b')
    lng_b = record.get('lng_b')
    ward_a = record.get('ward_a') or record.get('location_a')
    ward_b = record.get('ward_b') or record.get('location_b')

    has_geo = 1.0 if (lat_a is not None and lat_b is not None) else 0.0
    loc_sim, dist_m, _ = calculate_location_similarity(lat_a, lng_a, ward_a, lat_b, lng_b, ward_b)

    # 3. Temporal Compatibility
    ts_a = record.get('timestamp_a')
    ts_b = record.get('timestamp_b')
    temp_sim, delta_h, _ = calculate_temporal_compatibility(ts_a, ts_b)

    # 4. Department & Complaint Type Match
    cat_a = str(record.get('category_a', '')).strip().lower()
    cat_b = str(record.get('category_b', '')).strip().lower()
    cat_match = 1.0 if (cat_a == cat_b and cat_a != '') else 0.0

    type_a = str(record.get('complaint_type_a', '')).strip().lower()
    type_b = str(record.get('complaint_type_b', '')).strip().lower()
    type_match = 1.0 if (type_a == type_b and type_a != '') else 0.0

    # 5. Administrative Jurisdiction (Municipality & Ward)
    muni_a = str(record.get('muni_a', '')).strip().lower()
    muni_b = str(record.get('muni_b', '')).strip().lower()
    muni_match = 1.0 if (muni_a == muni_b and muni_a != '') else (1.0 if not muni_a or not muni_b else 0.0)

    if ward_a and ward_b:
        ward_match = 1.0 if str(ward_a).strip().lower() == str(ward_b).strip().lower() else 0.0
    elif dist_m <= 150.0 and has_geo:
        # Same localized radius (< 150m) belongs to the same ward boundary
        ward_match = 1.0
    else:
        ward_match = 0.0

    # 6. Image Evidence
    hash_a = record.get('image_hash_a')
    hash_b = record.get('image_hash_b')
    has_img = 1.0 if (hash_a and hash_b) else 0.0
    img_sim, _, _ = calculate_image_evidence_similarity(hash_a, hash_b)

    return {
        'semantic_similarity': float(semantic_sim),
        'cross_encoder_score': float(cross_encoder_score),
        'location_similarity': float(loc_sim),
        'haversine_distance_m': float(min(dist_m, 10000.0)),
        'temporal_compatibility': float(temp_sim),
        'temporal_hours_diff': float(min(delta_h, 720.0)),
        'category_match': float(cat_match),
        'complaint_type_match': float(type_match),
        'muni_match': float(muni_match),
        'ward_match': float(ward_match),
        'image_similarity': float(img_sim),
        'has_geo_coords': float(has_geo),
        'has_image_evidence': float(has_img)
    }

def batch_extract_features(df_pairs, semantic_scores=None, cross_encoder_scores=None) -> np.ndarray:
    """
    Extracts 2D feature matrix from a DataFrame of complaint pairs.
    """
    records = df_pairs.to_dict('records')
    matrix = []
    for i, r in enumerate(records):
        s_score = semantic_scores[i] if semantic_scores is not None else None
        c_score = cross_encoder_scores[i] if cross_encoder_scores is not None else None
        feat_dict = extract_pair_features(r, s_score, c_score)
        matrix.append([feat_dict[col] for col in FEATURE_COLUMNS])
    return np.array(matrix, dtype=np.float32)
