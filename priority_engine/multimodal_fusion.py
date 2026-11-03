"""
NEX-CIV Multimodal Feature Fusion Engine
Integrates:
1. Multilingual Text (Telugu, English, Code-Mixed)
2. Computer Vision / Image Modality (Damage severity, edge entropy, contrast, brightness)
3. Geospatial Zone & Location (Hospital, School, Highway, Transit Hub, Ward, GPS)
4. Civic & Administrative Meta (Statutory SLA, Citizens Affected, Safety/Health Hazards)
"""

import io
import re
import math
import base64
import numpy as np
from typing import Dict, Any, Optional, Tuple, List, Union
from PIL import Image, ImageFilter, ImageStat

# Authentic Andhra Pradesh & Indian Sensitive Zone Benchmarks
ZONE_KEYWORDS = {
    'hospital': [
        'hospital', 'emergency', 'ambulance', 'clinic', 'trauma', 'medical center',
        'icu', 'casualty', 'dispensary', 'healthcare', 'kgh', 'ggh', 'ruia', 'svims',
        'aiims', 'phc', 'chc', 'apollo', 'care hospital', 'manipal', 'ఆసుపత్రి', 'వైద్యశాల', 'ఎమర్జెన్సీ'
    ],
    'school': [
        'school', 'college', 'university', 'kindergarten', 'campus', 'institute',
        'children', 'playground', 'academy', 'vidyalaya', 'zp high school', 'mpp school',
        'andhra university', 'svu', 'jntu', 'iiit', 'పాఠశాల', 'బడి', 'కళాశాల'
    ],
    'highway': [
        'highway', 'expressway', 'flyover', 'outer ring road', 'arterial',
        'junction', 'toll gate', 'bridge', 'bypass', 'underpass', 'freeway',
        'nh-16', 'nh-65', 'nh-44', 'benz circle', 'kanaka durga', 'ghat road', 'రహదారి', 'ఫ్లైఓవర్'
    ],
    'transit_hub': [
        'metro station', 'railway', 'bus terminal', 'bus stand', 'airport',
        'interchange', 'depot', 'rtc bus stand', 'apsrtc', 'pnbs', 'బస్ స్టాండ్', 'రైల్వే'
    ]
}

# Municipal Coordinates Reference (Centroids)
MUNICIPALITY_CENTROIDS = {
    'ELR': {'lat': 16.7107, 'lng': 81.0952, 'name': 'Eluru Municipal Corporation'},
    'VMC': {'lat': 16.5062, 'lng': 80.6480, 'name': 'Vijayawada Municipal Corporation'},
    'GMC': {'lat': 16.3067, 'lng': 80.4365, 'name': 'Guntur Municipal Corporation'},
    'GVMC': {'lat': 17.6868, 'lng': 83.2185, 'name': 'Greater Visakhapatnam Municipal Corporation'},
    'TMC': {'lat': 13.6288, 'lng': 79.4192, 'name': 'Tirupati Municipal Corporation'},
    'KMC': {'lat': 15.8281, 'lng': 78.0373, 'name': 'Kurnool Municipal Corporation'},
    'NMC': {'lat': 14.4426, 'lng': 79.9865, 'name': 'Nellore Municipal Corporation'},
    'KKD': {'lat': 16.9891, 'lng': 82.2475, 'name': 'Kakinada Municipal Corporation'}
}

# Visual signatures by defect category for computer vision feature synthesis/extraction
CIVIC_VISUAL_SIGNATURES = {
    'road': {'brightness': 0.38, 'contrast': 0.55, 'edge_density': 0.72, 'severity': 65.0},
    'street_lights': {'brightness': 0.15, 'contrast': 0.78, 'edge_density': 0.82, 'severity': 60.0},
    'drainage': {'brightness': 0.28, 'contrast': 0.60, 'edge_density': 0.68, 'severity': 70.0},
    'water_supply': {'brightness': 0.62, 'contrast': 0.45, 'edge_density': 0.50, 'severity': 68.0},
    'others': {'brightness': 0.48, 'contrast': 0.62, 'edge_density': 0.70, 'severity': 50.0}
}


