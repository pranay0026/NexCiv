"""
NEX-CIV Priority Engine Microservice FastAPI Router
Exposes dedicated endpoints for complaint severity classification,
structured priority prediction, and batch inference.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from priority_engine.inference.infer import predict_complaint_priority

router = APIRouter(prefix="/api/ai/priority-engine", tags=["priority-engine"])

class PriorityInferenceRequest(BaseModel):
    text: str = Field(..., description="Grievance description in Telugu or English")
    safety_risk: float = Field(default=30.0, ge=0.0, le=100.0)
    public_health_risk: float = Field(default=20.0, ge=0.0, le=100.0)
    public_impact: float = Field(default=30.0, ge=0.0, le=100.0)
    infrastructure_criticality: float = Field(default=40.0, ge=0.0, le=100.0)
    sla_urgency: float = Field(default=20.0, ge=0.0, le=100.0)
    is_emergency: bool = Field(default=False)

class PriorityInferenceResponse(BaseModel):
    predicted_severity_level: int
    predicted_priority_score: float
    predicted_priority_tier: str
    is_emergency_override: bool
    model_version: str

@router.post("/predict", response_model=PriorityInferenceResponse)
def run_priority_prediction(req: PriorityInferenceRequest):
    try:
        res = predict_complaint_priority(
            text=req.text,
            safety_risk=req.safety_risk,
            public_health_risk=req.public_health_risk,
            public_impact=req.public_impact,
            infrastructure_criticality=req.infrastructure_criticality,
            sla_urgency=req.sla_urgency,
            is_emergency=req.is_emergency
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
