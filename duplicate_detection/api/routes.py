import sys
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from duplicate_detection.retrieval.vector_store import get_vector_store, IncidentVectorStore
from duplicate_detection.decision_engine.hybrid_engine import get_decision_engine, HybridDecisionEngine
from duplicate_detection.embeddings.embedder import get_embedder, MultilingualEmbedder
from duplicate_detection.cross_encoder.reranker import get_cross_encoder, CrossEncoderVerifier
from duplicate_detection.preprocessing.text_cleaner import clean_complaint_text
from duplicate_detection.preprocessing.image_fingerprint import calculate_image_evidence_similarity

router = APIRouter(prefix="/api", tags=["Duplicate Detection & Master Incidents"])

# Pydantic Schemas
class DuplicateCheckRequest(BaseModel):
    title: Optional[str] = ""
    description: str = Field(..., min_length=3, description="Complaint text or audio transcript")
    department: Optional[str] = None
    department_code: Optional[str] = None
    complaint_type: Optional[str] = None
    municipality: Optional[str] = "GVMC"
    ward: Optional[str] = None
    landmark: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    image_url: Optional[str] = None
    image_hash: Optional[str] = None
    audio_transcript: Optional[str] = None

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    decision: str  # 'duplicate', 'review_required', 'new_incident'
    confidence: float
    composite_score: float
    recommended_action: str
    matched_incident_id: Optional[str] = None
    matched_incident_title: Optional[str] = None
    candidates: List[Dict[str, Any]] = []
    justification_reasons: List[str] = []

class DuplicateVerifyRequest(BaseModel):
    complaint_id: str
    target_incident_id: str
    reviewer_employee_id: str
    action: str = Field(..., description="'confirm_duplicate', 'reject_duplicate', 'split_incident'")
    notes: Optional[str] = None

class LinkComplaintRequest(BaseModel):
    complaint_id: str
    master_incident_id: str
    user_id: Optional[str] = "system"
    notes: Optional[str] = None

@router.post("/duplicates/check", response_model=DuplicateCheckResponse)
def check_duplicate_complaint(
    req: DuplicateCheckRequest,
    store: IncidentVectorStore = Depends(get_vector_store),
    engine: HybridDecisionEngine = Depends(get_decision_engine),
    embedder: MultilingualEmbedder = Depends(get_embedder),
    cross_encoder: CrossEncoderVerifier = Depends(get_cross_encoder)
):
    """
    Intelligent Multilingual & Multimodal Duplicate Grievance Detection.
    Evaluates semantic similarity, Haversine spatial proximity, cross-encoder token interaction,
    temporal lifespan, and visual evidence to determine if a grievance matches an active incident.
    """
    text_content = req.audio_transcript if req.audio_transcript else req.description
    cleaned_text, lang = clean_complaint_text(text_content)

    # 1. Generate dense multilingual query vector
    query_emb = embedder.encode(cleaned_text)[0]

    # 2. Retrieve Top-K semantically similar candidate incidents
    dept = req.department_code or req.department
    candidates = store.search_candidates(
        query_embedding=query_emb,
        department_code=dept,
        municipality=req.municipality,
        top_k=10
    )

    if not candidates:
        return DuplicateCheckResponse(
            is_duplicate=False,
            decision="new_incident",
            confidence=0.95,
            composite_score=0.0,
            recommended_action="Register as new independent Master Incident",
            matched_incident_id=None,
            matched_incident_title=None,
            candidates=[],
            justification_reasons=["No matching historical incidents found in municipal registry"]
        )

    # 3. Evaluate each candidate using the Hybrid Decision Engine
    eval_candidates = []
    best_candidate = None
    highest_score = -1.0

    new_dict = req.dict()

    for cand in candidates:
        sem_sim = cand.get('semantic_similarity', 0.5)
        # Cross-encoder joint interaction score
        cand_text = cand.get('description', '') or cand.get('title', '')
        ce_score = cross_encoder.predict_pair(cleaned_text, cand_text) if cand_text else sem_sim

        eval_res = engine.evaluate_pair(
            new_complaint=new_dict,
            candidate_complaint=cand,
            semantic_sim=sem_sim,
            cross_encoder_score=ce_score
        )

        cand_entry = {
            'incident_id': cand.get('incident_id'),
            'complaint_id': cand.get('complaint_id'),
            'title': cand.get('title'),
            'description': cand.get('description'),
            'composite_score': eval_res['composite_score'],
            'decision': eval_res['decision'],
            'confidence': eval_res['confidence'],
            'distance_meters': eval_res['distance_meters'],
            'semantic_similarity': eval_res['semantic_similarity'],
            'reasons': eval_res['reasons']
        }
        eval_candidates.append(cand_entry)

        if eval_res['composite_score'] > highest_score:
            highest_score = eval_res['composite_score']
            best_candidate = (cand, eval_res)

    eval_candidates.sort(key=lambda x: x['composite_score'], reverse=True)

    matched_inc_id = None
    matched_title = None
    is_dup = False
    reasons = []
    decision = "new_incident"
    confidence = 0.90
    action = "Register as new Master Incident"

    if best_candidate and highest_score >= engine.threshold_rev:
        cand, eval_res = best_candidate
        matched_inc_id = cand.get('incident_id')
        matched_title = cand.get('title')
        decision = eval_res['decision']
        confidence = eval_res['confidence']
        action = eval_res['recommended_action']
        reasons = eval_res['reasons']
        if decision == 'duplicate':
            is_dup = True

    return DuplicateCheckResponse(
        is_duplicate=is_dup,
        decision=decision,
        confidence=confidence,
        composite_score=highest_score if highest_score >= 0 else 0.0,
        recommended_action=action,
        matched_incident_id=matched_inc_id,
        matched_incident_title=matched_title,
        candidates=eval_candidates[:5],
        justification_reasons=reasons
    )

