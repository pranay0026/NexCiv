import os
import sys
import torch
import numpy as np
from typing import List, Tuple, Union, Optional
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from duplicate_detection.configs.config import cfg
from duplicate_detection.preprocessing.text_cleaner import clean_complaint_text

class CrossEncoderVerifier:
    """
    Layer 2 Cross-Encoder Pair Verification Module.
    Performs joint cross-attention over complaint pairs (Complaint A, Complaint B)
    to evaluate whether they refer to the exact same physical civic incident.
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or cfg.PRIMARY_CROSS_ENCODER
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads CrossEncoder with fallback."""
        try:
            from sentence_transformers import CrossEncoder
            print(f"Loading Cross-Encoder model: {self.model_name} on device: {self.device}...")
            self.model = CrossEncoder(self.model_name, max_length=512, device=self.device)
            print(f"Successfully loaded Cross-Encoder: {self.model_name}")
        except Exception as e:
            print(f"Notice: Primary Cross-Encoder {self.model_name} unavailable ({e}). Loading fallback...")
            try:
                from sentence_transformers import CrossEncoder
                self.model_name = cfg.FALLBACK_CROSS_ENCODER
                self.model = CrossEncoder(self.model_name, max_length=512, device=self.device)
                print(f"Successfully loaded fallback Cross-Encoder: {self.model_name}")
            except Exception as e2:
                print(f"Cross-encoder model loading error: {e2}")
                self.model = None

    def predict_pair(self, text_a: str, text_b: str) -> float:
        """
        Computes calibrated incident duplication score for a single complaint pair.
        Returns float in range [0.0, 1.0].
        """
        clean_a, _ = clean_complaint_text(text_a)
        clean_b, _ = clean_complaint_text(text_b)
        
        if not clean_a or not clean_b:
            return 0.0

        if self.model is not None:
            # Predict raw logit / score
            score = self.model.predict([(clean_a, clean_b)])[0]
            # Sigmoid calibration to map real logit to [0, 1] probability
            prob = 1.0 / (1.0 + np.exp(-float(score))) if isinstance(score, (float, int, np.floating)) else 0.5
            return float(np.clip(prob, 0.0, 1.0))
        else:
            # Fallback heuristic if deep cross-encoder offline
            # Jaccard + length penalty
            tok_a = set(clean_a.lower().split())
            tok_b = set(clean_b.lower().split())
            inter = len(tok_a.intersection(tok_b))
            union = len(tok_a.union(tok_b))
            return float(inter / union) if union > 0 else 0.0

    def predict_batch(self, pairs: List[Tuple[str, str]], batch_size: int = 16) -> np.ndarray:
        """
        Predicts calibrated duplicate probabilities for a list of complaint pairs.
        Returns numpy array of probabilities.
        """
        cleaned_pairs = [(clean_complaint_text(a)[0], clean_complaint_text(b)[0]) for a, b in pairs]
        
        if self.model is not None:
            scores = self.model.predict(cleaned_pairs, batch_size=batch_size, show_progress_bar=False)
            probs = 1.0 / (1.0 + np.exp(-np.array(scores, dtype=np.float32)))
            return np.clip(probs, 0.0, 1.0)
        else:
            res = [self.predict_pair(a, b) for a, b in cleaned_pairs]
            return np.array(res, dtype=np.float32)

_GLOBAL_CROSS_ENCODER = None

def get_cross_encoder() -> CrossEncoderVerifier:
    """Singleton getter for cross-encoder."""
    global _GLOBAL_CROSS_ENCODER
    if _GLOBAL_CROSS_ENCODER is None:
        _GLOBAL_CROSS_ENCODER = CrossEncoderVerifier()
    return _GLOBAL_CROSS_ENCODER
