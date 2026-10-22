import os
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from vision_engine import CivicVisionEngine
from clustering import DuplicateClusteringEngine, haversine_distance_meters

def create_synthetic_road_image(defect: str = 'pothole') -> Image.Image:
    """Creates a synthetic photo representing real road defects for testing."""
    # Base asphalt texture (gray with noise)
    arr = np.random.normal(loc=110, scale=18, size=(200, 200)).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(arr, mode='L').convert('RGB')
    draw = ImageDraw.Draw(img)

    if defect == 'pothole':
        # Dark recessed crater in the center with jagged edges
        draw.ellipse([60, 60, 140, 140], fill=(25, 25, 25))
        draw.ellipse([70, 70, 130, 130], fill=(12, 12, 12))
        # Draw radial crack lines emanating outward
        draw.line([60, 100, 20, 80], fill=(15, 15, 15), width=2)
        draw.line([140, 100, 180, 120], fill=(15, 15, 15), width=2)
        draw.line([100, 60, 90, 20], fill=(15, 15, 15), width=2)
    elif defect == 'blank':
        # Blank solid color (simulating user uploading accidental white/blank screenshot)
        return Image.new('RGB', (200, 200), color=(250, 250, 250))

    return img.filter(ImageFilter.GaussianBlur(radius=0.5))


