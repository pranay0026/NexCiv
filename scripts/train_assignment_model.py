import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import lightgbm as lgb
import joblib

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COMPLAINTS_CSV = os.path.join(DATA_DIR, "complaints_training.csv")  # placeholder path
EMPLOYEES_CSV = os.path.join(DATA_DIR, "employees_training.csv")  # placeholder path
MODEL_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "assignment_model.pkl"))

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_data():
    """Load complaints and employees data.
    Expected columns (complaints):
        id, department_code, municipal_corporation, severity,
        safety_risk, public_impact, infrastructure_criticality,
        recurrence, sla_remaining_hours, location_lat, location_lng, ward
    Expected columns (employees):
        id, municipality_code, department, zone, current_workload,
        maximum_workload, availability_status, location_lat, location_lng, skills
    The training target is the employee id that ultimately resolved the complaint.
    """
    complaints = pd.read_csv(COMPLAINTS_CSV)
    employees = pd.read_csv(EMPLOYEES_CSV)
    return complaints, employees

def build_features(complaints: pd.DataFrame, employees: pd.DataFrame):
    """Join complaints with the true assigned employee to create a training set.
    The target column will be ``assigned_employee_id``.
    The function creates a flat feature vector for each (complaint, employee) pair
    and labels it 1 if this employee was the true assignee, otherwise 0.
    This allows us to train a binary classifier that scores a given employee for a
    given complaint. At inference time we rank all eligible employees and pick the
    highest‑scoring one.
    """
    # Merge complaints with the true assignment
    merged = complaints.merge(employees, left_on="assigned_employee_id", right_on="id", suffixes=("_complaint", "_employee"), how="left")
    # Basic feature engineering – numeric columns
    numeric_features = [
        "severity",
        "safety_risk",
        "public_impact",
        "infrastructure_criticality",
        "recurrence",
        "sla_remaining_hours",
        "current_workload",
        "maximum_workload",
    ]
    # Add distance feature (haversine)
    def haversine(row):
        lat1, lon1 = row["location_lat_complaint"], row["location_lng_complaint"]
        lat2, lon2 = row["location_lat_employee"], row["location_lng_employee"]
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        km = 6371 * c
        return km
    merged["distance_km"] = merged.apply(haversine, axis=1)
    numeric_features.append("distance_km")

    # Categorical features
    categorical_features = [
        "department_code_complaint",
        "municipal_corporation_complaint",
        "department_employee",
        "municipality_code",
        "zone",
        "availability_status",
    ]

    X = merged[numeric_features + categorical_features]
    y = merged["assigned_employee_id"].apply(lambda x: 1)  # All rows are positive examples (the true pair)
    return X, y, numeric_features, categorical_features

def train_model():
    complaints, employees = load_data()
    X, y, num_feats, cat_feats = build_features(complaints, employees)
    # Split for validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocess categorical columns
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_feats)
        ],
        remainder="passthrough"
    )

    # LightGBM works with numpy arrays; we embed preprocessing in a pipeline
    model = lgb.LGBMClassifier(
        objective="binary",
        boosting_type="gbdt",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
    pipeline.fit(X_train, y_train)
    # Simple validation metric – AUC
    from sklearn.metrics import roc_auc_score
    preds = pipeline.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, preds)
    print(f"Validation AUC: {auc:.4f}")
    # Save the pipeline (includes preprocessing)
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    joblib.dump(pipeline, MODEL_OUTPUT)
    print(f"Model saved to {MODEL_OUTPUT}")

if __name__ == "__main__":
    train_model()
