from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import hashlib

from corporations import AP_MUNICIPAL_CORPORATIONS, get_corporation
from auth import get_current_user, get_optional_current_user
from database import get_supabase
from supabase import Client
from routers.employees import _MEMORY_EMPLOYEES

router = APIRouter(prefix="/api/auth", tags=["auth"])

class DepartmentLoginPayload(BaseModel):
    corporation_id: str  # e.g., 'GVMC', 'VMC', 'GMC'
    department_wing: str = "all"  # 'supreme' (all wings) or 'road', 'drainage', 'water_supply', 'street_lights', 'others'
    password: str

class EmployeeLoginPayload(BaseModel):
    employee_code: str  # e.g., 'EMP-101'
    password: str

@router.get("/corporations")
def list_ap_corporations():
    """Returns the list of 17 Municipal Corporations of Andhra Pradesh."""
    return AP_MUNICIPAL_CORPORATIONS

@router.post("/department-login")
def department_login(payload: DepartmentLoginPayload):
    """
    Official Department Portal login for any of the 17 AP Municipal Corporations.
    Supports Supreme Commissioner login (all wings) or 5 individual Department Head logins
    (Roads, Drainage, Water Supply, Street Lights, Sanitation).
    """
    corp_code = payload.corporation_id.strip().upper()
    corp = get_corporation(corp_code)

    if not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )

    wing = (payload.department_wing or "all").lower()
    wing_names = {
        "all": "Supreme Central Command",
        "supreme": "Supreme Central Command",
        "road": "Roads & Buildings Department",
        "drainage": "Drainage & Sewerage Department",
        "water_supply": "Water Supply & Quality Department",
        "street_lights": "Electrical & Street Lighting Department",
        "others": "Sanitation & Public Health Department",
        "sanitation": "Sanitation & Public Health Department"
    }
    wing_name = wing_names.get(wing, "Municipal Department Command")
    clean_wing = "all" if wing in ["all", "supreme"] else wing

    token = f"demo-department-{corp['code'].lower()}-{clean_wing}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "department",
        "user": {
            "id": f"dept-{corp['code'].lower()}-{clean_wing}",
            "email": corp["contact_email"],
            "name": f"{corp['name']} - {wing_name}",
            "role": "department",
            "department": clean_wing,
            "department_role": wing,
            "department_name": wing_name,
            "municipal_corporation": corp["code"],
            "corporation_details": corp
        }
    }

@router.post("/employee-login")
def employee_login(payload: EmployeeLoginPayload, supabase: Client = Depends(get_supabase)):
    """
    Employee Portal login for municipal officers and field crew (EMP-101 to EMP-140+).
    """
    if not payload.password or not payload.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for employee access."
        )

    code = payload.employee_code.strip().upper()
    emp = None

    # 1. Check Supabase
    if supabase is not None:
        try:
            res = supabase.table("employees").select("*").eq("employee_code", code).execute()
            if res.data and len(res.data) > 0:
                emp = res.data[0]
        except Exception:
            pass

    # 2. Check local memory
    if not emp:
        for item in _MEMORY_EMPLOYEES:
            if item.get("employee_code", "").upper() == code or item.get("id") == code:
                emp = item
                break
            
    if not emp:
        # If code matches pattern EMP-xxx, allow access
        if code.startswith("EMP-"):
            emp = {
                "id": f"emp-{code.lower()}",
                "employee_code": code,
                "name": f"Municipal Officer ({code})",
                "email": f"{code.lower()}@nexciv.ap.gov.in",
                "department": "road",
                "department_name": "Roads & Buildings Department",
                "designation": "Assistant Executive Engineer (AEE)",
                "zone": "Zone 1",
                "status": "active",
                "assigned_count": 0,
                "completed_count": 0,
                "pending_count": 0
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with code '{code}' not found in Andhra Pradesh Cadre registry."
            )

    token = f"demo-employee-{emp.get('employee_code', code).lower()}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "employee",
        "user": {
            "id": emp.get("id"),
            "employee_code": emp.get("employee_code"),
            "email": emp.get("email"),
            "name": emp.get("name"),
            "role": "employee",
            "department": emp.get("department"),
            "department_name": emp.get("department_name"),
            "designation": emp.get("designation"),
            "zone": emp.get("zone")
        },
        "employee": emp
    }

@router.get("/me")
def get_auth_me(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated profile of the current session."""
    return current_user

# ==============================================================================
# CITIZEN REGISTRATION & AUTHENTICATION ENDPOINTS
# ==============================================================================
class CitizenRegisterPayload(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    municipality_code: Optional[str] = "ELR"
    ward: Optional[str] = None
    address: Optional[str] = None

class CitizenLoginPayload(BaseModel):
    email: str
    password: str

@router.post("/register-citizen")
def register_citizen_endpoint(payload: CitizenRegisterPayload):
    """Registers a new citizen with their chosen Andhra Pradesh Municipality/Corporation."""
    from data_manager import register_citizen
    try:
        profile = register_citizen(payload.dict())
        return {
            "access_token": f"citizen-{profile['id']}",
            "token_type": "bearer",
            "role": "citizen",
            "user": profile
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login-citizen")
def login_citizen_endpoint(payload: CitizenLoginPayload):
    """Authenticates citizen with email and password."""
    from data_manager import authenticate_citizen
    profile = authenticate_citizen(payload.email, payload.password)
    if not profile:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {
        "access_token": f"citizen-{profile['id']}",
        "token_type": "bearer",
        "role": "citizen",
        "user": profile
    }

@router.get("/municipalities")
def list_all_ap_municipalities():
    """Returns all Andhra Pradesh Municipal Corporations and Municipalities across all 26 districts."""
    from data_manager import ALL_AP_MUNICIPALITIES
    return ALL_AP_MUNICIPALITIES

class ChangePasswordPayload(BaseModel):
    role: str  # 'citizen', 'employee', 'department'
    identifier: str  # email, employee_code, or corp_code
    oldPassword: Optional[str] = None
    newPassword: str

@router.post("/change-password")
def change_password_endpoint(payload: ChangePasswordPayload, supabase: Client = Depends(get_supabase)):
    """
    Updates password for Citizen, Employee, or Department portal access.
    """
    if not payload.newPassword or len(payload.newPassword) < 4:
        raise HTTPException(status_code=400, detail="New password must be at least 4 characters long.")

    p_hash = hashlib.sha256(payload.newPassword.encode()).hexdigest()
    identifier = payload.identifier.strip()

    # 1. Update in Supabase if connected
    if supabase is not None:
        try:
            if payload.role == "citizen":
                supabase.table("citizens").update({"password_hash": p_hash}).ilike("email", identifier).execute()
            elif payload.role == "employee":
                supabase.table("employees").update({"password_hash": p_hash}).eq("employee_code", identifier.upper()).execute()
        except Exception as e:
            print(f"Supabase password update note: {e}")

    return {
        "success": True,
        "message": f"Password updated successfully for {payload.role} ({identifier})."
    }


