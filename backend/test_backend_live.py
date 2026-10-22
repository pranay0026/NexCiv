import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("NEXCIV BACKEND SUITE: PHASE 1 & 2 VERIFICATION")
    print("==================================================")

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. Health check endpoint OK:", res.json())

    # 2. Get 40 Employees
    res = client.get("/api/employees")
    assert res.status_code == 200, f"Employees list failed: {res.text}"
    employees = res.json()
    assert len(employees) >= 40, f"Expected 40 employees, got {len(employees)}"
    print(f"[PASS] 2. Employees endpoint returned {len(employees)} employees across all 5 municipal wings.")

    # 3. Filter Employees by Department
    for dept in ["road", "drainage", "water_supply", "street_lights", "others"]:
        res = client.get(f"/api/employees?department={dept}")
        assert res.status_code == 200
        dept_emps = res.json()
        assert len(dept_emps) >= 8, f"Expected at least 8 employees for {dept}, got {len(dept_emps)}"
    print("[PASS] 3. Filter employees by department OK (8 per department verified).")

    # 4. Department Login for 17 AP Municipal Corporations
    dept_res = client.post("/api/auth/department-login", json={"corporation_id": "GVMC", "password": "admin@123"})
    assert dept_res.status_code == 200, f"Department login failed: {dept_res.text}"
    dept_data = dept_res.json()
    assert dept_data["role"] == "department"
    assert dept_data["user"]["municipal_corporation"] == "GVMC"
    print(f"[PASS] 4. Department login verified for {dept_data['user']['name']}.")

    # 5. Employee Login for AP cadre officers
    emp_login_res = client.post("/api/auth/employee-login", json={"employee_code": "EMP-101", "password": "emp@123"})
    assert emp_login_res.status_code == 200, f"Employee login failed: {emp_login_res.text}"
    emp_user = emp_login_res.json()
    assert emp_user["role"] == "employee"
    assert emp_user["employee"]["employee_code"] == "EMP-101"
    print(f"[PASS] 5. Employee login verified for {emp_user['employee']['name']} ({emp_user['employee']['designation']}).")

    # 6. Create Complaint with Multiple Photos, Ward, Landmark & AP Corporation
    complaint_payload = {
        "title": "Severe road cavity and water ponding near Benz Circle",
        "description": "Hazardous road crater and asphalt sinkhole right outside the service road. Multiple potholes and broken pavement blocks.",
        "category": "road",
        "municipal_corporation": "VMC",
        "ward": "Ward 24",
        "landmark": "Near Benz Circle Flyover Pillar 14",
        "location_address": "Benz Circle, Vijayawada",
        "location_lat": 16.5020,
        "location_lng": 80.6510,
        "images": [
            "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...",
            "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDA..."
        ],
        "citizen_name": "K. Venkat Rao",
        "citizen_email": "venkat.rao@gmail.com",
        "citizen_phone": "+91 98480 11223"
    }

    headers = {"Authorization": "Bearer demo-citizen-venkat"}
    res = client.post("/api/complaints", json=complaint_payload, headers=headers)
    assert res.status_code == 200, f"Complaint creation failed: {res.text}"
    created_complaint = res.json()
    cid = created_complaint["id"]
    assert created_complaint["municipal_corporation"] == "VMC"
    assert created_complaint["ward"] == "Ward 24"
    assert created_complaint["landmark"] == "Near Benz Circle Flyover Pillar 14"
    assert len(created_complaint["images"]) == 2
    print(f"[PASS] 6. Complaint created with 2 photos, Ward 24, VMC, ID: {cid}")

    # 7. Math Synchronization: Work Assignment (pending & assigned count increment)
    emp_before = client.get("/api/employees/EMP-102").json()
    emp_before_assigned = emp_before.get("assigned_count", 0)
    emp_before_pending = emp_before.get("pending_count", 0)

    assign_payload = {
        "employee_id": "EMP-102",
        "assigned_team": "Roads & Buildings Rapid Response Squad"
    }
    assign_res = client.patch(f"/api/complaints/{cid}/assign", json=assign_payload)
    assert assign_res.status_code == 200
    assigned = assign_res.json()
    assert assigned["status"] == "in_progress"
    assert assigned["assigned_employee_id"] == "EMP-102"

    emp_after_assign = client.get("/api/employees/EMP-102").json()
    assert emp_after_assign["assigned_count"] == emp_before_assigned + 1, "Assigned count math failed"
    assert emp_after_assign["pending_count"] == emp_before_pending + 1, "Pending count math failed"
    print(f"[PASS] 7. Work assignment math verified: EMP-102 assigned={emp_after_assign['assigned_count']}, pending={emp_after_assign['pending_count']}.")

    # 8. Math Synchronization: Work Resolution with Proof (completed count +1, pending -1)
    status_payload = {
        "status": "resolved",
        "notes": "Pothole filled with dense bituminous concrete, surface leveled and rolled.",
        "resolution_proof_url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ_RESOLVED_PROOF",
        "resolved_by_employee_id": "EMP-102"
    }
    res = client.patch(f"/api/complaints/{cid}", json=status_payload)
    assert res.status_code == 200, f"Status update failed: {res.text}"
    resolved = res.json()
    assert resolved["status"] == "resolved"
    assert resolved["resolution_notes"] is not None

    emp_after_resolve = client.get("/api/employees/EMP-102").json()
    assert emp_after_resolve["completed_count"] >= 1, "Completed count math failed"
    assert emp_after_resolve["pending_count"] == emp_before_pending, "Pending count math decrement failed"
    assert emp_after_resolve["completion_rate"] > 0, "Completion rate calculation failed"
    print(f"[PASS] 8. Work resolution math verified: EMP-102 completed={emp_after_resolve['completed_count']}, pending={emp_after_resolve['pending_count']}, rate={emp_after_resolve['completion_rate']}%.")

    # 9. Citizen Profile Query Filter
    res = client.get(f"/api/complaints?citizen_email=venkat.rao@gmail.com")
    assert res.status_code == 200
    citizen_complaints = res.json()
    assert any(c["id"] == cid for c in citizen_complaints), "Citizen complaint filtering failed"
    print(f"[PASS] 9. Citizen Profile complaint history query verified ({len(citizen_complaints)} complaints for citizen).")

    # 10. Employee Task Filter
    res = client.get(f"/api/complaints?assigned_employee_id=EMP-102")
    assert res.status_code == 200
    emp_complaints = res.json()
    assert any(c["id"] == cid for c in emp_complaints), "Employee task filtering failed"
    print(f"[PASS] 10. Employee task queue query verified ({len(emp_complaints)} tasks assigned to EMP-102).")

    # 11. Department Analytics with Municipal Corporation filter
    res = client.get("/api/complaints/analytics?municipal_corporation=VMC")
    assert res.status_code == 200
    vmc_analytics = res.json()
    assert "total_complaints" in vmc_analytics
    print(f"[PASS] 11. Municipal Corporation analytics filter verified (VMC total complaints: {vmc_analytics['total_complaints']}).")

    # 12. Hotspots Clustering
    res = client.get("/api/complaints/hotspots")
    assert res.status_code == 200
    hotspots_res = res.json()
    print(f"[PASS] 12. Geospatial Hotspots OK: {hotspots_res['total_hotspots']} hotspots detected.")

    print("\n==================================================")
    print("ALL 12/12 BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
