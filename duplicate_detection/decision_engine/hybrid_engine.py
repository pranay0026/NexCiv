import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from duplicate_detection.configs.config import cfg
from duplicate_detection.preprocessing.text_cleaner import clean_complaint_text
from duplicate_detection.preprocessing.geo_utils import (
    haversine_distance_meters,
    calculate_location_similarity,
    calculate_temporal_compatibility
)
from duplicate_detection.preprocessing.image_fingerprint import (
    calculate_image_evidence_similarity
)
from duplicate_detection.structured_matching.feature_extractor import extract_pair_features
from duplicate_detection.structured_matching.classifier import get_structured_classifier

class HybridDecisionEngine:
    """
    NEX-CIV 3-Layer Hybrid Duplicate Decision Engine.
    Combines:
    - S: Dense Semantic Embedding Similarity (Layer 1)
    - L: Location & Geospatial Proximity Compatibility (Layer 3)
    - C: Deep Cross-Encoder Pair Interaction Score (Layer 2)
    - T: Temporal Lifespan Compatibility (Layer 3)
    - I: Multimodal Perceptual Image Fingerprint (Layer 3)

    Configurable Decision Formulation:
    D = w_s*S + w_l*L + w_c*C + w_t*T + w_i*I
    """

    def __init__(
        self,
        weight_s: Optional[float] = None,
        weight_l: Optional[float] = None,
        weight_c: Optional[float] = None,
        weight_t: Optional[float] = None,
        weight_i: Optional[float] = None,
        threshold_duplicate: Optional[float] = None,
        threshold_review: Optional[float] = None
    ):
        self.w_s = weight_s if weight_s is not None else cfg.WEIGHT_SEMANTIC
        self.w_l = weight_l if weight_l is not None else cfg.WEIGHT_LOCATION
        self.w_c = weight_c if weight_c is not None else cfg.WEIGHT_CROSS_ENCODER
        self.w_t = weight_t if weight_t is not None else cfg.WEIGHT_TEMPORAL
        self.w_i = weight_i if weight_i is not None else cfg.WEIGHT_IMAGE

        self.threshold_dup = threshold_duplicate if threshold_duplicate is not None else cfg.THRESHOLD_HIGH_CONFIDENCE_DUPLICATE
        self.threshold_rev = threshold_review if threshold_review is not None else cfg.THRESHOLD_HUMAN_REVIEW

        self.gbdt_classifier = get_structured_classifier()

    def evaluate_pair(
        self,
        new_complaint: Dict[str, Any],
        candidate_complaint: Dict[str, Any],
        semantic_sim: float,
        cross_encoder_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates an incoming complaint against an existing historical complaint or master incident candidate.
        Returns full explainable audit dictionary with decision, score, confidence, and reasons.
        """
        if cross_encoder_score is None:
            cross_encoder_score = semantic_sim

        reasons = []

        # 1. Department Compatibility Gate
        dept_new = str(new_complaint.get('category') or new_complaint.get('department_code') or '').strip().lower()
        dept_cand = str(candidate_complaint.get('category') or candidate_complaint.get('department_code') or '').strip().lower()

        dept_match = (dept_new == dept_cand) and (dept_new != '')
        if not dept_match and dept_new and dept_cand:
            # Different municipal wings are distinct physical problems
            return {
                'composite_score': 0.0,
                'decision': 'new_incident',
                'confidence': 0.98,
                'recommended_action': 'Register as new independent incident',
                'semantic_similarity': semantic_sim,
                'location_similarity': 0.0,
                'cross_encoder_score': cross_encoder_score,
                'temporal_compatibility': 0.0,
                'image_similarity': 0.0,
                'distance_meters': 999999.0,
                'reasons': [f"Different municipal wings: '{dept_new}' vs '{dept_cand}'"]
            }

        # 2. Location & Haversine Distance
        lat1, lng1 = new_complaint.get('location_lat'), new_complaint.get('location_lng')
        lat2, lng2 = candidate_complaint.get('location_lat'), candidate_complaint.get('location_lng')
        ward1 = new_complaint.get('ward') or new_complaint.get('location_address')
        ward2 = candidate_complaint.get('ward') or candidate_complaint.get('location_address')

        loc_score, dist_m, loc_just = calculate_location_similarity(lat1, lng1, ward1, lat2, lng2, ward2)
        reasons.append(loc_just)

        # 3. Temporal Compatibility
        t1 = new_complaint.get('created_at') or new_complaint.get('timestamp')
        t2 = candidate_complaint.get('created_at') or candidate_complaint.get('timestamp')
        temp_score, delta_hours, temp_just = calculate_temporal_compatibility(t1, t2)
        reasons.append(temp_just)

        # 4. Multimodal Image Evidence
        hash1 = new_complaint.get('image_hash')
        hash2 = candidate_complaint.get('image_hash')
        img_score, hamming_dist, img_just = calculate_image_evidence_similarity(hash1, hash2)
        if hash1 and hash2:
            reasons.append(img_just)

        # 5. Hybrid Weighted Scoring Formula:
        # D = w_s*S + w_l*L + w_c*C + w_t*T + w_i*I
        active_weights = self.w_s + self.w_l + self.w_c + self.w_t
        raw_composite = (
            self.w_s * semantic_sim +
            self.w_l * loc_score +
            self.w_c * cross_encoder_score +
            self.w_t * temp_score
        )

        if hash1 and hash2:
            raw_composite += self.w_i * img_score
            active_weights += self.w_i

        composite_score = float(np.clip(raw_composite / active_weights, 0.0, 1.0))

        # Check with ML Model if available for validation
        feat_dict = extract_pair_features(
            {
                'complaint_a': new_complaint.get('description', ''),
                'complaint_b': candidate_complaint.get('description', ''),
                'lat_a': lat1, 'lng_a': lng1, 'lat_b': lat2, 'lng_b': lng2,
                'ward_a': ward1, 'ward_b': ward2,
                'timestamp_a': t1, 'timestamp_b': t2,
                'category_a': dept_new, 'category_b': dept_cand,
                'complaint_type_a': new_complaint.get('complaint_type', ''),
                'complaint_type_b': candidate_complaint.get('complaint_type', ''),
                'image_hash_a': hash1, 'image_hash_b': hash2
            },
            semantic_sim=semantic_sim,
            cross_encoder_score=cross_encoder_score
        )
        ml_prob = self.gbdt_classifier.predict_pair(feat_dict)

        # Final calibrated score combines weighted formula and GBDT
        final_score = round(float(0.70 * composite_score + 0.30 * ml_prob), 4)

        # 6. Incident Duplication Decision Thresholds
        if final_score >= self.threshold_dup:
            decision = 'duplicate'
            recommended_action = 'Auto-link to existing Master Incident (increment upvote)'
            confidence = final_score
            reasons.insert(0, f"High-confidence duplicate incident match ({final_score:.1%})")
        elif final_score >= self.threshold_rev:
            decision = 'review_required'
            recommended_action = 'Flag for Municipal Cadre verification before linking'
            confidence = final_score
            reasons.insert(0, f"Potential duplicate requiring human review ({final_score:.1%})")
        else:
            decision = 'new_incident'
            recommended_action = 'Register as new Master Incident'
            confidence = round(1.0 - final_score, 4)
            reasons.insert(0, f"Distinct civic event ({final_score:.1%} match)")

        return {
            'composite_score': final_score,
            'decision': decision,
            'confidence': confidence,
            'recommended_action': recommended_action,
            'semantic_similarity': round(semantic_sim, 4),
            'location_similarity': round(loc_score, 4),
            'cross_encoder_score': round(cross_encoder_score, 4),
            'temporal_compatibility': round(temp_score, 4),
            'image_similarity': round(img_score, 4),
            'distance_meters': round(dist_m, 1),
            'reasons': reasons
        }

_GLOBAL_DECISION_ENGINE = None

def get_decision_engine() -> HybridDecisionEngine:
    global _GLOBAL_DECISION_ENGINE
    if _GLOBAL_DECISION_ENGINE is None:
        _GLOBAL_DECISION_ENGINE = HybridDecisionEngine()
    return _GLOBAL_DECISION_ENGINE
