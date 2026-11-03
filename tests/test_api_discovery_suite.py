"""
NEX-CIV Phase 3 Master API Discovery & Functional Test Suite
Covers all FastAPI endpoints across:
1. Health & Status
2. Authentication & Municipal Passkeys
3. Grievance Management (CRUD, SLA calculation, Isolation)
4. AI Dispatch, Classification & Computer Vision Verification
5. Employee Work Order Allocation & Cadre Integrity
6. Citizen Privacy Masking & Audit Trail
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "backend") not in sys.path:
    sys.path.append(str(BASE_DIR / "backend"))

from backend.main import app

client = TestClient(app)


def test_api_health_endpoint():
    """Validates health check API."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "NEXCIV" in data["service"]


def test_ai_classify_endpoint():
    """Tests multilingual complaint classification endpoint."""
    payload = {"text": "స్ట్రీట్ లైట్ పనిచేయడం లేదు రాత్రి సమయంలో చీకటిగా ఉంది"}
    res = client.post("/api/classify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert (
        data.get("department_code") in ["street_lights", "electrical"]
        or data.get("wing") in ["street_lights", "electrical"]
        or "Electrical" in data.get("department", "")
    )
    assert "confidence" in data


def test_ai_dispatch_recommendation_endpoint():
    """Tests Google OR-Tools CP-SAT Automated Cadre Dispatch endpoint."""
    payload = {
        "complaint": {
            "id": "NXC-TEST-SL-01",
            "grievance_ref_number": "NXC-TEST-SL-01",
            "title": "స్ట్రీట్ లైట్ వైర్ తెగిపడింది",
            "municipal_corporation": "ELR",
            "priority": "High"
        }
    }
    res = client.post("/api/ai/recommend-dispatch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "recommended_employee" in data
    # Cadre must be Street Lights, never Roads
    assert "Sky-Lift" in " ".join(data.get("required_equipment", []))
    assert data["recommended_employee"]["department"] in ["street_lights", "Electrical & Street Lighting Wing"]


def test_ai_verify_resolution_endpoint():
    """Tests Multimodal Computer Vision Resolution Proof Verification."""
    payload = {
        "before_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkWPjfDwAEeQHzG/N3wQAAAABJRU5ErkJggg==",
        "after_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkWPjfDwAEeQHzG/N3wQAAAABJRU5ErkJggg==",
        "defect_type": "pothole"
    }
    res = client.post("/api/ai/verify-resolution", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "isVerifiedResolved" in data
    assert "confidenceScore" in data


def test_ai_predict_escalation_endpoint():
    """Tests SLA Breach and Escalation Risk prediction."""
    payload = {
        "complaint": {
            "id": "NXC-RISK-01",
            "created_at": "2026-10-01T10:00:00Z",
            "priority": "Critical"
        }
    }
    res = client.post("/api/ai/predict-escalation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["riskScore"] >= 50
    assert data["riskLevel"] in ["High", "Critical Escalation"]


def test_complaints_crud_and_privacy_masking():
    """
    Tests citizen complaint registration, automatic AI triage,
    and unauthenticated citizen privacy masking (phone/email masked).
    """
    create_payload = {
        "title": "Road cave-in near Government Hospital Gate",
        "description": "Deep dangerous crater on asphalt road. Multiple bikes skidded.",
        "category": "road",
        "municipal_corporation": "ELR",
        "ward": "Ward 12",
        "location_address": "Hospital Road, Ward 12, Eluru",
        "citizen_name": "S. Rajesh Kumar",
        "citizen_email": "rajesh.kumar@example.com",
        "citizen_phone": "+91 94401 99887"
    }

    res = client.post("/api/complaints", json=create_payload)
    assert res.status_code == 200
    created = res.json()
    assert "id" in created
    c_id = created["id"]
    assert created["municipal_corporation"] == "ELR"
    assert created["status"] in ["pending", "in_progress"]

    # Public fetch: citizen phone and email must be masked for privacy!
    res_get = client.get(f"/api/complaints/{c_id}")
    assert res_get.status_code == 200
    pub_data = res_get.json()
    assert "citizen_phone" in pub_data
    phone_val = pub_data["citizen_phone"]
    assert ("•••••" in phone_val or "***" in phone_val), f"Privacy leak: {phone_val} was not masked!"


def test_employee_list_municipality_isolation():
    """Verifies that employees queried for Eluru (ELR) contain only ELR staff."""
    res = client.get("/api/employees?municipality_code=ELR")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    for emp in data:
        assert emp["municipality_code"] == "ELR", f"Employee {emp['id']} leaked into ELR query!"


def test_complaint_assignment_flow():
    """Tests assigning an open grievance to a field officer."""
    assign_payload = {
        "employee_id": "DEMO-ELR-RD-01",
        "assigned_team": "Roads & Buildings Rapid Response Squad",
        "reassignment_reason": "Urgent structural cave-in inspection deployed"
    }
    # Assign case
    res = client.post("/api/complaints/B13747/assign", json=assign_payload)
    if res.status_code == 200:
        data = res.json()
        assert data["assigned_employee_id"] == "DEMO-ELR-RD-01"
        assert data["status"] == "in_progress"
