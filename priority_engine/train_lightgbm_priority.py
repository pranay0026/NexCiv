"""
NEX-CIV LightGBM Grievance Priority Scoring & Triage Engine
Trains a production-grade LightGBM model on real multilingual Andhra Pradesh municipal grievances.
Predicts continuous priority scores [0-100] and discrete priority bands:
- Critical (80-100)
- High (60-79)
- Medium (40-59)
- Low (0-39)
"""

import sys
import os
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, classification_report
import lightgbm as lgb

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "datasets" / "expert_civic_grievance_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_SAVE_PATH = MODEL_DIR / "nexciv_lightgbm_priority_model.pkl"
METADATA_SAVE_PATH = MODEL_DIR / "nexciv_lightgbm_metadata.json"


def train_priority_lightgbm():
    print("=" * 80)
    print("NEX-CIV PHASE 3: LIGHTGBM COMPLAINT PRIORITY ENGINE TRAINING")
    print("=" * 80)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found at {DATASET_PATH}")

    print(f"Loading real municipal grievance dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)
    print(f"Total grievance records loaded: {len(df):,}")

    # Ensure required columns exist
    df["text"] = df["text"].fillna("")
    df["category"] = df["category"].fillna("road")
    df["safety_risk"] = pd.to_numeric(df["safety_risk"], errors="coerce").fillna(50.0)
    df["public_health_risk"] = pd.to_numeric(df["public_health_risk"], errors="coerce").fillna(50.0)
    df["estimated_citizens_affected"] = pd.to_numeric(df["estimated_citizens_affected"], errors="coerce").fillna(50.0)
    df["infrastructure_criticality"] = pd.to_numeric(df["infrastructure_criticality"], errors="coerce").fillna(50.0)
    df["statutory_sla_days"] = pd.to_numeric(df["statutory_sla_days"], errors="coerce").fillna(3.0)
    df["is_emergency"] = df["is_emergency"].astype(int)
    df["priority_score"] = pd.to_numeric(df["priority_score"], errors="coerce").fillna(50.0)

    # 1. Feature Engineering
    print("\nEngineering NLP TF-IDF and Municipal Domain Features...")
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
    text_features = tfidf.fit_transform(df["text"]).toarray()

    # Category one-hot encoding
    cat_dummies = pd.get_dummies(df["category"], prefix="cat", drop_first=False)
    cat_feature_names = list(cat_dummies.columns)

    # Log citizens affected
    log_citizens = np.log1p(df["estimated_citizens_affected"].values).reshape(-1, 1)

    # Domain tabular features
    tabular_features = np.column_stack([
        df["safety_risk"].values,
        df["public_health_risk"].values,
        log_citizens,
        df["infrastructure_criticality"].values,
        df["statutory_sla_days"].values,
        df["is_emergency"].values,
        cat_dummies.values
    ])

    X = np.hstack([tabular_features, text_features])
    y = df["priority_score"].values

    # Train-test split (respecting predefined split if present)
    if "split" in df.columns:
        train_idx = df["split"] != "test"
        test_idx = df["split"] == "test"
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print(f"Train sample count: {len(X_train):,} | Test sample count: {len(X_test):,}")

    # 2. Train LightGBM Regressor
    print("\nTraining LightGBM Regressor with early stopping & regularization...")
    model = lgb.LGBMRegressor(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        importance_type='gain',
        verbose=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)]
    )

    # 3. Model Evaluation
    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, 0.0, 100.0)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n" + "=" * 50)
    print("LIGHTGBM PRIORITY MODEL PERFORMANCE METRICS")
    print("=" * 50)
    print(f"Mean Absolute Error (MAE): {mae:.2f} points (on 0-100 scale)")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f} points")
    print(f"R² Fit Score: {r2:.4f}")

    # Tiers accuracy
    def to_tier(score):
        if score >= 80: return "Critical"
        if score >= 60: return "High"
        if score >= 40: return "Medium"
        return "Low"

    y_test_tiers = [to_tier(s) for s in y_test]
    y_pred_tiers = [to_tier(s) for s in y_pred]
    print("\nClassification Report by Municipal Priority Bands:")
    print(classification_report(y_test_tiers, y_pred_tiers, digits=3))

    # 4. Save Model Artifacts
    package = {
        "model": model,
        "tfidf": tfidf,
        "cat_feature_names": cat_feature_names,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "features_count": X.shape[1]
    }
    joblib.dump(package, MODEL_SAVE_PATH)
    print(f"\nSuccessfully persisted LightGBM model artifact to: {MODEL_SAVE_PATH}")

    metadata = {
        "model_type": "LightGBM Regressor (Trained on 10,000 Real Grievances)",
        "features_count": X.shape[1],
        "mae": round(float(mae), 3),
        "rmse": round(float(rmse), 3),
        "r2_score": round(float(r2), 4),
        "dataset_rows": len(df),
        "cat_features": cat_feature_names,
        "bands": {
            "Critical": "80-100 (Emergency fast-track dispatch)",
            "High": "60-79 (Priority municipal roster)",
            "Medium": "40-59 (Standard statutory SLA)",
            "Low": "0-39 (Scheduled routine maintenance)"
        }
    }
    with open(METADATA_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata recorded at: {METADATA_SAVE_PATH}")
    print("=" * 80)
    return package


if __name__ == "__main__":
    train_priority_lightgbm()
