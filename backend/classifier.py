import os
import io
import re
import base64
import joblib
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "complaint_classifier", "nexciv_multimodal_priority_model.pkl"
)
FALLBACK_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "complaint_classifier", "complaint_classifier.pkl"
)

DEPARTMENTS = {
    'road': {
        'name': 'Roads & Buildings Department (R&B / Municipal)',
        'code': 'road',
        'short': 'Roads & Buildings',
        'head': 'Superintending Engineer (R&B / Municipal Corporation)'
    },
    'drainage': {
        'name': 'Public Health & Drainage Department',
        'code': 'drainage',
        'short': 'Drainage & Sewerage',
        'head': 'Executive Engineer (Public Health & Sewerage)'
    },
    'water_supply': {
        'name': 'Water Supply & Quality Department',
        'code': 'water_supply',
        'short': 'Water Supply Board',
        'head': 'Chief Water Works Engineer (CPWS / Municipal)'
    },
    'street_lights': {
        'name': 'Electrical & Street Lighting Wing',
        'code': 'street_lights',
        'short': 'Electrical & Lighting',
        'head': 'Executive Engineer (APEPDCL / APSPDCL / Municipal)'
    },
    'others': {
        'name': 'Sanitation & Solid Waste Management Wing',
        'code': 'others',
        'short': 'Sanitation & SWM',
        'head': 'Chief Municipal Health Officer (CMHO)'
    }
}

WING_LABELS = {code: info['name'] for code, info in DEPARTMENTS.items()}

PRIORITY_LEVELS = {
    'Critical': 4,
    'High': 3,
    'Medium': 2,
    'Low': 1
}

LEVEL_TO_PRIORITY = {4: 'Critical', 3: 'High', 2: 'Medium', 1: 'Low'}

ZONE_KEYWORDS = {
    'hospital': [
        'hospital', 'emergency', 'ambulance', 'clinic', 'trauma', 'medical center',
        'icu', 'casualty', 'dispensary', 'healthcare', 'kgh', 'ggh', 'ruia', 'svims',
        'aiims', 'phc', 'chc', 'apollo', 'care hospital', 'manipal', 'vaidya vidhana parishad'
    ],
    'school': [
        'school', 'college', 'university', 'kindergarten', 'campus', 'institute',
        'children', 'playground', 'academy', 'vidyalaya', 'zp high school', 'mpp school',
        'andhra university', 'svu', 'jntu', 'iiit', 'sri chaitanya', 'narayana', 'bhashyam'
    ],
    'highway': [
        'highway', 'expressway', 'flyover', 'outer ring road', 'arterial',
        'junction', 'toll gate', 'bridge', 'bypass', 'underpass', 'freeway',
        'nh-16', 'nh-65', 'nh-44', 'ah45', 'benz circle', 'kanaka durga',
        'ghat road', 'r&b road', 'bt road', 'cc road'
    ],
    'transit_hub': [
        'metro station', 'railway', 'bus terminal', 'bus stand', 'airport',
        'interchange', 'depot', 'subway station', 'rtc bus stand', 'apsrtc',
        'pnbs', 'visakhapatnam junction', 'vijayawada junction', 'tirupati central', 'rythu bazaar'
    ]
}

AP_PROXIMITY_HUBS = [
    {'name': 'King George Hospital (KGH) Vizag', 'lat': 17.7102, 'lng': 83.3050, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'Government General Hospital (GGH) Vijayawada', 'lat': 16.5120, 'lng': 80.6270, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'AIIMS Mangalagiri Emergency Zone', 'lat': 16.4420, 'lng': 80.5640, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 2.0},
    {'name': 'SVIMS & Ruia Hospital Tirupati', 'lat': 13.6380, 'lng': 79.4080, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'Andhra University Campus Siripuram', 'lat': 17.7290, 'lng': 83.3190, 'zone_type': 'school', 'mult': 1.35, 'radius_km': 1.2},
    {'name': 'Benz Circle NH-16 Highway Vijayawada', 'lat': 16.4990, 'lng': 80.6540, 'zone_type': 'highway', 'mult': 1.30, 'radius_km': 1.5},
    {'name': 'Kanaka Durga Flyover Approach Vijayawada', 'lat': 16.5170, 'lng': 80.6130, 'zone_type': 'highway', 'mult': 1.30, 'radius_km': 1.5},
    {'name': 'Pandit Nehru Bus Station (PNBS) Vijayawada', 'lat': 16.5080, 'lng': 80.6210, 'zone_type': 'transit_hub', 'mult': 1.25, 'radius_km': 1.2},
    {'name': 'Maddilapalem Bus Complex Vizag', 'lat': 17.7340, 'lng': 83.3240, 'zone_type': 'transit_hub', 'mult': 1.25, 'radius_km': 1.2}
]

def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return float(R * c)


