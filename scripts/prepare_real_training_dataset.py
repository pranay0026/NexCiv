"""
NEX-CIV Real Dataset Preprocessing & Ground-Truth Annotation Pipeline
Uses the real 10,000 AP Municipal Grievance dataset (nexciv_multilingual_complaints_10k.csv)
and enriches each real complaint with:
- Multilingual Severity (1-4)
- Public Safety Risk (0-100)
- Public Health Risk (0-100)
- Critical Infrastructure Impact (0-100)
- Statutory SLA Deadlines (AP Working Days & Citizen Charter)
- Explainable Priority Score (0-100)
- Statutory Emergency Overrides
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.ai_severity_engine import analyze_complaint_severity
from backend.sla_service import compute_statutory_deadline
from backend.ai_priority_engine import calculate_priority

REAL_DATASET_SOURCE = BASE_DIR / "nexciv_multilingual_complaints_10k.csv"
OUTPUT_DATASET = BASE_DIR / "priority_engine" / "datasets" / "expert_civic_grievance_dataset.csv"

def process_real_dataset():
    if not REAL_DATASET_SOURCE.exists():
        print(f"Error: {REAL_DATASET_SOURCE} not found.")
        return

    print(f"Reading real AP municipal grievance dataset from {REAL_DATASET_SOURCE}...")
    df = pd.read_csv(REAL_DATASET_SOURCE)
    print(f"Loaded {len(df)} real complaints across {df['municipality'].nunique()} Urban Local Bodies.")

    enriched_rows = []

    for idx, row in df.iterrows():
        text = str(row.get("complaint_text", ""))
        cat = str(row.get("department", "others")).lower()
        muni = str(row.get("municipality", "ELR"))
        ward = str(row.get("ward", "Ward 1"))
        defect = str(row.get("complaint_type", ""))

        # 1. Multilingual Severity AI Evaluation
        sev_info = analyze_complaint_severity(
            text=text,
            category=cat,
            defect_type=defect,
            location_address=f"{ward}, {muni}"
        )

        # 2. Statutory SLA Lookup
        sla_info = compute_statutory_deadline(
            category=cat,
            defect_type=defect
        )

        # 3. Priority Scoring & Emergency Check
        payload = {
            "title": text[:60],
            "description": text,
            "category": cat,
            "defect_type": defect,
            "duplicate_count": 0,
            "upvote_count": 1
        }

        prio_info = calculate_priority(
            severity_info=sev_info,
            sla_info=sla_info,
            complaint_data=payload
        )

        enriched_rows.append({
            "complaint_id": row.get("complaint_id", f"NX{idx+1:06d}"),
            "text": text,
            "language": row.get("language_style", "en"),
            "category": cat,
            "complaint_type": defect,
            "municipality": muni,
            "ward": ward,
            "severity_level": sev_info["severity_level"],
            "severity_label": sev_info["severity_label"],
            "safety_risk": sev_info["safety_risk"],
            "public_health_risk": sev_info["public_health_risk"],
            "public_impact": sev_info["public_impact_score"],
            "estimated_citizens_affected": sev_info["estimated_citizens_affected"],
            "infrastructure_criticality": sev_info["infrastructure_criticality"],
            "sla_urgency": sla_info["sla_urgency_score"],
            "statutory_sla_days": sla_info["prescribed_days"],
            "is_emergency": 1 if prio_info["is_emergency_override"] else 0,
            "priority_score": prio_info["priority_score"],
            "priority_tier": prio_info["priority_label"],
            "priority_explanation": prio_info["explanation_summary"],
            "split": row.get("split", "train")
        })

    out_df = pd.DataFrame(enriched_rows)
    out_df.to_csv(OUTPUT_DATASET, index=False, encoding="utf-8")
    print(f"Successfully annotated and saved {len(out_df)} real complaints to {OUTPUT_DATASET}")
    print(f"Severity Distribution:\n{out_df['severity_label'].value_counts()}")
    print(f"Priority Distribution:\n{out_df['priority_tier'].value_counts()}")
    print(f"Emergency Overrides: {out_df['is_emergency'].sum()}")

if __name__ == "__main__":
    process_real_dataset()
