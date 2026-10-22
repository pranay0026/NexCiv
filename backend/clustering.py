import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from vision_engine import get_vision_engine

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes accurate Great Circle distance in meters between two GPS coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def compute_text_jaccard(text1: str, text2: str) -> float:
    """Computes word-level Jaccard similarity between two complaint descriptions."""
    if not text1 or not text2:
        return 0.0
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    # Strip basic punctuation
    tokens1 = {t.strip(".,!?:;\"'()[]{}") for t in tokens1 if len(t) > 2}
    tokens2 = {t.strip(".,!?:;\"'()[]{}") for t in tokens2 if len(t) > 2}
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / float(len(union))

class DuplicateClusteringEngine:
    """
    NEXCIV Phase 2 Duplicate Detection & Hotspot Clustering Engine.
    Detects duplicate citizen reports using:
    - Geospatial proximity (Haversine formula, meters threshold)
    - Perceptual image hashing (dHash Hamming distance)
    - Department & semantic text congruence
    """

    DUPLICATE_DISTANCE_THRESHOLD_METERS = 100.0  # Max distance for consideration
    DUPLICATE_SIMILARITY_THRESHOLD = 0.68         # Minimum composite score to declare duplicate

    def __init__(self):
        self.vision_engine = get_vision_engine()

    def calculate_pair_similarity(
        self,
        item1: Dict[str, Any],
        item2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates multimodal similarity between two complaints:
        Returns:
            {
                'similarity_score': float (0.0 to 1.0),
                'distance_meters': float,
                'geo_score': float,
                'visual_score': float,
                'text_score': float,
                'is_duplicate': bool,
                'reasons': List[str]
            }
        """
        reasons = []

        # 1. Department / Category Check
        cat1 = (item1.get('category') or item1.get('department_code') or '').lower()
        cat2 = (item2.get('category') or item2.get('department_code') or '').lower()
        category_match = (cat1 == cat2) and (cat1 != '')
        if not category_match:
            # Different municipal wings are almost never duplicates of each other
            return {
                'similarity_score': 0.0,
                'distance_meters': 999999.0,
                'geo_score': 0.0,
                'visual_score': 0.0,
                'text_score': 0.0,
                'is_duplicate': False,
                'reasons': ['Different municipal departments']
            }

        # 2. Geospatial Proximity Evaluation
        lat1, lng1 = item1.get('location_lat'), item1.get('location_lng')
        lat2, lng2 = item2.get('location_lat'), item2.get('location_lng')

        distance_meters = 999999.0
        geo_score = 0.0

        if (lat1 is not None and lng1 is not None and 
            lat2 is not None and lng2 is not None):
            try:
                distance_meters = haversine_distance_meters(float(lat1), float(lng1), float(lat2), float(lng2))
                if distance_meters <= 15.0:
                    geo_score = 1.0
                    reasons.append(f"Exact same spot ({distance_meters:.1f}m away)")
                elif distance_meters <= 40.0:
                    geo_score = 0.90
                    reasons.append(f"Same immediate road section ({distance_meters:.1f}m away)")
                elif distance_meters <= 80.0:
                    geo_score = 0.70
                    reasons.append(f"Nearby street vicinity ({distance_meters:.1f}m away)")
                elif distance_meters <= 150.0:
                    geo_score = 0.40
                elif distance_meters <= 300.0:
                    geo_score = 0.15
                else:
                    geo_score = 0.0
            except Exception:
                geo_score = 0.0
        else:
            # Fall back to address text comparison if GPS missing
            addr1 = (item1.get('location_address') or '').lower()
            addr2 = (item2.get('location_address') or '').lower()
            if addr1 and addr2 and (addr1 in addr2 or addr2 in addr1):
                geo_score = 0.75
                reasons.append("Matching street address")

        # 3. Visual Perceptual Hash Comparison
        hash1 = item1.get('image_hash')
        hash2 = item2.get('image_hash')
        
        # If hash not precomputed but image_url or image_data exists, compute on the fly
        if not hash1 and item1.get('image_url'):
            hash1 = self.vision_engine.verify_and_analyze_image(item1['image_url']).get('image_hash')
        if not hash2 and item2.get('image_url'):
            hash2 = self.vision_engine.verify_and_analyze_image(item2['image_url']).get('image_hash')

        visual_score = 0.5  # Neutral default when no images available
        has_images = bool(hash1 and hash2)
        if has_images:
            visual_score = self.vision_engine.visual_similarity_from_hashes(hash1, hash2)
            if visual_score >= 0.85:
                reasons.append(f"High visual similarity ({visual_score*100:.1f}%)")

        # 4. Semantic Text Similarity
        text1 = f"{item1.get('title', '')} {item1.get('description', '')}"
        text2 = f"{item2.get('title', '')} {item2.get('description', '')}"
        text_score = compute_text_jaccard(text1, text2)
        if text_score >= 0.35:
            reasons.append(f"Matching problem description keywords ({text_score*100:.1f}%)")

        # 5. Multimodal Composite Fusion
        if has_images:
            # Weighted: 45% Geo, 35% Visual, 20% Text
            composite_score = (0.45 * geo_score) + (0.35 * visual_score) + (0.20 * text_score)
        else:
            # Weighted: 65% Geo, 35% Text
            composite_score = (0.65 * geo_score) + (0.35 * text_score)

        # High confidence override: If exact same photo within 80 meters
        if has_images and visual_score >= 0.90 and distance_meters <= 80.0:
            composite_score = max(composite_score, 0.95)
            reasons.append("Identical photo evidence at same location")

        is_dup = (composite_score >= self.DUPLICATE_SIMILARITY_THRESHOLD and distance_meters <= self.DUPLICATE_DISTANCE_THRESHOLD_METERS)

        return {
            'similarity_score': round(composite_score, 3),
            'distance_meters': round(distance_meters, 1),
            'geo_score': round(geo_score, 3),
            'visual_score': round(visual_score, 3),
            'text_score': round(text_score, 3),
            'is_duplicate': is_dup,
            'reasons': reasons
        }

    def find_duplicate(
        self,
        new_complaint: Dict[str, Any],
        active_complaints: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Searches active complaints for the strongest duplicate match.
        Returns match dict if duplicate is confirmed, else None.
        """
        best_match = None
        highest_score = 0.0

        for candidate in active_complaints:
            # Skip resolved complaints or complaints with identical IDs
            if candidate.get('status') == 'resolved':
                continue
            if candidate.get('id') == new_complaint.get('id'):
                continue
            # If candidate is already marked as a duplicate, compare against its master instead
            if candidate.get('is_duplicate') and candidate.get('master_complaint_id'):
                continue

            sim_info = self.calculate_pair_similarity(new_complaint, candidate)
            if sim_info['is_duplicate'] and sim_info['similarity_score'] > highest_score:
                highest_score = sim_info['similarity_score']
                best_match = {
                    'master_complaint_id': candidate.get('id'),
                    'master_title': candidate.get('title'),
                    'master_description': candidate.get('description'),
                    'master_created_at': candidate.get('created_at'),
                    'similarity_score': sim_info['similarity_score'],
                    'distance_meters': sim_info['distance_meters'],
                    'reasons': sim_info['reasons']
                }

        return best_match

    def cluster_hotspots(
        self,
        complaints: List[Dict[str, Any]],
        radius_meters: float = 100.0
    ) -> List[Dict[str, Any]]:
        """
        Clusters city complaints into unified geographical hotspots / work orders.
        """
        valid_items = [
            c for c in complaints 
            if c.get('location_lat') is not None and c.get('location_lng') is not None
        ]
        
        clusters = []
        visited = set()

        for i, c1 in enumerate(valid_items):
            cid1 = c1.get('id', str(i))
            if cid1 in visited:
                continue

            current_cluster = [c1]
            visited.add(cid1)

            lat1 = float(c1['location_lat'])
            lng1 = float(c1['location_lng'])
            cat1 = c1.get('category') or c1.get('department_code')

            for j, c2 in enumerate(valid_items):
                cid2 = c2.get('id', str(j))
                if cid2 in visited:
                    continue
                
                cat2 = c2.get('category') or c2.get('department_code')
                if cat1 != cat2:
                    continue

                lat2 = float(c2['location_lat'])
                lng2 = float(c2['location_lng'])
                d = haversine_distance_meters(lat1, lng1, lat2, lng2)
                if d <= radius_meters:
                    current_cluster.append(c2)
                    visited.add(cid2)

            # Compute cluster centroid
            lats = [float(item['location_lat']) for item in current_cluster]
            lngs = [float(item['location_lng']) for item in current_cluster]
            centroid_lat = sum(lats) / len(lats)
            centroid_lng = sum(lngs) / len(lngs)

            clusters.append({
                'cluster_id': f"HOTSPOT-{len(clusters) + 1}",
                'category': cat1,
                'centroid_lat': round(centroid_lat, 6),
                'centroid_lng': round(centroid_lng, 6),
                'complaint_count': len(current_cluster),
                'complaints': [item.get('id') for item in current_cluster],
                'primary_title': current_cluster[0].get('title'),
                'address_sample': current_cluster[0].get('location_address')
            })

        # Sort clusters by severity / report count
        clusters.sort(key=lambda x: x['complaint_count'], reverse=True)
        return clusters

_CLUSTERING_ENGINE = None

def get_clustering_engine() -> DuplicateClusteringEngine:
    global _CLUSTERING_ENGINE
    if _CLUSTERING_ENGINE is None:
        _CLUSTERING_ENGINE = DuplicateClusteringEngine()
    return _CLUSTERING_ENGINE
