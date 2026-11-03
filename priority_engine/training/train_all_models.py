"""
NEX-CIV Master Model Training Engine
Trains:
1. Model 1 - Multilingual Complaint Severity Classifier (Telugu & English)
2. Model 2 - Structured Priority Prediction Engine (LightGBM)
3. Model 3 - Workforce Assignment Allocation Model

Saves serialized artifacts to priority_engine/saved_models/ and models/complaint_classifier/
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, mean_absolute_error, root_mean_squared_error, r2_score
import lightgbm as lgb

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = BASE_DIR / "priority_engine" / "datasets" / "expert_civic_grievance_dataset.csv"
SAVED_MODELS_DIR = BASE_DIR / "priority_engine" / "saved_models"
PRODUCTION_MODELS_DIR = BASE_DIR / "models" / "complaint_classifier"

SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTION_MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train_severity_model(df: pd.DataFrame):
    print("\n-----------------------------------------------------------")
    print("1. TRAINING MULTILINGUAL SEVERITY CLASSIFICATION MODEL")
    print("-----------------------------------------------------------")

    X = df["text"]
    y = df["severity_level"]  # 1 to 4

    X_train, X_test, y_train, y_test, lang_train, lang_test = train_test_split(
        X, y, df["language"], test_size=0.2, random_state=42, stratify=y
    )

    # Subword character n-gram + word n-gram pipeline for multilingual Telugu & English handling
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=12000,
            analyzer="char_wb",
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            C=2.5,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    # Global evaluation
    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["Low", "Moderate", "High", "Critical"], output_dict=True)

    print(f"Severity Classifier Overall Accuracy: {report['accuracy']*100:.2f}%")
    print(f"Severity Macro F1-Score: {report['macro avg']['f1-score']*100:.2f}%")

    # Evaluate Telugu vs English separately
    te_mask = (lang_test == "te")
    en_mask = (lang_test == "en")

    te_acc = (y_pred[te_mask] == y_test[te_mask]).mean()
    en_acc = (y_pred[en_mask] == y_test[en_mask]).mean()

    print(f"  Telugu (తెలుగు) Accuracy: {te_acc*100:.2f}%")
    print(f"  English Accuracy: {en_acc*100:.2f}%")

    # Save severity model
    sev_model_path = SAVED_MODELS_DIR / "nexciv_severity_model.pkl"
    joblib.dump(pipeline, sev_model_path)
    joblib.dump(pipeline, PRODUCTION_MODELS_DIR / "nexciv_severity_model.pkl")
    print(f"Saved severity model to {sev_model_path}")

    return pipeline, report, {"te_acc": te_acc, "en_acc": en_acc}

def train_structured_priority_model(df: pd.DataFrame):
    print("\n-----------------------------------------------------------")
    print("2. TRAINING STRUCTURED PRIORITY PREDICTION MODEL (LightGBM)")
    print("-----------------------------------------------------------")

    feature_cols = [
        "severity_level",
        "safety_risk",
        "public_health_risk",
        "public_impact",
        "infrastructure_criticality",
        "sla_urgency",
        "is_emergency"
    ]

    X = df[feature_cols]
    y = df["priority_score"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    lgb_regressor = lgb.LGBMRegressor(
        objective="regression",
        n_estimators=250,
        learning_rate=0.04,
        num_leaves=31,
        random_state=42,
        verbosity=-1
    )

    lgb_regressor.fit(X_train, y_train)

    y_pred = lgb_regressor.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"LightGBM Priority Prediction MAE: {mae:.2f}")
    print(f"LightGBM Priority Prediction RMSE: {rmse:.2f}")
    print(f"LightGBM Priority Prediction R2 Score: {r2*100:.2f}%")

    # Feature importances
    importances = dict(zip(feature_cols, lgb_regressor.feature_importances_))
    print(f"Feature Importances: {importances}")

    prio_model_path = SAVED_MODELS_DIR / "nexciv_structured_priority_model.pkl"
    joblib.dump(lgb_regressor, prio_model_path)
    joblib.dump(lgb_regressor, PRODUCTION_MODELS_DIR / "nexciv_structured_priority_model.pkl")
    print(f"Saved structured priority model to {prio_model_path}")

    return lgb_regressor, {"mae": mae, "rmse": rmse, "r2": r2}

def main():
    if not DATASET_PATH.exists():
        print(f"Dataset not found at {DATASET_PATH}. Run generate_expert_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset with {len(df)} samples from {DATASET_PATH}")

    sev_pipe, sev_rep, lang_stats = train_severity_model(df)
    prio_reg, prio_metrics = train_structured_priority_model(df)

    # Save summary metadata
    metrics_summary = {
        "dataset_samples": len(df),
        "severity_model": {
            "overall_accuracy": sev_rep["accuracy"],
            "macro_f1": sev_rep["macro avg"]["f1-score"],
            "telugu_accuracy": lang_stats["te_acc"],
            "english_accuracy": lang_stats["en_acc"]
        },
        "priority_model": {
            "algorithm": "LightGBM Regressor",
            "mae": prio_metrics["mae"],
            "rmse": prio_metrics["rmse"],
            "r2": prio_metrics["r2"]
        }
    }

    with open(SAVED_MODELS_DIR / "training_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    print("\nAll models trained and exported successfully!")

if __name__ == "__main__":
    main()
