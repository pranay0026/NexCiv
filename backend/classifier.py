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


MULTILINGUAL_INTENT_RULES = {
    'water_supply': {
        'pure_telugu': [
            r'నీళ్లు', r'నీరు', r'నీటి', r'తాగునీరు', r'మంచినీరు', r'పైప్‌లైన్', r'పైపు',
            r'కుళాయి', r'బోరు', r'మోటారు', r'నీటి సమస్య', r'నీటి కొరత', r'నీటి సరఫరా',
            r'నీటి లీకేజీ', r'నీళ్లు రావడం లేదు', r'నీటి కాలుష్యం'
        ],
        'romanized': [
            r'\bnelu\b', r'\bneelu\b', r'\bneellu\b', r'\bneeru\b', r'\bneeti\b',
            r'\btaguneeru\b', r'\btaaguneeru\b', r'\bmanchineellu\b', r'\bravadham\b',
            r'\bravatledu\b', r'\bravadam ledu\b', r'\bravatam ledu\b', r'\bneellu levu\b',
            r'\bdrinking water\b', r'\bwater problem\b', r'\bwater shortage\b',
            r'\bpipeline\b', r'\bpaipu\b', r'\bkulaayi\b', r'\bkulayi\b', r'\bborewell\b'
        ],
        'english': [
            r'\bwater\b', r'\bdrinking water\b', r'\bpipeline\b', r'\bleakage\b',
            r'\btap\b', r'\bwater supply\b', r'\bshortage\b', r'\bcontamination\b',
            r'\bwater tank\b', r'\bborewell\b', r'\blow pressure\b', r'\bno water\b'
        ],
        'subtypes': [
            ('pipeline_leakage', [r'leakage', r'leak', r'burst', r'pagilipoindi', r'లీకేజ్', r'లీకేజీ', r'పగిలిపోయింది']),
            ('water_contamination', [r'contamination', r'contaminated', r'dirty', r'smell', r'మురికి', r'కాలుష్య']),
            ('low_water_pressure', [r'low pressure', r'pressure', r'thakkuva', r'తక్కువ ప్రెషర్']),
            ('no_water_supply', [r'ravatledu', r'ravadham ledu', r'ravadam ledu', r'levu', r'shortage', r'no water', r'రావడం లేదు', r'రాలేదు', r'కొరత', r'ఆగిపోయింది', r'రెండు రోజులు'])
        ],
        'default_subtype': 'no_water_supply'
    },
    'drainage': {
        'pure_telugu': [
            r'డ్రైనేజీ', r'డ్రైనేజి', r'మురుగు', r'మురుగునీరు', r'కాలువ', r'మ్యాన్‌హోల్',
            r'పొంగిపొర్లు', r'మురుగు కాలువ', r'సెప్టిక్', r'గట్టర్'
        ],
        'romanized': [
            r'\bdrainage\b', r'\bdrain\b', r'\bmurugu\b', r'\bmuruguneeru\b', r'\bkaluva\b',
            r'\bmanhole\b', r'\bponguthondi\b', r'\bpongiporluthondi\b', r'\bsewage\b', r'\bgutter\b'
        ],
        'english': [
            r'\bdrain\b', r'\bdrainage\b', r'\bsewer\b', r'\bsewerage\b', r'\boverflow\b',
            r'\bmanhole\b', r'\bgutter\b', r'\bsewage leakage\b', r'\bclogged\b'
        ],
        'subtypes': [
            ('open_manhole', [r'open manhole', r'manhole open', r'మూత లేదు', r'తెరిచి ఉంది']),
            ('blocked_drainage', [r'blocked', r'clogged', r'choke', r'జామ్', r'బ్లాక్']),
            ('sewage_leakage', [r'leakage', r'leak', r'లీక్']),
            ('drainage_overflow', [r'overflow', r'ponguthondi', r'pongiporluthondi', r'పొంగిపొర్లు', r'పొంగుతోంది'])
        ],
        'default_subtype': 'drainage_overflow'
    },
    'road': {
        'pure_telugu': [
            r'రోడ్డు', r'రోడ్', r'గుంత', r'గుంతలు', r'రహదారి', r'ఫుట్‌పాత్', r'తారు రోడ్డు',
            r'డివైడర్', r'స్పీడ్ బ్రేకర్'
        ],
        'romanized': [
            r'\broad\b', r'\broads\b', r'\bguntha\b', r'\bgunthalu\b', r'\bpothole\b',
            r'\bpotholes\b', r'\basphalt\b', r'\bfootpath\b', r'\bcrater\b', r'\bcraters\b'
        ],
        'english': [
            r'\broad\b', r'\broads\b', r'\bpothole\b', r'\bpotholes\b', r'\bcrater\b',
            r'\bcraters\b', r'\basphalt\b', r'\bfootpath\b', r'\bpavement\b', r'\bflyover\b',
            r'\bspeed breaker\b', r'\bhighway\b'
        ],
        'subtypes': [
            ('footpath_damage', [r'footpath', r'pavement', r'ఫుట్‌పాత్']),
            ('road_obstruction', [r'obstruction', r'tree fell', r'చెట్టు', r'అడ్డంకి']),
            ('damaged_roads', [r'damaged road', r'damage', r'పాడైపోయింది', r'broken']),
            ('potholes', [r'pothole', r'potholes', r'guntha', r'gunthalu', r'crater', r'గుంత', r'గుంతలు'])
        ],
        'default_subtype': 'potholes'
    },
    'street_lights': {
        'pure_telugu': [
            r'స్ట్రీట్ లైట్', r'స్ట్రీట్‌లైట్', r'వీధి దీపాలు', r'దీపాలు', r'కరెంట్',
            r'స్తంభం', r'లైట్లు', r'కరెంట్ వైర్లు', r'ట్రాన్స్‌ఫార్మర్', r'చీకటి'
        ],
        'romanized': [
            r'\bstreet light\b', r'\bstreetlight\b', r'\bstreet lights\b', r'\bdeepalu\b',
            r'\bcurrent\b', r'\bstambham\b', r'\bvelagadam ledu\b', r'\bvelagatam ledu\b',
            r'\bchikatiga\b', r'\bdarkness\b', r'\belectric pole\b', r'\btransformer\b', r'\bwires\b'
        ],
        'english': [
            r'\bstreet light\b', r'\bstreetlight\b', r'\bstreet lights\b', r'\belectric pole\b',
            r'\bdark\b', r'\bdarkness\b', r'\bexposed wire\b', r'\btransformer\b', r'\bpower cut\b',
            r'\bblackout\b', r'\blamp post\b'
        ],
        'subtypes': [
            ('exposed_electrical_wires', [r'wire', r'wires', r'spark', r'షాక్', r'తీగలు', r'exposed']),
            ('damaged_electric_pole', [r'pole', r'stambham', r'వంగిపోయింది', r'కూలిపోయింది', r'damaged pole']),
            ('street_light_failure', [r'velagadam ledu', r'not working', r'off', r'dark', r'చీకటి', r'failure'])
        ],
        'default_subtype': 'street_light_failure'
    },
    'others': {
        'pure_telugu': [
            r'చెత్త', r'వ్యర్థాలు', r'దుర్గంధం', r'స్వచ్ఛ', r'చెత్తకుండీ', r'చచ్చిన జంతువు',
            r'పారిశుధ్యం', r'కంపు', r'డస్ట్‌బిన్'
        ],
        'romanized': [
            r'\bchetha\b', r'\bkachra\b', r'\bdurgandham\b', r'\bgarbage\b', r'\btrash\b',
            r'\bwaste\b', r'\bdustbin\b', r'\bdead animal\b', r'\bswachh\b', r'\bkampu\b'
        ],
        'english': [
            r'\bgarbage\b', r'\btrash\b', r'\bwaste\b', r'\bdump\b', r'\bdustbin\b',
            r'\bdead animal\b', r'\blitter\b', r'\bsanitation\b', r'\bfilth\b', r'\bstench\b'
        ],
        'subtypes': [
            ('dead_animal_removal', [r'dead animal', r'dead dog', r'చచ్చిన జంతువు']),
            ('garbage_collection_failure', [r'collection', r'not collected', r'ethadam ledu']),
            ('public_sanitation_issue', [r'sanitation', r'filth', r'stench', r'దుర్గంధం', r'కంపు']),
            ('garbage_accumulation', [r'garbage', r'trash', r'waste', r'chetha', r'కుప్పలు', r'చెత్త'])
        ],
        'default_subtype': 'garbage_accumulation'
    }
}