@router.get("/duplicates/candidates/{complaint_id}")
def get_complaint_duplicate_candidates(
    complaint_id: str,
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Retrieves duplicate candidate breakdown for a given complaint ID."""
    # Look up in predictions
    preds = [p for p in store._predictions if p.get('new_complaint_id') == complaint_id]
    return {"complaint_id": complaint_id, "evaluations": preds}

@router.post("/duplicates/verify")
def verify_duplicate(
    req: DuplicateVerifyRequest,
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Municipal Cadre / Officer Review: Confirms or rejects duplicate link."""
    review_record = {
        'complaint_id': req.complaint_id,
        'target_incident_id': req.target_incident_id,
        'reviewer_employee_id': req.reviewer_employee_id,
        'action': req.action,
        'notes': req.notes,
        'reviewed_at': "now"
    }
    store._reviews.insert(0, review_record)
    
    if req.action == 'confirm_duplicate':
        store.link_complaint(
            complaint_id=req.complaint_id,
            master_incident_id=req.target_incident_id,
            link_type='officer_verified',
            linked_by_user_id=req.reviewer_employee_id,
            notes=req.notes
        )
        return {"status": "success", "message": f"Complaint {req.complaint_id} confirmed and linked to {req.target_incident_id}"}
    elif req.action == 'split_incident':
        return {"status": "success", "message": f"Complaint {req.complaint_id} maintained as separate incident"}
    else:
        return {"status": "success", "message": f"Duplicate rejected for complaint {req.complaint_id}"}

@router.get("/incidents")
def list_incidents(
    municipality: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Returns consolidated Master Incidents with affected citizen counts."""
    incidents = store.get_all_incidents(municipality, department, status)
    return {"count": len(incidents), "incidents": incidents}

@router.get("/incidents/{incident_id}")
def get_incident(
    incident_id: str,
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Fetches details of a specific master incident."""
    inc = store.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    linked_complaints = store.get_incident_complaints(incident_id)
    return {"incident": inc, "linked_complaints": linked_complaints}

@router.get("/incidents/{incident_id}/complaints")
def get_incident_complaints_endpoint(
    incident_id: str,
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Returns all citizen complaints linked to a master incident."""
    complaints = store.get_incident_complaints(incident_id)
    return {"incident_id": incident_id, "complaints_count": len(complaints), "complaints": complaints}

@router.post("/incidents/link-complaint")
def manually_link_complaint(
    req: LinkComplaintRequest,
    store: IncidentVectorStore = Depends(get_vector_store)
):
    """Manually links an authorized complaint to a master incident."""
    link = store.link_complaint(
        complaint_id=req.complaint_id,
        master_incident_id=req.master_incident_id,
        link_type='officer_manual',
        linked_by_user_id=req.user_id,
        notes=req.notes
    )
    return {"status": "success", "link": link}