class ComplaintClassifier:
    """Singleton classifier that loads the trained multimodal model and provides predictions."""

    _instance = None
    _bundle = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self):
        if self._bundle is None:
            for p in [MODEL_PATH, FALLBACK_MODEL_PATH]:
                if os.path.exists(p):
                    try:
                        self._bundle = joblib.load(p)
                        print(f"Model loaded successfully from {p}")
                        return
                    except Exception as e:
                        print(f"Warning: Could not load model from {p}: {e}")
            print("Classifier will fall back to default civic heuristics.")

    def _resolve_location(
        self,
        location_address: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """Resolves location vulnerability multiplier based on sensitive zoning and AP GPS coordinates."""
        zone_type = 'residential'
        multiplier = 1.00
        resolved_address = location_address or "Location Coordinates"

        # Check 1: GPS Proximity to known AP sensitive infrastructure
        if location_lat is not None and location_lng is not None:
            try:
                for hub in AP_PROXIMITY_HUBS:
                    dist = _haversine_distance_km(location_lat, location_lng, hub['lat'], hub['lng'])
                    if dist <= hub['radius_km']:
                        if hub['mult'] > multiplier:
                            zone_type = hub['zone_type']
                            multiplier = hub['mult']
                            if not location_address or location_address == "Location Coordinates":
                                resolved_address = f"Near {hub['name']} ({dist:.2f} km)"
            except Exception as e:
                print(f"Proximity calculation warning: {e}")

        # Check 2: Semantic text keywords in address or landmark name
        search_text = f"{resolved_address} {location_address or ''}".lower()
        
        for z_type, kw_list in ZONE_KEYWORDS.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', search_text) for kw in kw_list):
                if z_type == 'hospital':
                    zone_type = 'hospital'
                    multiplier = max(multiplier, 1.50)
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

        return {
            'resolved_address': resolved_address,
            'zone_type': zone_type,
            'vulnerability_multiplier': multiplier,
            'location_lat': location_lat,
            'location_lng': location_lng
        }

    def _analyze_image(self, image_data) -> dict:
        """Analyze civic complaint image using PIL for visual severity and characteristics."""
        try:
            if isinstance(image_data, str):
                if image_data.startswith('data:'):
                    image_data = image_data.split(',')[1]
                raw_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(raw_bytes)).convert('RGB')
            elif isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data)).convert('RGB')
            elif isinstance(image_data, Image.Image):
                img = image_data
            else:
                return {}

            gray = np.array(img.convert('L'))
            std_contrast = float(np.std(gray))
            mean_brightness = float(np.mean(gray))

            heuristic_score = min(100.0, std_contrast * 1.3)
            if mean_brightness < 35:
                heuristic_score = max(heuristic_score, 80.0)

            visual_score = round(heuristic_score, 1)
            visual_priority = 'Medium'
            if visual_score >= 80:
                visual_priority = 'Critical'
            elif visual_score >= 60:
                visual_priority = 'High'
            elif visual_score >= 35:
                visual_priority = 'Medium'
            else:
                visual_priority = 'Low'

            return {
                'visual_score': visual_score,
                'visual_priority': visual_priority,
                'contrast': std_contrast,
                'brightness': mean_brightness
            }
        except Exception as e:
            print(f"Image analysis warning: {e}")
            return {}

    def classify_complaint(
        self,
        text: str,
        image_data=None,
        location_address: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lng: Optional[float] = None
    ) -> dict:
        """
        Multimodal classification of civic complaint into Department and Priority Score.
        Evaluates Text, Picture, and Location context.
        """
        if self._bundle is None:
            self.load_model()

        wing = 'others'
        wing_confidence = 0.5
        priority = 'Medium'
        priority_confidence = 0.5
        all_probabilities = {code: 0.2 for code in DEPARTMENTS.keys()}
        top_keywords = []
        text_score = 50.0

        if self._bundle is not None:
            try:
                if isinstance(self._bundle, dict) and ('wing_pipeline' in self._bundle or 'pipeline' in self._bundle):
                    wing_pipe = self._bundle.get('wing_pipeline') or self._bundle.get('pipeline')
                    prio_pipe = self._bundle.get('prio_pipeline') or self._bundle.get('priority_pipeline')

                    if text and text.strip():
                        clean_text = text.strip()
                        wing = wing_pipe.predict([clean_text])[0]
                        w_probs = wing_pipe.predict_proba([clean_text])[0]
                        wing_confidence = float(np.max(w_probs))

                        # Build probabilities map for all departments
                        classes = wing_pipe.classes_
                        all_probabilities = {
                            str(cls): round(float(prob), 4)
                            for cls, prob in zip(classes, w_probs)
                        }

                        priority = prio_pipe.predict([clean_text])[0]
                        p_probs = prio_pipe.predict_proba([clean_text])[0]
                        priority_confidence = float(np.max(p_probs))

                        prio_base_weights = {'Critical': 90.0, 'High': 75.0, 'Medium': 50.0, 'Low': 25.0}
                        text_score = prio_base_weights[priority] * priority_confidence + (1.0 - priority_confidence) * 50.0

                        # Extract salient feature words from TF-IDF vectorizer
                        try:
                            tfidf = wing_pipe.named_steps['tfidf']
                            feature_names = tfidf.get_feature_names_out()
                            vec = tfidf.transform([clean_text])
                            nonzeros = vec.nonzero()[1]
                            sorted_idx = sorted(nonzeros, key=lambda idx: vec[0, idx], reverse=True)
                            top_keywords = [str(feature_names[idx]) for idx in sorted_idx[:5]]
                        except Exception:
                            top_keywords = []
                else:
                    if text and text.strip():
                        wing = self._bundle.predict([text])[0]
                        probs = self._bundle.predict_proba([text])[0]
                        wing_confidence = float(np.max(probs))
            except Exception as e:
                print(f"Prediction error: {e}")

        # 1. Computer vision evaluation
        image_meta = {}
        visual_score = None
        if image_data:
            image_meta = self._analyze_image(image_data)
            visual_score = image_meta.get('visual_score')

        # 2. Location intelligence evaluation
        loc_meta = self._resolve_location(
            location_address=location_address,
            location_lat=location_lat,
            location_lng=location_lng
        )
        vuln_mult = loc_meta['vulnerability_multiplier']

        # 3. Multimodal Fusion Calculation
        if visual_score is not None:
            base_score = 0.60 * text_score + 0.40 * visual_score
        else:
            base_score = text_score

        scaled_score = base_score * vuln_mult

        # Safety-First Dynamic Escalation
        escalated = False
        if (priority == 'Critical' or (visual_score and visual_score >= 80)) and vuln_mult >= 1.30:
            scaled_score = max(scaled_score, 95.0)
            escalated = True

        final_score = round(min(100.0, max(0.0, scaled_score)), 1)

        # Determine Final Priority Tier & Municipal Response SLA
        if final_score >= 88:
            final_prio = 'Critical'
            sla_hours = '0 - 4 Hours (Emergency Dispatch)'
        elif final_score >= 68:
            final_prio = 'High'
            sla_hours = '24 Hours (Next Shift Field Team)'
        elif final_score >= 40:
            final_prio = 'Medium'
            sla_hours = '48 - 72 Hours (Standard Municipal Maintenance)'
        else:
            final_prio = 'Low'
            sla_hours = '5 - 7 Days (Scheduled Routine Maintenance)'

        dept_info = DEPARTMENTS.get(wing, DEPARTMENTS['others'])

        return {
            'wing': wing,
            'wing_label': dept_info['name'],
            'wing_confidence': wing_confidence,
            'priority': final_prio,
            'priority_confidence': priority_confidence,
            'priority_score': final_score,
            'category': wing,
            'confidence': wing_confidence,
            'department': dept_info['name'],
            'department_code': dept_info['code'],
            'department_head': dept_info['head'],
            'all_probabilities': all_probabilities,
            'top_keywords': top_keywords,
            'image_analysis': image_meta,
            'location_info': loc_meta,
            'municipal_sla': sla_hours,
            'safety_escalation_applied': escalated
        }