def extract_vision_features_from_image(image_input: Any) -> Dict[str, float]:
    """
    Extracts computer vision features directly from PIL image, base64 data, or image bytes:
    - visual_severity_score (0.0 to 100.0)
    - edge_density (0.0 to 1.0)
    - contrast_ratio (0.0 to 1.0)
    - brightness_level (0.0 to 1.0)
    """
    try:
        img = None
        if isinstance(image_input, Image.Image):
            img = image_input.convert('RGB')
        elif isinstance(image_input, (bytes, bytearray)):
            img = Image.open(io.BytesIO(image_input)).convert('RGB')
        elif isinstance(image_input, str) and len(image_input) > 50:
            raw = image_input
            if raw.startswith('data:'):
                raw = raw.split(',')[1]
            raw_bytes = base64.b64decode(raw)
            img = Image.open(io.BytesIO(raw_bytes)).convert('RGB')

        if img is not None:
            # Resize for fast feature extraction
            small = img.resize((128, 128))
            stat = ImageStat.Stat(small)
            mean_brightness = float(np.mean(stat.mean) / 255.0)
            contrast = float(np.mean(stat.stddev) / 100.0)

            # Edge detection filter
            edges = small.convert('L').filter(ImageFilter.FIND_EDGES)
            edge_arr = np.array(edges)
            edge_density = float(np.count_nonzero(edge_arr > 35) / edge_arr.size)

            # Visual damage severity heuristic
            severity = float(np.clip((edge_density * 60.0) + (contrast * 40.0), 10.0, 98.0))

            return {
                'visual_severity_score': round(severity, 2),
                'edge_density': round(edge_density, 3),
                'contrast_ratio': round(contrast, 3),
                'brightness_level': round(mean_brightness, 3),
                'has_image_proof': 1.0
            }
    except Exception:
        pass

    return {
        'visual_severity_score': 0.0,
        'edge_density': 0.0,
        'contrast_ratio': 0.0,
        'brightness_level': 0.0,
        'has_image_proof': 0.0
    }


def synthesize_vision_features_for_defect(category: str, severity_level: int = 2) -> Dict[str, float]:
    """Synthesizes authentic vision features when training on records without raw image bytes."""
    sig = CIVIC_VISUAL_SIGNATURES.get(category.lower(), CIVIC_VISUAL_SIGNATURES['others'])
    level_scale = severity_level / 2.0
    sev = np.clip(sig['severity'] * level_scale + np.random.normal(0, 4.0), 10.0, 98.0)
    edge = np.clip(sig['edge_density'] * (0.8 + 0.2 * level_scale) + np.random.normal(0, 0.04), 0.05, 0.95)
    contrast = np.clip(sig['contrast'] + np.random.normal(0, 0.03), 0.1, 0.95)
    brightness = np.clip(sig['brightness'] + np.random.normal(0, 0.03), 0.05, 0.95)

    return {
        'visual_severity_score': round(float(sev), 2),
        'edge_density': round(float(edge), 3),
        'contrast_ratio': round(float(contrast), 3),
        'brightness_level': round(float(brightness), 3),
        'has_image_proof': 1.0
    }


def normalize_municipality_code(muni_input: Optional[str]) -> str:
    """Normalizes any municipal corporation representation to its 3-letter ULB code."""
    raw = (muni_input or 'ELR').strip().upper()
    if 'ELURU' in raw or raw == 'ELR':
        return 'ELR'
    if 'VIJAYA' in raw or raw == 'VMC':
        return 'VMC'
    if 'GUNTUR' in raw or raw == 'GMC':
        return 'GMC'
    if 'VISAKHA' in raw or 'GVMC' in raw:
        return 'GVMC'
    if 'TIRUPATI' in raw or raw == 'TMC':
        return 'TMC'
    if 'KURNOOL' in raw or raw == 'KMC':
        return 'KMC'
    if 'NELLORE' in raw or raw == 'NMC':
        return 'NMC'
    if 'KAKINADA' in raw or raw == 'KKD':
        return 'KKD'
    return 'ELR'


def resolve_zone_features(
    text: str,
    location_name: Optional[str] = None,
    ward: Optional[str] = None,
    municipality: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Dict[str, Any]:
    """
    Extracts Geospatial Zone features:
    - zone_type: hospital, school, highway, transit_hub, residential
    - vulnerability_multiplier: 1.50 (hospital), 1.35 (school), 1.30 (highway), 1.25 (transit), 1.00 (residential)
    - ward_num: numeric ward identifier
    - normalized lat, lng
    - standardized 3-letter municipality_code
    """
    combined = f"{text or ''} {location_name or ''} {ward or ''}".lower()
    
    zone_type = 'residential'
    multiplier = 1.00

    for z_type, kws in ZONE_KEYWORDS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', combined) for kw in kws):
            if z_type == 'hospital':
                zone_type = 'hospital'
                multiplier = 1.50
                break
            elif z_type == 'school' and multiplier < 1.35:
                zone_type = 'school'
                multiplier = 1.35
            elif z_type == 'highway' and multiplier < 1.30:
                zone_type = 'highway'
                multiplier = 1.30
            elif z_type == 'transit_hub' and multiplier < 1.25:
                zone_type = 'transit_hub'
                multiplier = 1.25

    # Extract ward number
    ward_num = 1
    if ward:
        digits = re.findall(r'\b\d+\b', str(ward))
        if digits:
            ward_num = int(digits[0])

    # Geocode coordinates if missing
    muni_key = normalize_municipality_code(municipality)
    centroid = MUNICIPALITY_CENTROIDS.get(muni_key, MUNICIPALITY_CENTROIDS['ELR'])
    final_lat = float(lat) if lat is not None else centroid['lat']
    final_lng = float(lng) if lng is not None else centroid['lng']

    return {
        'zone_type': zone_type,
        'vulnerability_multiplier': multiplier,
        'ward_num': ward_num,
        'latitude': final_lat,
        'longitude': final_lng,
        'municipality_code': muni_key
    }
