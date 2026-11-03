"""
NEX-CIV: Two-Task Prediction & Inference Service
Performs real-time inference on civic grievances:
- Preprocesses input (Unicode NFC, language style detection)
- Predicts Department (5 classes) with probability confidence
- Predicts Complaint Type (20 classes) with probability confidence
- Ensures deterministic consistency between complaint type and department
"""

import os
import joblib
import numpy as np
from typing import Dict, Any

from .preprocess import preprocess_complaint_text

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "models", "complaint_classifier", "complaint_classifier.pkl"
)

DEPT_NAMES = {
    'road': {'id': 'D01', 'name': 'Roads & Buildings', 'telugu_name': 'రహదారులు మరియు భవనాల శాఖ'},
    'drainage': {'id': 'D02', 'name': 'Drainage & Sewerage', 'telugu_name': 'ప్రజారోగ్యం మరియు డ్రైనేజీ శాఖ'},
    'water_supply': {'id': 'D03', 'name': 'Water Supply', 'telugu_name': 'తాగునీటి సరఫరా విభాగం'},
    'street_lights': {'id': 'D04', 'name': 'Electrical & Street Lighting', 'telugu_name': 'విద్యుత్ మరియు వీధి దీపాల విభాగం'},
    'others': {'id': 'D05', 'name': 'Sanitation & Solid Waste', 'telugu_name': 'పారిశుధ్యం మరియు ఘన వ్యర్థాల నిర్వహణ'}
}

TYPE_NAMES = {
    'potholes': {'id': 'C01', 'name': 'Potholes'},
    'damaged_roads': {'id': 'C02', 'name': 'Damaged roads'},
    'footpath_damage': {'id': 'C03', 'name': 'Footpath damage'},
    'road_obstruction': {'id': 'C04', 'name': 'Road obstruction'},
    'drainage_overflow': {'id': 'C05', 'name': 'Drainage overflow'},
    'blocked_drainage': {'id': 'C06', 'name': 'Blocked drainage'},
    'open_manhole': {'id': 'C07', 'name': 'Open manhole'},
    'sewage_leakage': {'id': 'C08', 'name': 'Sewage leakage'},
    'no_water_supply': {'id': 'C09', 'name': 'No water supply'},
    'water_contamination': {'id': 'C10', 'name': 'Water contamination'},
    'pipeline_leakage': {'id': 'C11', 'name': 'Pipeline leakage'},
    'low_water_pressure': {'id': 'C12', 'name': 'Low water pressure'},
    'street_light_failure': {'id': 'C13', 'name': 'Street light failure'},
    'damaged_electric_pole': {'id': 'C14', 'name': 'Damaged electric pole'},
    'exposed_electrical_wires': {'id': 'C15', 'name': 'Exposed electrical wires'},
    'garbage_accumulation': {'id': 'C16', 'name': 'Garbage accumulation'},
    'garbage_collection_failure': {'id': 'C17', 'name': 'Garbage collection failure'},
    'dead_animal_removal': {'id': 'C18', 'name': 'Dead animal removal'},
    'public_sanitation_issue': {'id': 'C19', 'name': 'Public sanitation issue'},
    'other_civic_issue': {'id': 'C20', 'name': 'Other civic issue'}
}

class NexCivPredictor:
    _instance = None
    _bundle = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, path: str = MODEL_PATH):
        if self._bundle is None:
            if os.path.exists(path):
                self._bundle = joblib.load(path)
                print(f"Loaded NexCiv Multi-Task Model from: {path}")
            else:
                print(f"Warning: Model path not found at {path}")

    def predict(self, text: str) -> Dict[str, Any]:
        if self._bundle is None:
            self.load_model()

        prep = preprocess_complaint_text(text)
        clean_text = prep['cleaned_text']
        lang_style = prep['language_style']

        dept_code = 'others'
        dept_conf = 0.5
        all_dept_probs = {}

        type_code = 'other_civic_issue'
        type_conf = 0.5
        all_type_probs = {}

        if self._bundle:
            dept_pipe = self._bundle.get('wing_pipeline') or self._bundle.get('pipeline')
            type_pipe = self._bundle.get('complaint_type_pipeline')

            if dept_pipe and clean_text:
                dept_code = dept_pipe.predict([clean_text])[0]
                d_probs = dept_pipe.predict_proba([clean_text])[0]
                dept_conf = float(np.max(d_probs))
                all_dept_probs = {cls: round(float(p), 4) for cls, p in zip(dept_pipe.classes_, d_probs)}

            if type_pipe and clean_text:
                type_code = type_pipe.predict([clean_text])[0]
                t_probs = type_pipe.predict_proba([clean_text])[0]
                type_conf = float(np.max(t_probs))
                all_type_probs = {cls: round(float(p), 4) for cls, p in zip(type_pipe.classes_, t_probs)}

        dept_meta = DEPT_NAMES.get(dept_code, {'id': 'D05', 'name': 'Sanitation & Solid Waste'})
        type_meta = TYPE_NAMES.get(type_code, {'id': 'C20', 'name': 'Other civic issue'})

        return {
            'text': text,
            'cleaned_text': clean_text,
            'language_style': lang_style,
            'department': {
                'id': dept_meta['id'],
                'code': dept_code,
                'name': dept_meta['name'],
                'confidence': dept_conf,
                'probabilities': all_dept_probs
            },
            'complaint_type': {
                'id': type_meta['id'],
                'code': type_code,
                'name': type_meta['name'],
                'confidence': type_conf,
                'probabilities': all_type_probs
            }
        }