def get_classifier() -> ComplaintClassifier:
    """FastAPI dependency to get the classifier singleton."""
    classifier = ComplaintClassifier()
    classifier.load_model()
    return classifier


if __name__ == "__main__":
    clf = get_classifier()
    res1 = clf.classify_complaint(
        text="Deep dangerous pothole crater in the road causing vehicle damage.",
        location_address="Outside City Hospital Emergency Casualty Corridor"
    )
    print("\n--- HOSPITAL CORRIDOR TEST ---")
    print(f"Department: {res1['department']}")
    print(f"Priority:   {res1['priority']} (Score: {res1['priority_score']} / 100)")
    print(f"Zone Type:  {res1['location_info']['zone_type']} ({res1['location_info']['vulnerability_multiplier']}x)")
    print(f"SLA:        {res1['municipal_sla']}")

    res2 = clf.classify_complaint(
        text="Deep dangerous pothole crater in the road causing vehicle damage.",
        location_address="7th Cross Residential Layout Cul-de-sac"
    )
    print("\n--- RESIDENTIAL CUL-DE-SAC TEST ---")
    print(f"Department: {res2['department']}")
    print(f"Priority:   {res2['priority']} (Score: {res2['priority_score']} / 100)")
    print(f"Zone Type:  {res2['location_info']['zone_type']} ({res2['location_info']['vulnerability_multiplier']}x)")
    print(f"SLA:        {res2['municipal_sla']}")