def run_phase2_tests():
    print("\n" + "="*85)
    print("NEXCIV PHASE 2: COMPUTER VISION & DUPLICATE CLUSTERING VERIFICATION SUITE")
    print("="*85)

    vision_engine = CivicVisionEngine()
    clustering_engine = DuplicateClusteringEngine()

    # -------------------------------------------------------------
    # TEST 1: COMPUTER VISION DEFECT VERIFICATION & SEVERITY SCORING
    # -------------------------------------------------------------
    print("\n[TEST 1: Computer Vision Authenticity & Severity Analysis]")
    pothole_img = create_synthetic_road_image('pothole')
    blank_img = create_synthetic_road_image('blank')

    res_pothole = vision_engine.verify_and_analyze_image(pothole_img)
    print(f"  Valid Pothole Image:")
    print(f"    - Authenticity Passed:  {res_pothole['authenticity_passed']}")
    print(f"    - Detected Defect:      {res_pothole['defect_type']}")
    print(f"    - Visual Severity:      {res_pothole['visual_severity_score']} / 100 ({res_pothole['visual_priority_tier']})")
    print(f"    - Confidence:           {res_pothole['visual_confidence']*100:.1f}%")
    print(f"    - Perceptual Hash:      {res_pothole['image_hash']}")

    assert res_pothole['authenticity_passed'] is True, "Pothole should pass authenticity check!"
    assert res_pothole['visual_severity_score'] >= 60.0, "Pothole severity should be High/Critical!"

    res_blank = vision_engine.verify_and_analyze_image(blank_img)
    print(f"  Spam/Blank Image:")
    print(f"    - Authenticity Passed:  {res_blank['authenticity_passed']}")
    print(f"    - Rejection Reason:     {res_blank.get('rejection_reason')}")
    assert res_blank['authenticity_passed'] is False, "Blank image should be rejected!"
    print("  --> TEST 1 PASSED: Defect verified and spam filter working.")

    # -------------------------------------------------------------
    # TEST 2: PERCEPTUAL IMAGE HASHING (INVARIANCE TO NOISE / RESIZE)
    # -------------------------------------------------------------
    print("\n[TEST 2: Perceptual Image Fingerprinting (dHash)]")
    hash1 = res_pothole['image_hash']
    # Create slight variation of same image (e.g. resized + slightly blurred)
    variant_img = pothole_img.resize((160, 160)).filter(ImageFilter.GaussianBlur(0.6))
    hash2 = vision_engine.compute_perceptual_hash(variant_img)
    
    hamming_dist = vision_engine.hamming_distance(hash1, hash2)
    visual_sim = vision_engine.visual_similarity_from_hashes(hash1, hash2)
    print(f"    - Original Hash:        {hash1}")
    print(f"    - Variant Hash:         {hash2}")
    print(f"    - Hamming Distance:     {hamming_dist} bits (out of 64)")
    print(f"    - Visual Match Score:   {visual_sim * 100:.1f}%")

    assert visual_sim >= 0.85, "Same defect image variant must yield high perceptual similarity!"
    print("  --> TEST 2 PASSED: Perceptual hashing robust against minor image perturbations.")

    # -------------------------------------------------------------
    # TEST 3: GEOSPATIAL & MULTIMODAL DUPLICATE COMPLAINT DETECTION
    # -------------------------------------------------------------
    print("\n[TEST 3: Multimodal Duplicate Detection at Benz Circle, Vijayawada]")
    
    # Existing Master Complaint
    master_complaint = {
        'id': 'M-101',
        'title': 'Dangerous deep pothole on NH-16 Benz Circle flyover approach',
        'description': 'Large road crater on the fast lane causing two-wheelers to skid and heavy traffic bottleneck.',
        'category': 'road',
        'location_lat': 16.4990,
        'location_lng': 80.6540,
        'location_address': 'Benz Circle Flyover, Vijayawada',
        'image_hash': hash1,
        'status': 'pending'
    }

    # Case A: Same pothole submitted 30 minutes later by another citizen 22 meters away
    dup_report = {
        'id': 'D-202',
        'title': 'Huge road crater near Benz Circle',
        'description': 'Deep pothole on flyover road, vehicle tires taking heavy damage, repair immediately.',
        'category': 'road',
        'location_lat': 16.49915,
        'location_lng': 80.65415,  # ~22 meters away
        'location_address': 'NH-16 near Benz Circle, Vijayawada',
        'image_hash': hash2,
        'status': 'pending'
    }

    sim_res = clustering_engine.calculate_pair_similarity(dup_report, master_complaint)
    print(f"  Case A (Duplicate Pothole 22m away with matching photo):")
    print(f"    - Distance:             {sim_res['distance_meters']:.1f} meters")
    print(f"    - Composite Similarity: {sim_res['similarity_score'] * 100:.1f}%")
    print(f"    - Is Duplicate:         {sim_res['is_duplicate']}")
    print(f"    - Reasons Detected:     {', '.join(sim_res['reasons'])}")

    assert sim_res['is_duplicate'] is True, "Case A must be detected as a duplicate!"
    assert sim_res['similarity_score'] >= 0.80, "Case A similarity score must be >= 80%!"

    # Case B: Completely different location (KGH Hospital Visakhapatnam, 350 km away)
    distant_report = {
        'id': 'R-303',
        'title': 'Pothole near KGH casualty ward gate',
        'description': 'Pothole on hospital approach road.',
        'category': 'road',
        'location_lat': 17.7102,
        'location_lng': 83.3050,  # ~350 km away
        'location_address': 'KGH Hospital Gate, Visakhapatnam',
        'image_hash': hash1,
        'status': 'pending'
    }
    sim_distant = clustering_engine.calculate_pair_similarity(distant_report, master_complaint)
    print(f"\n  Case B (Same description & photo but in Visakhapatnam, 350 km away):")
    print(f"    - Distance:             {sim_distant['distance_meters'] / 1000:.1f} km")
    print(f"    - Composite Similarity: {sim_distant['similarity_score'] * 100:.1f}%")
    print(f"    - Is Duplicate:         {sim_distant['is_duplicate']}")
    assert sim_distant['is_duplicate'] is False, "Case B in another city must NOT be a duplicate!"

    # Case C: Same GPS location but different category (Streetlight vs Road Pothole)
    diff_cat_report = {
        'id': 'E-404',
        'title': 'Streetlight pole sparking in rain',
        'description': 'Electrical wire loose on lighting pole near Benz Circle.',
        'category': 'street_lights',
        'location_lat': 16.4990,
        'location_lng': 80.6540,
        'location_address': 'Benz Circle, Vijayawada',
        'image_hash': '0000000000000000',
        'status': 'pending'
    }
    sim_diff_cat = clustering_engine.calculate_pair_similarity(diff_cat_report, master_complaint)
    print(f"\n  Case C (Same location but Streetlight complaint vs Road Pothole):")
    print(f"    - Composite Similarity: {sim_diff_cat['similarity_score'] * 100:.1f}%")
    print(f"    - Is Duplicate:         {sim_diff_cat['is_duplicate']}")
    print(f"    - Reason:               {', '.join(sim_diff_cat['reasons'])}")
    assert sim_diff_cat['is_duplicate'] is False, "Different municipal wings must NOT merge!"
    print("  --> TEST 3 PASSED: Duplicate detection accurately identifies duplicates without false positives.")

    # -------------------------------------------------------------
    # TEST 4: CITY-WIDE HOTSPOT CLUSTERING
    # -------------------------------------------------------------
    print("\n[TEST 4: Hotspot Clustering (Combining multiple reports into Work Orders)]")
    pool = [
        master_complaint,
        dup_report,
        {
            'id': 'D-203',
            'title': 'Benz Circle road broken',
            'category': 'road',
            'location_lat': 16.49908,
            'location_lng': 80.65405,
            'location_address': 'Benz Circle',
            'status': 'pending'
        },
        distant_report,
        {
            'id': 'R-304',
            'title': 'KGH road damage near casualty',
            'category': 'road',
            'location_lat': 17.71025,
            'location_lng': 83.30510,
            'location_address': 'KGH Maharanipeta',
            'status': 'pending'
        }
    ]

    hotspots = clustering_engine.cluster_hotspots(pool, radius_meters=100.0)
    print(f"  Clustered {len(pool)} complaints into {len(hotspots)} distinct ULB Hotspots:")
    for h in hotspots:
        print(f"    - {h['cluster_id']} ({h['category'].upper()}): {h['complaint_count']} complaints merged at ({h['centroid_lat']}, {h['centroid_lng']})")
    
    assert len(hotspots) == 2, "Expected exactly 2 hotspots: Benz Circle (3 reports) and KGH (2 reports)!"
    assert hotspots[0]['complaint_count'] == 3, "Benz Circle hotspot should contain 3 merged reports!"
    print("  --> TEST 4 PASSED: Hotspot clustering accurately consolidated regional incident work orders.")

    print("\n" + "="*85)
    print("ALL PHASE 2 COMPUTER VISION & CLUSTERING TESTS PASSED SUCCESSFULLY!")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_phase2_tests()
