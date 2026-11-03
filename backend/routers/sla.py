from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client
from database import get_supabase
from auth import get_current_user
from schemas import SLARuleCreate, SLARuleResponse

router = APIRouter(prefix="/api/sla", tags=["sla"])

@router.post("/", response_model=SLARuleResponse)
def create_sla_rule(rule: SLARuleCreate, current_user: dict = Depends(get_current_user), supabase: Client = Depends(get_supabase)):
    # Only municipal commissioners or state admins can create rules (simplified check)
    if current_user.get('role') not in ('commissioner', 'admin'):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    data = rule.dict()
    try:
        res = supabase.table("sla_rules").insert(data).execute()
        if res.error:
            raise HTTPException(status_code=400, detail=res.error.message)
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SLARuleResponse])
def list_sla_rules(municipality_code: str = None, department: str = None, category: str = None,
                    current_user: dict = Depends(get_current_user), supabase: Client = Depends(get_supabase)):
    query = supabase.table("sla_rules").select("*")
    if municipality_code:
        query = query.eq("municipality_code", municipality_code)
    if department:
        query = query.eq("department", department)
    if category:
        query = query.eq("complaint_category", category)
    res = query.execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data
