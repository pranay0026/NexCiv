"""
NEX-CIV Priority Engine - Standalone Inference Module
Loads serialized ML models from saved_models/ and performs real-time severity
and priority prediction with emergency override protection.
"""

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "saved_models"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
SEVERITY_MODEL_PATH = SAVED_MODELS_DIR / "nexciv_severity_model.pkl"
PRIORITY_MODEL_PATH = SAVED_MODELS_DIR / "nexciv_structured_priority_model.pkl"
LIGHTGBM_MODEL_PATH = MODELS_DIR / "nexciv_lightgbm_priority_model.pkl"

_SEVERITY_PIPELINE = None
_PRIORITY_MODEL = None
_LIGHTGBM_PACKAGE = None

def get_models():
    global _SEVERITY_PIPELINE, _PRIORITY_MODEL, _LIGHTGBM_PACKAGE
    if _LIGHTGBM_PACKAGE is None:
        p = LIGHTGBM_MODEL_PATH if LIGHTGBM_MODEL_PATH.exists() else (SAVED_MODELS_DIR / "nexciv_lightgbm_priority_model.pkl")
        if p.exists():
            try:
                _LIGHTGBM_PACKAGE = joblib.load(p)
            except Exception as e:
                print(f"[INFERENCE] Error loading LightGBM model: {e}")

    if _SEVERITY_PIPELINE is None and SEVERITY_MODEL_PATH.exists():
        try:
            _SEVERITY_PIPELINE = joblib.load(SEVERITY_MODEL_PATH)
        except Exception as e:
            print(f"[INFERENCE] Error loading severity model: {e}")

    if _PRIORITY_MODEL is None and PRIORITY_MODEL_PATH.exists():
        try:
            _PRIORITY_MODEL = joblib.load(PRIORITY_MODEL_PATH)
        except Exception as e:
            print(f"[INFERENCE] Error loading priority model: {e}")

    return _SEVERITY_PIPELINE, _PRIORITY_MODEL, _LIGHTGBM_PACKAGE

def predict_complaint_priority(
    text: str,
    safety_risk: float,
    public_health_risk: float,
    public_impact: float,
    infrastructure_criticality: float,
    sla_urgency: float,
    is_emergency: bool = False,
    category: str = "road",
    estimated_citizens_affected: float = 50.0,
    statutory_sla_days: float = 3.0
) -> Dict[str, Any]:
    """Runs inference across trained LightGBM ML models with emergency safety fallbacks."""
    sev_pipe, prio_model, lgb_pkg = get_models()

    pred_sev_level = 3 if is_emergency else 2
    if sev_pipe is not None:
        try:
            pred_sev_level = int(sev_pipe.predict([text])[0])
        except Exception:
            pass

    pred_priority_score = None

    # Priority 1: Use Production LightGBM Model if loaded
    if lgb_pkg is not None:
        try:
            model = lgb_pkg["model"]
            tfidf = lgb_pkg["tfidf"]
            cat_feature_names = lgb_pkg["cat_feature_names"]

            text_vec = tfidf.transform([text]).toarray()
            cat_col = f"cat_{category}"
            cat_vec = np.array([[1 if c == cat_col else 0 for c in cat_feature_names]])
            log_citizens = np.log1p(np.array([[float(estimated_citizens_affected)]]))

            tabular = np.column_stack([
                [[float(safety_risk)]],
                [[float(public_health_risk)]],
                log_citizens,
                [[float(infrastructure_criticality)]],
                [[float(statutory_sla_days)]],
                [[1 if is_emergency else 0]],
                cat_vec
            ])
            X_input = np.hstack([tabular, text_vec])
            pred_priority_score = float(model.predict(X_input)[0])
        except Exception as e:
            print(f"[INFERENCE] LightGBM inference fallback: {e}")

    # Priority 2: Structured scikit-learn regression model
    if pred_priority_score is None:
        features_df = pd.DataFrame([{
            "severity_level": pred_sev_level,
            "safety_risk": safety_risk,
            "public_health_risk": public_health_risk,
            "public_impact": public_impact,
            "infrastructure_criticality": infrastructure_criticality,
            "sla_urgency": sla_urgency,
            "is_emergency": 1 if is_emergency else 0
        }])

        if prio_model is not None:
            try:
                pred_priority_score = float(prio_model.predict(features_df)[0])
            except Exception:
                pred_priority_score = 95.0 if is_emergency else 65.0
        else:
            pred_priority_score = 95.0 if is_emergency else 65.0

    # Emergency safeguard: never allow an emergency to score below 95.0
    if is_emergency:
        pred_priority_score = max(95.0, pred_priority_score)

    pred_priority_score = round(max(0.0, min(100.0, pred_priority_score)), 2)

    if pred_priority_score >= 80.0 or is_emergency:
        tier = "Critical"
    elif pred_priority_score >= 60.0:
        tier = "High"
    elif pred_priority_score >= 40.0:
        tier = "Medium"
    else:
        tier = "Low"

    return {
        "predicted_severity_level": pred_sev_level,
        "predicted_priority_score": pred_priority_score,
        "predicted_priority_tier": tier,
        "is_emergency_override": is_emergency,
        "model_version": "3.3.0-LIGHTGBM-PROD"
    }
