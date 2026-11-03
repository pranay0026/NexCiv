from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import uuid
from supabase import Client

from database import get_supabase
from auth import get_optional_current_user
from schemas import EmployeeResponse, EmployeeCreate, EmployeeUpdate
from classifier import DEPARTMENTS

router = APIRouter(prefix="/api/employees", tags=["employees"])

# Persistent local disk storage for employees
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_LOCAL_EMPLOYEES_FILE = _DATA_DIR / "local_employees.json"

def _load_stored_employees() -> List[Dict[str, Any]]:
    if _LOCAL_EMPLOYEES_FILE.exists():
        try:
            with open(_LOCAL_EMPLOYEES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading local employees: {e}")
    return []

def _save_stored_employees(employees: List[Dict[str, Any]]):
    try:
        with open(_LOCAL_EMPLOYEES_FILE, "w", encoding="utf-8") as f:
            json.dump(employees, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving local employees: {e}")

_MEMORY_EMPLOYEES: List[Dict[str, Any]] = _load_stored_employees()

@router.get("", response_model=List[EmployeeResponse])
def list_employees(
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    municipality_code: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    offset: int = Query(0),
    supabase: Client = Depends(get_supabase)
):
    """
    Returns list of municipal employees across Roads, Drainage, Water Supply, Street Lights, and Sanitation.
    Supports filtering by municipality, department, status, zone, and search term.
    """
    from data_manager import get_employees_by_municipality
    source = get_employees_by_municipality(municipality_code) if municipality_code and municipality_code.lower() != 'all' else _MEMORY_EMPLOYEES

    # Apply in-memory filtering for local fallback or extra search
    filtered = []
    for emp in source:
        # Municipality filter
        if municipality_code and municipality_code.lower() != 'all':
            target_mun = municipality_code.strip().upper()
            emp_mun = (emp.get("municipality_code") or "").upper()
            emp_code = (emp.get("employee_code") or "").upper()
            if emp_mun != target_mun and target_mun not in emp_code:
                continue

        # Department filter
        if department and department.lower() != "all" and department != "All departments":
            target = department.lower().replace(" ", "_")
            emp_dept = emp.get("department", "").lower()
            emp_dept_name = emp.get("department_name", "").lower()
            if target not in emp_dept and target not in emp_dept_name:
                continue

        # Status filter
        if status and status.lower() != "all" and status != "All statuses":
            if emp.get("status", "").lower() != status.lower():
                continue

        # Zone filter
        if zone and zone.lower() != "all":
            if zone.lower() not in emp.get("zone", "").lower():
                continue

        # Search filter (name, employee_code, email, designation)
        if search and search.strip():
            q = search.strip().lower()
            name_match = q in emp.get("name", "").lower()
            code_match = q in emp.get("employee_code", "").lower()
            email_match = q in emp.get("email", "").lower()
            desig_match = q in emp.get("designation", "").lower()
            zone_match = q in emp.get("zone", "").lower()
            if not (name_match or code_match or email_match or desig_match or zone_match):
                continue

        filtered.append(emp)

    return filtered[offset : offset + limit]

@router.get("/{id_or_code}", response_model=EmployeeResponse)
def get_employee(
    id_or_code: str,
    supabase: Client = Depends(get_supabase)
):
    """Fetches single employee by UUID or employee code (e.g. EMP-101)."""
    # 1. Try Supabase
    if supabase is not None:
        try:
            if id_or_code.startswith("EMP-"):
                res = supabase.table("employees").select("*").eq("employee_code", id_or_code).execute()
            else:
                res = supabase.table("employees").select("*").eq("id", id_or_code).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    # 2. Check local memory
    for emp in _MEMORY_EMPLOYEES:
        if emp.get("id") == id_or_code or emp.get("employee_code") == id_or_code:
            return emp

    raise HTTPException(status_code=404, detail=f"Employee {id_or_code} not found")


def find_employee_record(id_or_code: str) -> Optional[Dict[str, Any]]:
    """Helper to find an employee dictionary by ID or code across all municipal registries."""
    if not id_or_code:
        return None
    for emp in _MEMORY_EMPLOYEES:
        if emp.get("id") == id_or_code or emp.get("employee_code") == id_or_code:
            return emp
    return None

@router.post("", response_model=EmployeeResponse)
def create_employee(
    payload: EmployeeCreate,
    supabase: Client = Depends(get_supabase)
):
    """Creates a new municipal employee bound to a specific municipality."""
    from data_manager import add_municipality_employee
    try:
        record = add_municipality_employee(payload.dict())
        _MEMORY_EMPLOYEES.insert(0, record)
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{id_or_code}", response_model=EmployeeResponse)
def update_employee(
    id_or_code: str,
    payload: EmployeeUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Updates an employee record."""
    now_str = datetime.utcnow().isoformat() + "Z"
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    update_data["updated_at"] = now_str

    updated_record = None

    # Update in memory
    for emp in _MEMORY_EMPLOYEES:
        if emp.get("id") == id_or_code or emp.get("employee_code") == id_or_code:
            emp.update(update_data)
            # Recompute completion rate if counts changed
            assigned = emp.get("assigned_count", 0)
            completed = emp.get("completed_count", 0)
            if assigned > 0:
                emp["completion_rate"] = round((completed / assigned) * 100, 1)
            updated_record = emp
            break

    if updated_record:
        _save_stored_employees(_MEMORY_EMPLOYEES)

    # Update in Supabase
    if supabase is not None:
        try:
            if id_or_code.startswith("EMP-"):
                res = supabase.table("employees").update(update_data).eq("employee_code", id_or_code).execute()
            else:
                res = supabase.table("employees").update(update_data).eq("id", id_or_code).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"Supabase employee update note: {e}")

    if updated_record:
        return updated_record

    raise HTTPException(status_code=404, detail=f"Employee {id_or_code} not found")

def increment_employee_workload(employee_id_or_code: str, supabase: Optional[Client] = None) -> Optional[Dict[str, Any]]:
    """Increments assigned_count and pending_count when a complaint is assigned."""
    now_str = datetime.utcnow().isoformat() + "Z"
    updated = None
    clean_target = employee_id_or_code.strip().upper()
    clean_name = employee_id_or_code.strip().lower()

    for emp in _MEMORY_EMPLOYEES:
        emp_name = (emp.get("name") or "").strip().lower()
        if (emp.get("id") == employee_id_or_code 
            or emp.get("employee_code", "").upper() == clean_target
            or (emp_name and emp_name == clean_name)
            or (clean_target and clean_target in emp.get("employee_code", "").upper())):
            emp["assigned_count"] = emp.get("assigned_count", 0) + 1
            emp["pending_count"] = emp.get("pending_count", 0) + 1
            assigned = emp["assigned_count"]
            completed = emp.get("completed_count", 0)
            emp["completion_rate"] = round((completed / max(1, assigned)) * 100, 1)
            emp["updated_at"] = now_str
            updated = emp
            break

    if updated:
        _save_stored_employees(_MEMORY_EMPLOYEES)
        if supabase is not None:
            try:
                update_payload = {
                    "assigned_count": updated["assigned_count"],
                    "pending_count": updated["pending_count"],
                    "completion_rate": updated["completion_rate"],
                    "updated_at": now_str
                }
                code_to_match = updated.get("employee_code")
                if code_to_match:
                    supabase.table("employees").update(update_payload).eq("employee_code", code_to_match).execute()
                else:
                    supabase.table("employees").update(update_payload).eq("id", updated.get("id")).execute()
            except Exception as e:
                print(f"Supabase workload sync note: {e}")

    return updated

def record_employee_resolution(employee_id_or_code: str, supabase: Optional[Client] = None) -> Optional[Dict[str, Any]]:
    """Increments completed_count and decrements pending_count when a complaint is resolved."""
    now_str = datetime.utcnow().isoformat() + "Z"
    updated = None
    clean_target = employee_id_or_code.strip().upper()
    clean_name = employee_id_or_code.strip().lower()

    for emp in _MEMORY_EMPLOYEES:
        emp_name = (emp.get("name") or "").strip().lower()
        if (emp.get("id") == employee_id_or_code 
            or emp.get("employee_code", "").upper() == clean_target
            or (emp_name and emp_name == clean_name)
            or (clean_target and clean_target in emp.get("employee_code", "").upper())):
            emp["completed_count"] = emp.get("completed_count", 0) + 1
            emp["pending_count"] = max(0, emp.get("pending_count", 1) - 1)
            # Ensure assigned_count is at least completed_count
            if emp.get("assigned_count", 0) < emp["completed_count"]:
                emp["assigned_count"] = emp["completed_count"]
            assigned = emp["assigned_count"]
            completed = emp["completed_count"]
            emp["completion_rate"] = round((completed / max(1, assigned)) * 100, 1)
            emp["updated_at"] = now_str
            updated = emp
            break

    if updated:
        _save_stored_employees(_MEMORY_EMPLOYEES)
        if supabase is not None:
            try:
                update_payload = {
                    "completed_count": updated["completed_count"],
                    "pending_count": updated["pending_count"],
                    "assigned_count": updated["assigned_count"],
                    "completion_rate": updated["completion_rate"],
                    "updated_at": now_str
                }
                code_to_match = updated.get("employee_code")
                if code_to_match:
                    supabase.table("employees").update(update_payload).eq("employee_code", code_to_match).execute()
                else:
                    supabase.table("employees").update(update_payload).eq("id", updated.get("id")).execute()
            except Exception as e:
                print(f"Supabase resolution sync note: {e}")

    return updated
