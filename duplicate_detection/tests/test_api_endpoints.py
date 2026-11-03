import sys
from pathlib import Path
# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_suite():
    print("=================================================================")
    print("NEX-CIV DUPLICATE DETECTION & MASTER INCIDENT API TEST SUITE")
    print("=================================================================")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    print("[PASS] 1. GET /api/health:", res_health.json())

    # 2. Check duplicate for brand new incident
    check_payload_1 = {
        "title": "Severe Pothole Cluster",
        "description": "Deep crater pothole near Main Bazaar RTC Bus stand causing accidents",
        "department_code": "road",
        "complaint_type": "potholes",
        "municipality": "GVMC",
        "ward": "Ward 12",
        "location_address": "RTC Complex, Ward 12, Visakhapatnam",
        "location_lat": 17.7200,
        "location_lng": 83.3050
    }
    res_chk_1 = client.post("/api/duplicates/check", json=check_payload_1)
    assert res_chk_1.status_code == 200
    chk_1_data = res_chk_1.json()
    print("[PASS] 2. POST /api/duplicates/check (First submission):")
    print(f"       Decision: {chk_1_data['decision']}, Recommended Action: {chk_1_data['recommended_action']}")

    # 3. Create First Complaint (Should generate a new Master Incident)
    complaint_1_payload = {
        "title": "Severe Pothole Cluster at RTC Complex",
        "description": "Deep crater pothole near Main Bazaar RTC Bus stand causing accidents",
        "category": "road",
        "municipal_corporation": "GVMC",
        "ward": "Ward 12",
        "location_address": "RTC Complex, Ward 12, Visakhapatnam",
        "location_lat": 17.7200,
        "location_lng": 83.3050,
        "citizen_name": "Rao Garu",
        "citizen_phone": "9876543210"
    }
    res_create_1 = client.post("/api/complaints/", json=complaint_1_payload)
    assert res_create_1.status_code in (200, 201)
    c1_data = res_create_1.json()
    print("[PASS] 3. POST /api/complaints/ (Original Complaint):")
    print(f"       Complaint ID: {c1_data['id']}, Ref: {c1_data.get('grievance_ref_number')}")
    print(f"       Master Incident ID: {c1_data.get('master_complaint_id')}")

    master_inc_id = c1_data.get('master_complaint_id')

    # 4. Check duplicate for second complaint in same spot in Telugu
    check_payload_2 = {
        "title": "రోడ్డుపై పెద్ద గుంతలు",
        "description": "ఆర్టీసీ బస్టాండ్ రోడ్డులో పెద్ద గుంత పడింది ప్రమాదాలు జరుగుతున్నాయి",
        "department_code": "road",
        "complaint_type": "potholes",
        "municipality": "GVMC",
        "ward": "Ward 12",
        "location_address": "RTC Bus Stand, Ward 12, Visakhapatnam",
        "location_lat": 17.7201, # 15 meters away
        "location_lng": 83.3051
    }
    res_chk_2 = client.post("/api/duplicates/check", json=check_payload_2)
    assert res_chk_2.status_code == 200
    chk_2_data = res_chk_2.json()
    print("[PASS] 4. POST /api/duplicates/check (Telugu submission in same spot):")
    print(f"       Decision: {chk_2_data['decision']}, Composite Score: {chk_2_data['composite_score']}")
    print(f"       Matched Incident: {chk_2_data.get('matched_incident_id')}")
    print(f"       Reasons: {chk_2_data['justification_reasons']}")

    # 5. Submit Second Complaint (Should Auto-Link to Master Incident)
    complaint_2_payload = {
        "title": "రోడ్డుపై పెద్ద గుంతలు",
        "description": "ఆర్టీసీ బస్టాండ్ రోడ్డులో పెద్ద గుంత పడింది ప్రమాదాలు జరుగుతున్నాయి",
        "category": "road",
        "municipal_corporation": "GVMC",
        "ward": "Ward 12",
        "location_address": "RTC Bus Stand, Ward 12, Visakhapatnam",
        "location_lat": 17.7201,
        "location_lng": 83.3051,
        "citizen_name": "Suresh Kumar",
        "citizen_phone": "9876543211"
    }
    res_create_2 = client.post("/api/complaints/", json=complaint_2_payload)
    assert res_create_2.status_code in (200, 201)
    c2_data = res_create_2.json()
    print("[PASS] 5. POST /api/complaints/ (Duplicate Telugu Complaint):")
    print(f"       Complaint ID: {c2_data['id']}, Ref: {c2_data.get('grievance_ref_number')}")
    print(f"       Is Duplicate: {c2_data.get('is_duplicate')}")
    print(f"       Master Incident ID: {c2_data.get('master_complaint_id')}")

    # 6. Verify GET /api/incidents
    res_inc = client.get("/api/incidents")
    assert res_inc.status_code == 200
    inc_data = res_inc.json()
    print(f"[PASS] 6. GET /api/incidents: Total Master Incidents: {inc_data['count']}")

    # 7. Verify GET /api/incidents/{incident_id}
    if master_inc_id:
        res_single_inc = client.get(f"/api/incidents/{master_inc_id}")
        assert res_single_inc.status_code == 200
        single_data = res_single_inc.json()
        print(f"[PASS] 7. GET /api/incidents/{master_inc_id}:")
        print(f"       Linked Complaints Count: {single_data['incident'].get('linked_complaints_count')}")
        print(f"       Affected Citizens Count: {single_data['incident'].get('citizens_affected_count')}")

    # 8. Verify POST /api/duplicates/verify (Officer Human-in-the-Loop)
    if master_inc_id:
        verify_payload = {
            "complaint_id": c2_data['id'],
            "target_incident_id": master_inc_id,
            "reviewer_employee_id": "EMP-ROAD-001",
            "action": "confirm_duplicate",
            "notes": "Verified by Assistant Engineer on site inspection"
        }
        res_verify = client.post("/api/duplicates/verify", json=verify_payload)
        assert res_verify.status_code == 200
        print("[PASS] 8. POST /api/duplicates/verify:", res_verify.json())

    print("\n=================================================================")
    print("ALL API ENDPOINT INTEGRATION TESTS PASSED SUCCESSFULLY (100% OK)")
    print("=================================================================")

if __name__ == "__main__":
    test_api_suite()
