# priority_engine.py – Configurable priority scoring
"""
Priority Engine for NEX‑CIV

The engine receives a complaint record (as a dict) enriched with:
- severity (1‑4) – from the severity classifier
- safety_risk (0‑100)
- public_impact (0‑100)
- sla_urgency (0‑100) – derived from time‑remaining thresholds
- infrastructure_criticality (0‑100)
- recurrence (0‑100)

It applies configurable weights (default matching the spec) and returns:
- priority_score (0‑100)
- priority_label (Critical/High/Medium/Low)

All weights are stored in a simple JSON config that can be edited at runtime.
"""
import json
from typing import Dict, Any

DEFAULT_CONFIG = {
    "weights": {
        "severity": 0.25,
        "safety_risk": 0.20,
        "public_impact": 0.15,
        "sla_urgency": 0.20,
        "infrastructure": 0.10,
        "recurrence": 0.10
    },
    "thresholds": {
        "critical": 80,
        "high": 60,
        "medium": 40,
        "low": 0
    }
}

_config_path = "backend/config/priority_config.json"

def load_config() -> Dict[str, Any]:
    try:
        with open(_config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # fallback to defaults if file missing or corrupted
        return DEFAULT_CONFIG

def normalize(value: float, max_val: float = 100.0) -> float:
    """Clamp and scale a raw value to 0‑100 range."""
    if value is None:
        return 0.0
    v = max(0.0, min(float(value), max_val))
    return (v / max_val) * 100.0

def compute_sla_urgency(remaining_hours: int) -> float:
    """Map remaining SLA time to a 0‑100 urgency score.
    The spec defines thresholds based on percentage of allowed time.
    Here we approximate using the remaining hours relative to a
    typical 48‑hour SLA (adjustable in the caller).
    """
    if remaining_hours <= 0:
        return 100.0
    # Assume a 48‑hour window for scaling – this can be tuned per complaint.
    pct = 1.0 - (remaining_hours / 48.0)
    return max(0.0, min(pct * 100.0, 100.0))

def score_priority(features: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_config()
    w = cfg["weights"]
    # Normalize each incoming feature to 0‑100 scale
    sev = normalize(features.get("severity"), 4)  # severity 1‑4
    safety = normalize(features.get("safety_risk"))
    public = normalize(features.get("public_impact"))
    sla_urg = normalize(features.get("sla_urgency"))
    infra = normalize(features.get("infrastructure_criticality"))
    rec = normalize(features.get("recurrence"))

    # Weighted sum
    raw_score = (
        sev * w["severity"] +
        safety * w["safety_risk"] +
        public * w["public_impact"] +
        sla_urg * w["sla_urgency"] +
        infra * w["infrastructure"] +
        rec * w["recurrence"]
    )
    # Clamp to 0‑100
    priority_score = max(0.0, min(raw_score, 100.0))

    # Determine label from thresholds
    th = cfg["thresholds"]
    if priority_score >= th["critical"]:
        label = "Critical"
    elif priority_score >= th["high"]:
        label = "High"
    elif priority_score >= th["medium"]:
        label = "Medium"
    else:
        label = "Low"

    return {
        "priority_score": round(priority_score, 2),
        "priority_label": label
    }

# Helper wrapper used by the complaints router
def evaluate_priority(complaint: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare feature dict and invoke the scoring logic.
    Expected keys in *complaint*:
        - severity (int 1‑4) – from severity model
        - safety_risk (float 0‑100)
        - public_impact (float 0‑100)
        - sla_remaining_hours (int)
        - infrastructure_criticality (float 0‑100)
        - recurrence (float 0‑100)
    """
    features = {
        "severity": complaint.get("severity"),
        "safety_risk": complaint.get("safety_risk"),
        "public_impact": complaint.get("public_impact"),
        "sla_urgency": compute_sla_urgency(complaint.get("sla_remaining_hours", 0)),
        "infrastructure_criticality": complaint.get("infrastructure_criticality"),
        "recurrence": complaint.get("recurrence")
    }
    return score_priority(features)
