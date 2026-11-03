import sys
from pathlib import Path
import pytest
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "backend") not in sys.path:
    sys.path.append(str(BASE_DIR / "backend"))

from backend.priority_engine import evaluate_priority
from backend.assignment_engine import select_employee_for_complaint

# Helper minimal complaint dict for priority scoring
def sample_complaint(overdue=False, remaining_hours=24):
    return {
        "severity": 3,
        "safety_risk": 70,
        "public_impact": 60,
        "sla_remaining_hours": remaining_hours,
        "infrastructure_criticality": 40,
        "recurrence": 20,
    }

def test_priority_scoring():
    comp = sample_complaint()
    result = evaluate_priority(comp)
    assert "priority_score" in result
    assert result["priority_label"] in {"Critical", "High", "Medium", "Low"}

def test_assignment_hard_constraints(monkeypatch):
    # Mock supabase employee fetch
    def mock_get_supabase():
        class MockTable:
            def __init__(self, data):
                self._data = data
            def select(self, *_):
                return self
            def eq(self, *_):
                return self
            def execute(self):
                class Res:
                    def __init__(self, data):
                        self.data = data
                        self.error = None
                return Res(self._data)
        class MockSupabase:
            def table(self, name):
                if name == "employees":
                    return MockTable([
                        {"id": "EMP-1", "municipality_code": "VMC", "department": "road", "status": "Active", "skills": "pothole,crater", "maximum_workload": 5, "current_workload": 2, "availability_status": "available", "location_lat": 16.5, "location_lng": 80.6, "zone": "Ward 14"},
                        {"id": "EMP-2", "municipality_code": "VMC", "department": "road", "status": "Active", "skills": "road_obstruction", "maximum_workload": 5, "current_workload": 5, "availability_status": "available", "location_lat": 16.5, "location_lng": 80.6, "zone": "Ward 8"},
                    ])
                raise ValueError("Unknown table")
        return MockSupabase()
    monkeypatch.setattr('backend.database.get_supabase', mock_get_supabase)
    monkeypatch.setattr('backend.assignment_engine.get_supabase', mock_get_supabase)
    comp = {
        "municipal_corporation": "VMC",
        "department_code": "road",
        "required_skills": "pothole",
        "location_lat": 16.51,
        "location_lng": 80.61,
        "ward": "Ward 14",
    }
    assigned = select_employee_for_complaint(comp)
    assert assigned == "EMP-1"
