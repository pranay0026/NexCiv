import os
import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

import lightgbm as lgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from duplicate_detection.configs.config import cfg
from duplicate_detection.structured_matching.feature_extractor import (
    FEATURE_COLUMNS,
    extract_pair_features,
    batch_extract_features
)

MODEL_SAVE_PATH = cfg.SAVED_MODELS_DIR / "incident_matching_lgbm.pkl"

class StructuredIncidentClassifier:
    """
    Layer 3 Machine Learning Incident Matching Model (LightGBM / XGBoost).
    Learns non-linear interactions between:
    - Haversine distance & Ward boundaries
    - Semantic similarity & Complaint category match
    - Temporal decay & Evidence congruence
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or MODEL_SAVE_PATH
        self.model = None
        self.feature_names = FEATURE_COLUMNS
        self._load_if_exists()

    def _load_if_exists(self):
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.model = data.get('model')
                self.feature_names = data.get('feature_names', FEATURE_COLUMNS)
                print(f"Loaded trained structured incident classifier from {self.model_path}")
            except Exception as e:
                print(f"Notice: Could not load saved GBDT model ({e})")

    def train(self, train_df: pd.DataFrame, val_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains LightGBM classifier on extracted pair features.
        """
        print(f"Extracting features for {len(train_df)} training pairs...")
        X_train = batch_extract_features(train_df)
        y_train = train_df['label'].values.astype(int)

        print(f"Extracting features for {len(val_df)} validation pairs...")
        X_val = batch_extract_features(val_df)
        y_val = val_df['label'].values.astype(int)

        clf = lgb.LGBMClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=6,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )

        clf.fit(X_train, y_train, eval_set=[(X_val, y_val)])
        self.model = clf

        val_preds = clf.predict(X_val)
        val_probs = clf.predict_proba(X_val)[:, 1]

        acc = float(accuracy_score(y_val, val_preds))
        prec = float(precision_score(y_val, val_preds, zero_division=0))
        rec = float(recall_score(y_val, val_preds, zero_division=0))
        f1 = float(f1_score(y_val, val_preds, zero_division=0))
        auc = float(roc_auc_score(y_val, val_probs))

        # Save checkpoint
        cfg.SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'metrics': {'val_acc': acc, 'val_precision': prec, 'val_recall': rec, 'val_f1': f1, 'val_auc': auc}
        }, self.model_path)

        print(f"Model saved to {self.model_path}")
        print(f"Validation Metrics: Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}, AUC={auc:.4f}")

        return {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1': f1,
            'auc': auc
        }

    def predict_pair(self, features: Dict[str, float]) -> float:
        """
        Predicts duplicate incident probability given a feature dictionary.
        Returns float between 0.0 and 1.0.
        """
        if self.model is not None:
            feat_vec = np.array([[features.get(col, 0.0) for col in self.feature_names]], dtype=np.float32)
            prob = float(self.model.predict_proba(feat_vec)[0, 1])
            return prob
        else:
            # Weighted baseline scoring fallback
            S = features.get('semantic_similarity', 0.0)
            L = features.get('location_similarity', 0.0)
            C = features.get('cross_encoder_score', S)
            T = features.get('temporal_compatibility', 0.5)
            I = features.get('image_similarity', 0.5)
            # D = 0.45S + 0.25L + 0.15C + 0.10T + 0.05I
            score = 0.45 * S + 0.25 * L + 0.15 * C + 0.10 * T + 0.05 * I
            return float(np.clip(score, 0.0, 1.0))

_GLOBAL_CLASSIFIER = None

def get_structured_classifier() -> StructuredIncidentClassifier:
    global _GLOBAL_CLASSIFIER
    if _GLOBAL_CLASSIFIER is None:
        _GLOBAL_CLASSIFIER = StructuredIncidentClassifier()
    return _GLOBAL_CLASSIFIER