class ComplaintClassifier:
    """Singleton classifier that loads the trained multimodal model and provides predictions."""

    _instance = None
    _bundle = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _analyze_multilingual_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        High-precision multilingual intent anchor supporting:
        - Pure Telugu Unicode (నీళ్లు, నీరు, రోడ్డు, డ్రైనేజీ, etc.)
        - Romanized Telugu transliterations (nelu, neellu, ravadham ledu, etc.)
        - English municipal terminology
        """
        if not text or not text.strip():
            return None
        clean = text.lower()
        check_order = ['drainage', 'water_supply', 'street_lights', 'road', 'others']
        for dept in check_order:
            cfg = MULTILINGUAL_INTENT_RULES[dept]
            matches = []
            for pat in cfg['pure_telugu'] + cfg['romanized'] + cfg['english']:
                found = re.findall(pat, clean)
                if found:
                    matches.extend(found)
            if matches:
                chosen_subtype = cfg['default_subtype']
                for stype, stype_pats in cfg['subtypes']:
                    if any(re.search(p, clean) for p in stype_pats):
                        chosen_subtype = stype
                        break
                prio = 'High' if dept in ['water_supply', 'drainage', 'road'] else 'Medium'
                if any(re.search(p, clean) for p in [r'accident', r'hospital', r'hazard', r'fatal', r'burst', r'cyclone', r'తుఫాన్', r'danger', r'casualty']):
                    prio = 'Critical'
                return {
                    'wing': dept,
                    'complaint_type': chosen_subtype,
                    'matched': list(set(matches)),
                    'priority': prio
                }
        return None

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
        complaint_type = 'other_civic_issue'
        complaint_type_conf = 0.5
        priority = 'Medium'
        priority_confidence = 0.5
        all_probabilities = {code: 0.2 for code in DEPARTMENTS.keys()}
        top_keywords = []
        text_score = 50.0

        clean_text = text.strip() if text else ""
        intent = self._analyze_multilingual_intent(clean_text)

        if intent:
            wing = intent['wing']
            wing_confidence = 0.98
            complaint_type = intent['complaint_type']
            complaint_type_conf = 0.96
            priority = intent['priority']
            priority_confidence = 0.95
            all_probabilities = {code: 0.005 for code in DEPARTMENTS.keys()}
            all_probabilities[wing] = 0.98
            top_keywords = intent['matched']
            prio_base_weights = {'Critical': 90.0, 'High': 75.0, 'Medium': 50.0, 'Low': 25.0}
            text_score = prio_base_weights.get(priority, 75.0)
        elif self._bundle is not None:
            try:
                if isinstance(self._bundle, dict) and ('wing_pipeline' in self._bundle or 'pipeline' in self._bundle):
                    wing_pipe = self._bundle.get('wing_pipeline') or self._bundle.get('pipeline')
                    prio_pipe = self._bundle.get('prio_pipeline') or self._bundle.get('priority_pipeline')

                    if clean_text:
                        wing = wing_pipe.predict([clean_text])[0]
                        w_probs = wing_pipe.predict_proba([clean_text])[0]
                        wing_confidence = float(np.max(w_probs))

                        # Build probabilities map for all departments
                        classes = wing_pipe.classes_
                        all_probabilities = {
                            str(cls): round(float(prob), 4)
                            for cls, prob in zip(classes, w_probs)
                        }

                        # Predict Complaint Type if multi-task pipeline present
                        type_pipe = self._bundle.get('complaint_type_pipeline')
                        if type_pipe:
                            try:
                                complaint_type = type_pipe.predict([clean_text])[0]
                                t_probs = type_pipe.predict_proba([clean_text])[0]
                                complaint_type_conf = float(np.max(t_probs))
                            except Exception:
                                pass

                        if prio_pipe is not None:
                            try:
                                priority = prio_pipe.predict([clean_text])[0]
                                p_probs = prio_pipe.predict_proba([clean_text])[0]
                                priority_confidence = float(np.max(p_probs))
                            except Exception:
                                pass

                        prio_base_weights = {'Critical': 90.0, 'High': 75.0, 'Medium': 50.0, 'Low': 25.0}
                        text_score = prio_base_weights.get(priority, 50.0) * priority_confidence + (1.0 - priority_confidence) * 50.0

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
                    if clean_text:
                        wing = self._bundle.predict([clean_text])[0]
                        probs = self._bundle.predict_proba([clean_text])[0]
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
            'complaint_type': complaint_type,
            'complaint_type_confidence': complaint_type_conf,
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
