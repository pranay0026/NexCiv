from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from ai_dispatch_engine import AiPhase3Engine
from routers.employees import _MEMORY_EMPLOYEES
from data_manager import get_employees_by_municipality

router = APIRouter(prefix="/api/ai", tags=["ai"])

class DispatchRequest(BaseModel):
    complaint: Dict[str, Any]

class ResolutionVerifyRequest(BaseModel):
    before_image: Optional[str] = None
    after_image: Optional[str] = None
    defect_type: Optional[str] = "defect"

class EscalationRiskRequest(BaseModel):
    complaint: Dict[str, Any]

@router.post("/recommend-dispatch")
def recommend_dispatch_endpoint(payload: DispatchRequest):
    """
    Phase 3 AI: Automated Cadre Crew & Work Order Smart Dispatch
    """
    complaint = payload.complaint
    corp = complaint.get("municipal_corporation") or "ELR"
    employees = get_employees_by_municipality(corp)
    if not employees:
        employees = _MEMORY_EMPLOYEES

    recommendation = AiPhase3Engine.recommend_dispatch(complaint, employees)
    return recommendation

@router.post("/verify-resolution")
def verify_resolution_endpoint(payload: ResolutionVerifyRequest):
    """
    Phase 3 AI: Multimodal Computer Vision Resolution Proof Verification
    """
    result = AiPhase3Engine.verify_resolution_proof(
        payload.before_image,
        payload.after_image,
        payload.defect_type or "defect"
    )
    return result

@router.post("/predict-escalation")
def predict_escalation_endpoint(payload: EscalationRiskRequest):
    """
    Phase 3 AI: Grievance Escalation & SLA Breach Risk Predictor
    """
    result = AiPhase3Engine.predict_escalation_risk(payload.complaint)
    return result
