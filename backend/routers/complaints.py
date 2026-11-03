from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import uuid
import random
from supabase import Client

from database import get_supabase
from auth import get_current_user, get_optional_current_user
from classifier import get_classifier, ComplaintClassifier, DEPARTMENTS
from vision_engine import get_vision_engine
from clustering import get_clustering_engine
from notifications import send_complaint_acknowledgment, send_complaint_resolution
from legal_rules import match_legal_rule_for_complaint
from sla_engine import calculate_service_deadline
from data_manager import record_activity_log, get_all_legal_rules
from schemas import (
    ComplaintCreate, ComplaintResponse, StatusUpdateRequest,
    ComplaintAssignRequest, DuplicateCheckRequest, DuplicateCheckResponse,
    ImageVerificationRequest, ImageVerificationResponse
)
from routers.employees import increment_employee_workload, record_employee_resolution

# NEX-CIV Duplicate Detection & Master Incident Integration
try:
    from duplicate_detection.retrieval.vector_store import get_vector_store
    from duplicate_detection.decision_engine.hybrid_engine import get_decision_engine
    from duplicate_detection.embeddings.embedder import get_embedder
    from duplicate_detection.cross_encoder.reranker import get_cross_encoder
    _HAS_HYBRID_DUPLICATE_ENGINE = True
except Exception as e:
    print(f"Notice: Duplicate detection hybrid engine import: {e}")
    _HAS_HYBRID_DUPLICATE_ENGINE = False

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

# Persistent local disk storage for complaints (resilient fallback against cloud network/RLS issues)
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_LOCAL_STORAGE_FILE = _DATA_DIR / "local_complaints.json"


def _load_stored_complaints() -> List[Dict[str, Any]]:
    if _LOCAL_STORAGE_FILE.exists():
        try:
            with open(_LOCAL_STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Notice loading local complaints: {e}")
    return []


def _save_all_local_complaints(items: List[Dict[str, Any]]):
    try:
        with open(_LOCAL_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(items[:500], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Notice saving local complaints: {e}")


_MEMORY_COMPLAINTS: List[Dict[str, Any]] = _load_stored_complaints()

# Seed baseline complaints if local file was empty
if len(_MEMORY_COMPLAINTS) == 0:
    _MEMORY_COMPLAINTS = [
        {
            "id": "a1111111-1111-1111-1111-111111111111",
            "grievance_ref_number": "AP-VMC-2026-NXCA111",
            "user_id": None,
            "title": "Massive road cave-in and sinkhole near Benz Circle Flyover",
            "description": "Deep dangerous trench and sinkhole formed on the main NH-16 highway approach slab after heavy downpour. Two-wheelers skidding and fatal accident hazard.",
            "category": "road",
            "department": "Roads & Buildings Department (R&B / Municipal)",
            "department_code": "road",
            "municipal_corporation": "VMC",
            "ward": "Ward 14",
            "landmark": "Benz Circle Flyover",
            "priority": "Critical",
            "priority_score": 98.5,
            "confidence": 0.994,
            "location_lat": 16.4990,
            "location_lng": 80.6540,
            "location_address": "[VMC] NH-16 Benz Circle Flyover, Vijayawada",
            "zone_type": "highway",
            "vulnerability_multiplier": 1.30,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
            "workflow_type": "ordinary_grievance",
            "legal_source": "AP Municipal Corporation Citizen Charter & PGRS Guidelines",
            "designated_officer": "Assistant Executive Engineer (AEE - Roads)",
            "assigned_team": "Roads & Buildings Rapid Response Team",
            "assigned_employee_id": "EMP-101",
            "citizen_name": "K. Venkat Rao",
            "citizen_email": "citizen@nexciv.org",
            "citizen_phone": "+91 98480 12345",
            "status": "pending",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 4,
            "image_hash": "c1f0a8d432b1e7f9",
            "defect_type": "pothole_crater",
            "visual_score": 92.0,
            "escalation_level": 1,
            "reopened_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "b2222222-2222-2222-2222-222222222222",
            "grievance_ref_number": "AP-GVMC-2026-NXCB222",
            "user_id": None,
            "title": "Drinking water pipeline burst and yellow contaminated supply near KGH Casualty",
            "description": "Main drinking water pipeline burst open and contaminated sewage is seeping in outside KGH Casualty Gate. Zero potable water for hospital wards.",
            "category": "water_supply",
            "department": "Water Supply & Quality Department",
            "department_code": "water_supply",
            "municipal_corporation": "GVMC",
            "ward": "Ward 22",
            "landmark": "KGH Casualty Gate",
            "priority": "Critical",
            "priority_score": 99.2,
            "confidence": 0.998,
            "location_lat": 17.7102,
            "location_lng": 83.3050,
            "location_address": "[GVMC] King George Hospital (KGH) Casualty Gate, Visakhapatnam",
            "zone_type": "hospital",
            "vulnerability_multiplier": 1.50,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
            "workflow_type": "ordinary_grievance",
            "legal_source": "AP Municipal Citizen Charter (Water Quality)",
            "designated_officer": "Water Works Inspector / Section Officer",
            "assigned_team": "Water Works Emergency Repair Squad",
            "assigned_employee_id": "EMP-117",
            "citizen_name": "Dr. K. Srinivas",
            "citizen_email": "kgh.doctor@nexciv.org",
            "citizen_phone": "+91 94401 55678",
            "status": "in_progress",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 5,
            "image_hash": "a4d2e9f180c5b3a7",
            "defect_type": "waterlogging_flood",
            "visual_score": 88.5,
            "escalation_level": 1,
            "reopened_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "c3333333-3333-3333-3333-333333333333",
            "grievance_ref_number": "AP-VMC-2026-NXCC333",
            "user_id": None,
            "title": "Live electric wire snapped and sparking on wet road outside bus terminal",
            "description": "High voltage electrical transmission line snapped from concrete pole and sparking in water puddle outside RTC Bus Terminal entrance.",
            "category": "street_lights",
            "department": "Electrical & Street Lighting Wing",
            "department_code": "street_lights",
            "municipal_corporation": "VMC",
            "ward": "Ward 8",
            "landmark": "PNBS Entrance",
            "priority": "Critical",
            "priority_score": 99.8,
            "confidence": 0.997,
            "location_lat": 16.5080,
            "location_lng": 80.6210,
            "location_address": "[VMC] Pandit Nehru Bus Station (PNBS), Vijayawada",
            "zone_type": "transit_hub",
            "vulnerability_multiplier": 1.25,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
            "workflow_type": "ordinary_grievance",
            "legal_source": "AP Municipal Corporation Citizen Charter (Electrical Wing)",
            "designated_officer": "Assistant Engineer (Electrical)",
            "assigned_team": "APEPDCL Lineman Quick Response Team",
            "assigned_employee_id": "EMP-125",
            "citizen_name": "M. Satish",
            "citizen_email": "satish.m@gmail.com",
            "citizen_phone": "+91 98490 22334",
            "status": "pending",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 2,
            "image_hash": "e8a9d12345bc6789",
            "defect_type": "night_hazard_blackout",
            "visual_score": 95.0,
            "escalation_level": 1,
            "reopened_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "d4444444-4444-4444-4444-444444444444",
            "grievance_ref_number": "AP-GMC-2026-NXCD444",
            "user_id": None,
            "title": "Toxic sewage overflow from blocked storm water nala",
            "description": "Main municipal canal choked with plastic waste, black sewage backflow submerging residential street and spreading foul stench.",
            "category": "drainage",
            "department": "Public Health & Drainage Department",
            "department_code": "drainage",
            "municipal_corporation": "GMC",
            "ward": "Ward 18",
            "landmark": "Brodipet 4th Line",
            "priority": "High",
            "priority_score": 82.0,
            "confidence": 0.985,
            "location_lat": 16.3010,
            "location_lng": 80.4410,
            "location_address": "[GMC] Brodipet 4th Line, Guntur",
            "zone_type": "residential",
            "vulnerability_multiplier": 1.00,
            "municipal_sla": "24 Hours (Next Shift Field Team)",
            "workflow_type": "ordinary_grievance",
            "legal_source": "AP Municipal Citizen Charter (Public Health Wing)",
            "designated_officer": "Assistant Engineer / Jetting In-charge",
            "assigned_team": "Drainage & Sewerage Jetting Crew",
            "assigned_employee_id": "EMP-109",
            "citizen_name": "V. Radhika",
            "citizen_email": "radhika.v@outlook.com",
            "citizen_phone": "+91 94411 98765",
            "status": "in_progress",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 4,
            "image_hash": "3f8b1c4e7d2a5099",
            "defect_type": "waterlogging_flood",
            "visual_score": 78.0,
            "escalation_level": 1,
            "reopened_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "e5555555-5555-5555-5555-555555555555",
            "grievance_ref_number": "AP-GVMC-2026-NXCE555",
            "user_id": None,
            "title": "Overflowing community garbage dumper bin and illegal roadside dumping",
            "description": "Commercial garbage bin overflowing for three days with stray cattle littering plastic across the street.",
            "category": "others",
            "department": "Sanitation & Solid Waste Management Wing",
            "department_code": "others",
            "municipal_corporation": "GVMC",
            "ward": "Sector 4",
            "landmark": "MVP Colony Sector 4",
            "priority": "Medium",
            "priority_score": 55.0,
            "confidence": 0.996,
            "location_lat": 17.7420,
            "location_lng": 83.3370,
            "location_address": "[GVMC] MVP Colony Sector 4, Visakhapatnam",
            "zone_type": "residential",
            "vulnerability_multiplier": 1.00,
            "municipal_sla": "48 - 72 Hours (Standard Municipal Maintenance)",
            "workflow_type": "ordinary_grievance",
            "legal_source": "AP Swachh Andhra Citizen Charter & Municipal SWM Rules",
            "designated_officer": "Sanitary Inspector / Ward Sanitation Officer",
            "assigned_team": "GVMC Sanitation Wing Zone 2",
            "assigned_employee_id": "EMP-133",
            "citizen_name": "P. Govind",
            "citizen_email": "govind.p@gmail.com",
            "citizen_phone": "+91 98660 45678",
            "status": "resolved",
            "action_taken": "Waste lifted using compactor truck and perimeter disinfected with lime powder.",
            "resolution_summary": "Garbage cleared and dumper bin sanitized.",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 1,
            "image_hash": "99bb11aa22cc33dd",
            "defect_type": "road_debris_or_pavement_damage",
            "visual_score": 52.0,
            "escalation_level": 1,
            "reopened_count": 0,
            "resolved_at": datetime.utcnow().isoformat() + "Z",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    ]
    _save_all_local_complaints(_MEMORY_COMPLAINTS)


def _enrich_complaint_sla(c: Dict[str, Any]) -> Dict[str, Any]:
    """Enriches complaint dictionary with legal workflow metadata and real-time SLA countdown."""
    cid = c.get("id") or "12345"
    corp = (c.get("municipal_corporation") or "GVMC").upper()
    if not c.get("grievance_ref_number"):
        short_id = cid[:6].upper().replace("-", "")
        c["grievance_ref_number"] = f"AP-{corp}-2026-NXC{short_id}"

    created_at_str = c.get("created_at")
    created_at_dt = None
    if created_at_str:
        try:
            created_at_dt = datetime.fromisoformat(created_at_str.replace("Z", ""))
        except Exception:
            created_at_dt = datetime.utcnow()
    else:
        created_at_dt = datetime.utcnow()

    rule_id = c.get("legal_rule_id")
    rule = None
    if rule_id:
        all_rules = get_all_legal_rules()
        for r in all_rules:
            if r.get("id") == rule_id:
                rule = r
                break

    if not rule:
        rule = match_legal_rule_for_complaint(
            category=c.get("category", "others"),
            title=c.get("title", ""),
            description=c.get("description", "")
        )

    if rule:
        c["legal_rule_id"] = rule.get("id")
        c["legal_source"] = rule.get("legal_source")
        c["workflow_type"] = c.get("workflow_type") or rule.get("workflow_type") or "ordinary_grievance"
        c["designated_officer"] = rule.get("designated_officer_title")
        c["appellate_authority"] = rule.get("first_appellate_authority")

        prescribed_days = rule.get("prescribed_timeline_days", 7)
        calc_method = rule.get("calculation_method", "working_days")
        deadline_info = calculate_service_deadline(
            created_at_dt=created_at_dt,
            prescribed_timeline_days=prescribed_days,
            calculation_method=calc_method,
            workflow_type=c["workflow_type"]
        )
        c["expected_resolution_date"] = deadline_info.get("deadline_date")
        c["deadline_formatted"] = deadline_info.get("deadline_formatted")
        c["sla_remaining_hours"] = deadline_info.get("remaining_hours")
        c["sla_is_overdue"] = deadline_info.get("is_overdue")
        c["sla_overdue_hours"] = deadline_info.get("overdue_duration_hours")
    else:
        c["deadline_formatted"] = "Timeline not configured – departmental action required"
        c["workflow_type"] = c.get("workflow_type") or "ordinary_grievance"
        c["sla_is_overdue"] = False

    return c


def _apply_privacy_mask(c: Dict[str, Any], current_user: dict) -> Dict[str, Any]:
    """Protects citizen personal data under Digital Personal Data Protection Act, 2023."""
    role = (current_user.get("role") or "").lower()
    user_id = current_user.get("id")
    if role in ["employee", "department"] or (user_id and user_id == c.get("user_id")):
        return c

    masked = dict(c)
    phone = masked.get("citizen_phone")
    if phone and len(phone) > 6:
        masked["citizen_phone"] = phone[:6] + " •••••"
    email = masked.get("citizen_email")
    if email and "@" in email:
        parts = email.split("@")
        masked["citizen_email"] = parts[0][:2] + "•••••@" + parts[1]
    return masked


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    complaint: ComplaintCreate,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase),
    classifier: ComplaintClassifier = Depends(get_classifier)
):
    """
    Creates a new civic complaint or notified public service application.
    Executes multimodal AI classification, legal workflow classification (Act No. 6 of 2018 vs Citizen Charter),
    deadline calculation via SLA engine, computer vision damage inspection, and duplicate detection.
    """
    # 1. Multimodal AI Classification (Title + Description Fusion)
    full_text = f"{complaint.title or ''} {complaint.description or ''}".strip()
    classification = classifier.classify_complaint(
        text=full_text,
        image_data=complaint.image_data or complaint.image_url,
        location_address=complaint.location_address,
        location_lat=complaint.location_lat,
        location_lng=complaint.location_lng
    )

    category = complaint.category or classification["category"]
    dept_info = DEPARTMENTS.get(category, DEPARTMENTS['others'])
    department = dept_info['name']
    department_code = dept_info['code']
    priority = classification["priority"]
    priority_score = classification.get("priority_score", 50.0)
    confidence = classification["confidence"]
    image_url = complaint.image_url or complaint.image_data

    loc_info = classification.get("location_info") or {}
    zone_type = loc_info.get("zone_type", "residential")
    vulnerability_multiplier = loc_info.get("vulnerability_multiplier", 1.0)
    municipal_sla = classification.get("municipal_sla", "48 - 72 Hours (Standard Municipal Maintenance)")
    assigned_team = f"{dept_info.get('short', 'Municipal')} Response Team"

    # 2. Legal Applicability & Deadline Calculation (Section 3 of Act No. 6 of 2018 / Citizen Charters)
    legal_rule = match_legal_rule_for_complaint(
        category=category,
        title=complaint.title,
        description=complaint.description
    )

    now_dt = datetime.utcnow()
    now_str = now_dt.isoformat() + "Z"
    item_id = str(uuid.uuid4())
    corp = (complaint.municipal_corporation or "GVMC").upper()
    random_suffix = random.randint(1000, 9999)
    grievance_ref_number = f"AP-{corp}-2026-NXC{random_suffix}"

    workflow_type = complaint.workflow_type or (legal_rule.get("workflow_type") if legal_rule else "ordinary_grievance")
    legal_source = legal_rule.get("legal_source") if legal_rule else "AP Municipal Citizen Charter & PGRS Guidelines"
    designated_officer = legal_rule.get("designated_officer_title") if legal_rule else "Municipal Engineer"
    appellate_authority = legal_rule.get("first_appellate_authority") if legal_rule else "Superintending Engineer / Commissioner"

    if legal_rule:
        deadline_info = calculate_service_deadline(
            created_at_dt=now_dt,
            prescribed_timeline_days=legal_rule.get("prescribed_timeline_days", 7),
            calculation_method=legal_rule.get("calculation_method", "working_days"),
            workflow_type=workflow_type
        )
        expected_resolution_date = deadline_info.get("deadline_date")
        deadline_formatted = deadline_info.get("deadline_formatted")
        sla_remaining_hours = deadline_info.get("remaining_hours")
        sla_is_overdue = deadline_info.get("is_overdue")
    else:
        expected_resolution_date = None
        deadline_formatted = "Timeline not configured – departmental action required"
        sla_remaining_hours = None
        sla_is_overdue = False

    # 3. Computer Vision Damage Verification
    vision_engine = get_vision_engine()
    raw_img = complaint.image_data or complaint.image_url
    image_hash = complaint.image_hash
    defect_type = complaint.defect_type
    visual_score = complaint.visual_score

    if raw_img:
        cv_res = vision_engine.verify_and_analyze_image(raw_img)
        if cv_res.get('is_valid_civic_image'):
            image_hash = cv_res.get('image_hash')
            defect_type = cv_res.get('defect_type')
            visual_score = cv_res.get('visual_severity_score')

    # 4. Intelligent Multilingual & Multimodal Duplicate Detection
    is_duplicate = False
    master_complaint_id = None
    upvote_count = 1

    candidate_obj = {
        'id': item_id,
        'title': complaint.title,
        'description': complaint.description,
        'category': category,
        'department_code': department_code,
        'department': department,
        'complaint_type': classification.get('complaint_type', 'other_civic_issue'),
        'location_lat': complaint.location_lat,
        'location_lng': complaint.location_lng,
        'location_address': complaint.location_address,
        'ward': complaint.ward,
        'municipal_corporation': corp,
        'image_hash': image_hash,
        'image_url': image_url,
        'priority': priority,
        'priority_score': priority_score,
        'assigned_team': assigned_team,
        'assigned_employee_id': complaint.assigned_employee_id,
        'created_at': now_str
    }

    if _HAS_HYBRID_DUPLICATE_ENGINE:
        try:
            vector_store = get_vector_store()
            hybrid_engine = get_decision_engine()
            embedder = get_embedder()
            cross_encoder = get_cross_encoder()

            # Encode and store embedding
            q_emb = embedder.encode(complaint.description)[0]
            vector_store.add_complaint_embedding(item_id, q_emb)

            # Retrieve candidate master incidents
            candidates = vector_store.search_candidates(
                query_embedding=q_emb,
                department_code=department_code,
                municipality=corp,
                top_k=8
            )

            matched_inc = None
            highest_score = 0.0

            for cand in candidates:
                sem_sim = cand.get('semantic_similarity', 0.5)
                cand_desc = cand.get('description', '') or cand.get('title', '')
                ce_score = cross_encoder.predict_pair(complaint.description, cand_desc) if cand_desc else sem_sim
                eval_res = hybrid_engine.evaluate_pair(candidate_obj, cand, sem_sim, ce_score)
                if eval_res['composite_score'] > highest_score and eval_res['decision'] == 'duplicate':
                    highest_score = eval_res['composite_score']
                    matched_inc = (cand, eval_res)

            if matched_inc:
                cand, eval_res = matched_inc
                is_duplicate = True
                master_complaint_id = cand['incident_id']
                vector_store.link_complaint(
                    complaint_id=item_id,
                    master_incident_id=master_complaint_id,
                    link_type='ai_auto',
                    similarity_score=eval_res['composite_score'],
                    notes=f"Auto-linked duplicate incident: {eval_res['composite_score']:.1%} match"
                )
                vector_store.record_prediction({
                    'new_complaint_id': item_id,
                    'candidate_incident_id': master_complaint_id,
                    'composite_duplicate_score': eval_res['composite_score'],
                    'semantic_similarity': eval_res['semantic_similarity'],
                    'location_similarity': eval_res['location_similarity'],
                    'cross_encoder_score': eval_res['cross_encoder_score'],
                    'temporal_compatibility': eval_res['temporal_compatibility'],
                    'image_similarity': eval_res['image_similarity'],
                    'distance_meters': eval_res['distance_meters'],
                    'decision': eval_res['decision'],
                    'reasons': eval_res['reasons']
                })
            else:
                # Register as a brand new Master Incident
                new_inc = vector_store.create_master_incident(candidate_obj)
                master_complaint_id = new_inc['incident_id']
                is_duplicate = False

        except Exception as e:
            print(f"Notice: Hybrid duplicate detection fallback: {e}")
            active_candidates = []
            if supabase is not None:
                try:
                    sup_res = supabase.table("complaints").select("*").neq("status", "resolved").limit(150).execute()
                    if sup_res.data:
                        active_candidates = sup_res.data
                except Exception:
                    pass
            if not active_candidates:
                active_candidates = [c for c in _MEMORY_COMPLAINTS if c.get("status") != "resolved"]

            duplicate_match = clustering_engine.find_duplicate(candidate_obj, active_candidates)
            if duplicate_match:
                is_duplicate = True
                master_complaint_id = duplicate_match['master_complaint_id']
    else:
        clustering_engine = get_clustering_engine()
        active_candidates = []
        if supabase is not None:
            try:
                sup_res = supabase.table("complaints").select("*").neq("status", "resolved").limit(150).execute()
                if sup_res.data:
                    active_candidates = sup_res.data
            except Exception:
                pass
        if not active_candidates:
            active_candidates = [c for c in _MEMORY_COMPLAINTS if c.get("status") != "resolved"]

        duplicate_match = clustering_engine.find_duplicate(candidate_obj, active_candidates)
        if duplicate_match:
            is_duplicate = True
            master_complaint_id = duplicate_match['master_complaint_id']

    if is_duplicate and master_complaint_id and supabase is not None:
        try:
            m_res = supabase.table("complaints").select("id, upvote_count, duplicate_count").eq("id", master_complaint_id).execute()
            if m_res.data:
                m_row = m_res.data[0]
                supabase.table("complaints").update({
                    "upvote_count": (m_row.get("upvote_count") or 1) + 1,
                    "duplicate_count": (m_row.get("duplicate_count") or 0) + 1
                }).eq("id", master_complaint_id).execute()
        except Exception as m_err:
            print(f"Notice: Master incident count increment note: {m_err}")

    images = complaint.images or ([image_url] if image_url else [])
    if not image_url and images and len(images) > 0:
        image_url = images[0]

    complaint_dict = {
        "id": item_id,
        "grievance_ref_number": grievance_ref_number,
        "user_id": current_user.get("id"),
        "title": complaint.title,
        "description": complaint.description,
        "category": category,
        "department": department,
        "department_code": department_code,
        "municipal_corporation": corp,
        "ward": complaint.ward,
        "landmark": complaint.landmark,
        "priority": priority,
        "priority_score": priority_score,
        "confidence": confidence,
        "location_lat": complaint.location_lat,
        "location_lng": complaint.location_lng,
        "location_address": complaint.location_address,
        "image_url": image_url,
        "images": images,
        "zone_type": zone_type,
        "vulnerability_multiplier": vulnerability_multiplier,
        "municipal_sla": municipal_sla,
        "workflow_type": workflow_type,
        "legal_rule_id": legal_rule.get("id") if legal_rule else None,
        "legal_source": legal_source,
        "designated_officer": designated_officer,
        "appellate_authority": appellate_authority,
        "expected_resolution_date": expected_resolution_date,
        "deadline_formatted": deadline_formatted,
        "sla_remaining_hours": sla_remaining_hours,
        "sla_is_overdue": sla_is_overdue,
        "sla_overdue_hours": 0,
        "assigned_team": assigned_team,
        "assigned_employee_id": complaint.assigned_employee_id,
        "citizen_name": complaint.citizen_name or current_user.get("name") or "Citizen",
        "citizen_email": complaint.citizen_email or current_user.get("email"),
        "citizen_phone": complaint.citizen_phone,
        "is_duplicate": is_duplicate,
        "master_complaint_id": master_complaint_id,
        "duplicate_count": 0,
        "upvote_count": upvote_count,
        "image_hash": image_hash,
        "defect_type": defect_type,
        "visual_score": visual_score,
        "cluster_id": None,
        "status": "pending",
        "escalation_level": 1,
        "reopened_count": 0,
        "appealed": False,
        "created_at": now_str,
        "updated_at": now_str
    }

    final_complaint = complaint_dict

    # 5. Insert into Supabase if connected
    if supabase is not None:
        try:
            loc_addr = complaint.location_address or ""
            corp_tag = f"[{corp}]"
            if corp_tag not in loc_addr:
                loc_addr = f"{corp_tag} {loc_addr}".strip()

            modern_payload = {
                "id": item_id,
                "title": complaint.title,
                "description": complaint.description,
                "category": category,
                "department": department,
                "department_code": department_code,
                "priority": priority,
                "priority_score": priority_score,
                "confidence": confidence,
                "location_lat": complaint.location_lat,
                "location_lng": complaint.location_lng,
                "location_address": loc_addr,
                "image_url": image_url,
                "zone_type": zone_type,
                "vulnerability_multiplier": vulnerability_multiplier,
                "municipal_sla": municipal_sla,
                "assigned_team": assigned_team,
                "assigned_employee_id": complaint.assigned_employee_id,
                "citizen_name": complaint_dict["citizen_name"],
                "citizen_email": complaint_dict["citizen_email"],
                "citizen_phone": complaint_dict["citizen_phone"],
                "is_duplicate": is_duplicate,
                "master_complaint_id": master_complaint_id,
                "image_hash": image_hash,
                "defect_type": defect_type,
                "visual_score": visual_score,
                "status": "pending"
            }
            if current_user.get("id"):
                modern_payload["user_id"] = current_user["id"]

            res = supabase.table("complaints").insert(modern_payload).execute()
            if res.data and len(res.data) > 0:
                final_complaint = {**complaint_dict, **res.data[0]}
        except Exception as e:
            # Resilient fallback if remote Supabase schema has master_complaint_id as UUID type
            if "22P02" in str(e) and modern_payload.get("master_complaint_id"):
                try:
                    retry_payload = {**modern_payload, "master_complaint_id": None}
                    res = supabase.table("complaints").insert(retry_payload).execute()
                    if res.data and len(res.data) > 0:
                        final_complaint = {**complaint_dict, **res.data[0]}
                except Exception as e2:
                    print(f"Supabase retry insert note: {e2}")
            else:
                print(f"Supabase insert note: {e}")

    # 6. Record Immutable Activity Logs
    record_activity_log(
        complaint_id=item_id,
        actor_role="citizen",
        actor_name=complaint_dict["citizen_name"],
        action="Grievance Registered",
        new_status="pending",
        comments=f"Reference: {grievance_ref_number}. Workflow: {workflow_type}. Mode: Public Portal."
    )
    record_activity_log(
        complaint_id=item_id,
        actor_role="system",
        actor_name="AI Legal Triage Engine",
        action="Legal Applicability & SLA Assigned",
        new_status="pending",
        comments=f"Governing source: {legal_source}. Expected resolution: {deadline_formatted}."
    )

    # 7. Automated Citizen Notification Receipt
    try:
        send_complaint_acknowledgment(final_complaint)
    except Exception as notif_err:
        print(f"Notification dispatch note: {notif_err}")

    # 8. Save in memory and isolated municipality storage
    _MEMORY_COMPLAINTS.insert(0, final_complaint)
    _save_all_local_complaints(_MEMORY_COMPLAINTS)
    try:
        from data_manager import save_complaint_isolated
        save_complaint_isolated(final_complaint)
    except Exception as e_iso:
        print(f"Isolated table save note: {e_iso}")

    return final_complaint


def _normalize_dept_key(d: Optional[str]) -> str:
    if not d:
        return ""
    val = d.lower().replace(" ", "_").strip()
    if val.startswith("road"):
        return "road"
    if val.startswith("drain"):
        return "drainage"
    if val.startswith("water"):
        return "water_supply"
    if val.startswith("street") or val.startswith("light") or val.startswith("electr"):
        return "street_lights"
    if val.startswith("other") or val.startswith("sanit"):
        return "others"
    return val.rstrip("s")


@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    municipal_corporation: Optional[str] = Query(None),
    assigned_employee_id: Optional[str] = Query(None),
    citizen_email: Optional[str] = Query(None),
    workflow_type: Optional[str] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    offset: int = Query(0),
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Lists complaints across Citizen, Employee, and Department Dashboards.
    Enriches each record with real-time statutory SLA countdown and DPDP Act privacy masking.
    """
    results = []

    # 1. Fetch from Supabase safely
    if supabase is not None:
        try:
            query = supabase.table("complaints").select("*")
            if status and status.lower() != 'all':
                query = query.eq("status", status.lower())

            res = query.order("created_at", desc=True).limit(200).execute()
            if res.data:
                for item in res.data:
                    cat = item.get("category", "others")
                    dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                    item["department"] = item.get("department") or dept_info["name"]
                    item["department_code"] = item.get("department_code") or dept_info["code"]
                    item["confidence"] = item.get("confidence") or 0.90

                    addr = item.get("location_address") or ""
                    if not item.get("municipal_corporation"):
                        if "[" in addr and "]" in addr:
                            try:
                                item["municipal_corporation"] = addr[addr.index("[")+1 : addr.index("]")].upper()
                            except Exception:
                                item["municipal_corporation"] = "GVMC"
                        else:
                            item["municipal_corporation"] = "GVMC"

                    results.append(item)
        except Exception as e:
            print(f"Supabase complaints fetch note: {e}")

    # 2. Merge with in-memory / local storage records
    existing_ids = {r.get("id") for r in results if r.get("id")}
    for m in _MEMORY_COMPLAINTS:
        mid = m.get("id")
        if mid not in existing_ids:
            results.append(m)

    # Enforce municipality isolation for employee role unless overridden by query param
    if current_user and current_user.get('role') == 'employee':
        user_muni = current_user.get('municipalityCode') or current_user.get('municipality_code')
        if user_muni:
            results = [c for c in results if c.get('municipal_corporation') == user_muni]
    # Allow explicit query param to override (e.g., admin dashboards)
    if municipal_corporation and municipal_corporation.lower() != 'all':
        target_corp = municipal_corporation.strip().upper()
        from data_manager import get_isolated_municipality_complaints
        try:
            results = get_isolated_municipality_complaints(target_corp)
        except Exception:
            pass

    # 3. Dynamic SLA countdown & DPDP privacy protection
    enriched_list = []
    for c in results:
        enriched = _enrich_complaint_sla(c)
        protected = _apply_privacy_mask(enriched, current_user)
        enriched_list.append(protected)

    # 4. Filtering
    filtered = []
    for c in enriched_list:
        cat_norm = _normalize_dept_key(c.get("category"))
        dept_norm = _normalize_dept_key(c.get("department_code") or c.get("department"))
        c_prio = (c.get("priority") or "").lower()
        c_stat = (c.get("status") or "").lower()
        c_corp = (c.get("municipal_corporation") or "").upper()
        c_addr = (c.get("location_address") or "").upper()
        c_emp = (c.get("assigned_employee_id") or "")
        c_email = (c.get("citizen_email") or "").lower()
        c_wf = (c.get("workflow_type") or "ordinary_grievance").lower()
        c_overdue = c.get("sla_is_overdue", False)

        if category and category.lower() != 'all':
            target = _normalize_dept_key(category)
            if cat_norm != target and dept_norm != target:
                continue
        if department and department.lower() != 'all':
            target = _normalize_dept_key(department)
            if dept_norm != target and cat_norm != target:
                continue
        if priority and priority.lower() != 'all' and c_prio != priority.lower():
            continue
        if status and status.lower() != 'all' and c_stat != status.lower():
            continue
        // Enforce municipality isolation for employee role unless overridden by query param
    if current_user and current_user.get('role') == 'employee':
        user_muni = current_user.get('municipalityCode') or current_user.get('municipality_code')
        if user_muni:
            results = [c for c in results if c.get('municipal_corporation') == user_muni]
    # Allow explicit query param to override (e.g., admin dashboards)
    if municipal_corporation and municipal_corporation.lower() != 'all':
        target_corp = municipal_corporation.strip().upper()
        from data_manager import get_isolated_municipality_complaints
        try:
            results = get_isolated_municipality_complaints(target_corp)
            target_corp = municipal_corporation.strip().upper()
            if c_corp != target_corp and target_corp not in c_addr:
                continue
        if assigned_employee_id and assigned_employee_id.lower() != 'all':
            target_emp = assigned_employee_id.strip().upper()
            if c_emp.upper() != target_emp and target_emp not in (c.get("assigned_team") or "").upper():
                continue
        if citizen_email and citizen_email.lower() != 'all':
            target_email = citizen_email.strip().lower()
            if c_email != target_email and target_email not in c_email:
                continue
        if workflow_type and workflow_type.lower() != 'all':
            if c_wf != workflow_type.strip().lower():
                continue
        if is_overdue is not None:
            if c_overdue != is_overdue:
                continue

        filtered.append(c)

    # 5. Optional Free-Text Search
    if search and search.strip():
        q = search.strip().lower()
        filtered = [
            r for r in filtered
            if q in (r.get("title") or "").lower()
            or q in (r.get("description") or "").lower()
            or q in (r.get("location_address") or "").lower()
            or q in (r.get("assigned_team") or "").lower()
            or q in (r.get("grievance_ref_number") or "").lower()
            or q in (r.get("id") or "").lower()
            or q in (r.get("municipal_corporation") or "").lower()
            or q in (r.get("ward") or "").lower()
            or q in (r.get("landmark") or "").lower()
        ]

    return filtered[offset : offset + limit]


@router.get("/analytics")
def get_analytics(
    municipal_corporation: Optional[str] = Query(None),
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Computes real-time municipal analytics across Roads, Drainage, Water Supply, Street Lights, and Sanitation.
    Calculates actual database records: pending, in_progress, resolved, reopened, overdue, and resolution rates.
    """
    all_items = []
    if supabase is not None:
        try:
            res = supabase.table("complaints").select("*").execute()
            if res.data:
                all_items.extend(res.data)
        except Exception:
            pass

    existing_ids = {r.get("id") for r in all_items}
    for m in _MEMORY_COMPLAINTS:
        if m.get("id") not in existing_ids:
            all_items.append(m)

    // Enforce municipality isolation for employee role unless overridden by query param
    if current_user and current_user.get('role') == 'employee':
        user_muni = current_user.get('municipalityCode') or current_user.get('municipality_code')
        if user_muni:
            results = [c for c in results if c.get('municipal_corporation') == user_muni]
    # Allow explicit query param to override (e.g., admin dashboards)
    if municipal_corporation and municipal_corporation.lower() != 'all':
        target_corp = municipal_corporation.strip().upper()
        from data_manager import get_isolated_municipality_complaints
        try:
            results = get_isolated_municipality_complaints(target_corp)
        target_mc = municipal_corporation.strip().upper()
        from data_manager import get_isolated_municipality_complaints
        try:
            all_items = get_isolated_municipality_complaints(target_mc)
        except Exception:
            all_items = [c for c in _MEMORY_COMPLAINTS if (c.get("municipal_corporation") or "").upper() == target_mc]

    total_count = len(all_items)

    dept_stats = {}
    for code, info in DEPARTMENTS.items():
        dept_stats[code] = {
            "name": info["name"],
            "code": code,
            "short": info["short"],
            "head": info["head"],
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "critical": 0,
            "high": 0,
            "overdue": 0,
            "resolution_rate": 0.0,
            "avg_confidence": 0.92
        }

    status_counts = {"pending": 0, "in_progress": 0, "resolved": 0}
    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    overdue_count = 0
    reopened_count = 0
    escalated_count = 0

    for item in all_items:
        enriched = _enrich_complaint_sla(item)
        raw_cat = (item.get("category") or item.get("department_code") or "others").lower().replace(" ", "_")
        code = raw_cat if raw_cat in DEPARTMENTS else "others"
        item_status = (item.get("status") or "pending").lower()
        item_priority = item.get("priority") or "Medium"

        if item_status not in status_counts:
            item_status = "pending"
        status_counts[item_status] += 1

        if item_priority in priority_counts:
            priority_counts[item_priority] += 1

        if enriched.get("sla_is_overdue") and item_status != "resolved":
            overdue_count += 1
        if (enriched.get("reopened_count") or 0) > 0:
            reopened_count += 1
        if (enriched.get("escalation_level") or 1) > 1:
            escalated_count += 1

        d = dept_stats[code]
        d["total"] += 1
        if item_status == "pending":
            d["pending"] += 1
        elif item_status == "in_progress":
            d["in_progress"] += 1
        elif item_status == "resolved":
            d["resolved"] += 1

        if enriched.get("sla_is_overdue") and item_status != "resolved":
            d["overdue"] += 1
        if item_priority == "Critical":
            d["critical"] += 1
        elif item_priority == "High":
            d["high"] += 1

    for code, d in dept_stats.items():
        if d["total"] > 0:
            d["resolution_rate"] = round((d["resolved"] / d["total"]) * 100, 1)

    overall_res_rate = round((status_counts["resolved"] / total_count * 100), 1) if total_count > 0 else 0.0

    return {
        "total_complaints": total_count,
        "awaiting_assignment": status_counts.get("pending", 0),
        "in_progress": status_counts.get("in_progress", 0),
        "resolved": status_counts.get("resolved", 0),
        "overdue": overdue_count,
        "reopened": reopened_count,
        "escalated": escalated_count,
        "overall_resolution_rate": overall_res_rate,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_department": dept_stats,
        "departments_list": list(DEPARTMENTS.keys()),
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/hotspots")
def list_hotspots(
    radius_meters: float = Query(100.0, ge=10.0, le=1000.0),
    supabase: Client = Depends(get_supabase)
):
    """Clusters complaints into geographical hotspots to combine duplicate work orders."""
    clustering_engine = get_clustering_engine()
    items = []
    if supabase is not None:
        try:
            sup_res = supabase.table("complaints").select("*").neq("status", "resolved").execute()
            if sup_res.data:
                items = sup_res.data
        except Exception:
            pass
    if not items:
        items = [c for c in _MEMORY_COMPLAINTS if c.get("status") != "resolved"]

    hotspots = clustering_engine.cluster_hotspots(items, radius_meters=radius_meters)
    return {"total_hotspots": len(hotspots), "hotspots": hotspots}


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate_complaint(
    req: DuplicateCheckRequest,
    supabase: Client = Depends(get_supabase)
):
    clustering_engine = get_clustering_engine()
    vision_engine = get_vision_engine()

    img_hash = None
    if req.image_data:
        cv_res = vision_engine.verify_and_analyze_image(req.image_data)
        img_hash = cv_res.get('image_hash')

    candidate_obj = {
        'title': req.title or "",
        'description': req.description,
        'category': req.category,
        'location_lat': req.location_lat,
        'location_lng': req.location_lng,
        'location_address': req.location_address,
        'image_hash': img_hash,
        'image_url': req.image_data
    }

    active_candidates = []
    if supabase is not None:
        try:
            sup_res = supabase.table("complaints").select("*").neq("status", "resolved").limit(150).execute()
            if sup_res.data:
                active_candidates = sup_res.data
        except Exception:
            pass
    if not active_candidates:
        active_candidates = [c for c in _MEMORY_COMPLAINTS if c.get("status") != "resolved"]

    match = clustering_engine.find_duplicate(candidate_obj, active_candidates)
    if match:
        return DuplicateCheckResponse(
            is_duplicate=True,
            master_complaint_id=match['master_complaint_id'],
            master_title=match.get('master_title'),
            similarity_score=match['similarity_score'],
            distance_meters=match['distance_meters'],
            reasons=match['reasons']
        )
    return DuplicateCheckResponse(is_duplicate=False)


@router.post("/verify-image", response_model=ImageVerificationResponse)
def verify_complaint_image(req: ImageVerificationRequest):
    vision_engine = get_vision_engine()
    res = vision_engine.verify_and_analyze_image(req.image_data)
    return ImageVerificationResponse(**res)


def _matches_complaint_id(item_id: str, target: str) -> bool:
    if not item_id or not target:
        return False
    clean_target = target.strip()
    if clean_target.upper().startswith("NXC-") or clean_target.upper().startswith("NEX-") or clean_target.upper().startswith("AP-"):
        parts = clean_target.split("-")
        clean_target = parts[-1].strip()
    c_target = clean_target.lower()
    c_target_compact = c_target.replace("-", "")

    mid = item_id.strip().lower()
    mid_compact = mid.replace("-", "")

    return (
        mid == c_target
        or mid.startswith(c_target)
        or mid_compact.startswith(c_target_compact)
        or (len(c_target) >= 4 and c_target in mid)
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Fetches single complaint by ID or Reference Code (e.g. NXC-A11111 or AP-VMC-2026-NXC1234).
    Enriches with real-time statutory SLA countdown and DPDP Act privacy masking.
    """
    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id) or _matches_complaint_id(m.get("grievance_ref_number", ""), complaint_id):
            enriched = _enrich_complaint_sla(m)
            return _apply_privacy_mask(enriched, current_user)

    if supabase is not None:
        try:
            res = supabase.table("complaints").select("*").eq("id", complaint_id.strip()).execute()
            if res.data and len(res.data) > 0:
                item = res.data[0]
                cat = item.get("category", "others")
                dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                item["department"] = item.get("department") or dept_info["name"]
                item["department_code"] = item.get("department_code") or dept_info["code"]
                enriched = _enrich_complaint_sla(item)
                return _apply_privacy_mask(enriched, current_user)

            res2 = supabase.table("complaints").select("*").order("created_at", desc=True).limit(200).execute()
            if res2.data:
                for item in res2.data:
                    if _matches_complaint_id(item.get("id"), complaint_id):
                        cat = item.get("category", "others")
                        dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                        item["department"] = item.get("department") or dept_info["name"]
                        item["department_code"] = item.get("department_code") or dept_info["code"]
                        enriched = _enrich_complaint_sla(item)
                        return _apply_privacy_mask(enriched, current_user)
        except Exception as e:
            print(f"Supabase complaint lookup note: {e}")

    raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found")


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: str,
    payload: StatusUpdateRequest,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Updates complaint status with mandatory resolution remarks & immutable activity audit logging.
    Enforces Rule 5.3: An employee must not mark resolved without providing action taken and resolution summary.
    """
    new_status = payload.status.lower()
    now_str = datetime.utcnow().isoformat() + "Z"

    # Mandatory Resolution Remarks Validation
    if new_status == "resolved":
        resolution_desc = (payload.action_taken or payload.notes or payload.resolution_summary or "").strip()
        if not resolution_desc:
            raise HTTPException(
                status_code=400,
                detail="Mandatory Resolution Requirement: Action taken and resolution summary must be provided to mark a grievance resolved."
            )

    # Mandatory Rejection Reason Validation
    if new_status in ["rejected", "closed_unresolved"]:
        reason_desc = (payload.rejection_reason or payload.notes or "").strip()
        if not reason_desc:
            raise HTTPException(
                status_code=400,
                detail="Statutory Requirement: Clear recorded reasons must be provided for grievance rejection under Section 8 of Act No. 6 of 2018."
            )

    # Update in memory
    updated_record = None
    real_item_id = complaint_id
    emp_to_resolve = payload.resolved_by_employee_id
    old_status = "pending"

    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id) or _matches_complaint_id(m.get("grievance_ref_number", ""), complaint_id):
            real_item_id = m.get("id") or complaint_id
            old_status = m.get("status", "pending")
            m["status"] = new_status
            m["updated_at"] = now_str
            if payload.notes:
                m["resolution_notes"] = payload.notes
            if payload.action_taken:
                m["action_taken"] = payload.action_taken
            if payload.resolution_summary:
                m["resolution_summary"] = payload.resolution_summary
            if payload.rejection_reason:
                m["rejection_reason"] = payload.rejection_reason
            if payload.resolution_proof_url:
                m["resolution_proof_url"] = payload.resolution_proof_url
            if new_status == "resolved":
                m["resolved_at"] = now_str
                if not emp_to_resolve:
                    emp_to_resolve = m.get("assigned_employee_id")
                if old_status != "resolved" and emp_to_resolve:
                    record_employee_resolution(emp_to_resolve, supabase)
            updated_record = m
            break

    if updated_record:
        _save_all_local_complaints(_MEMORY_COMPLAINTS)
        try:
            from data_manager import save_complaint_isolated
            save_complaint_isolated(updated_record)
        except Exception:
            pass

    # Record Immutable Audit Activity Log
    actor_name = current_user.get("name") or "Municipal Officer"
    actor_id = current_user.get("id") or payload.resolved_by_employee_id or "EMP-101"
    log_action = "Grievance Status Transition"
    log_comment = payload.action_taken or payload.notes or payload.rejection_reason or f"Status changed to {new_status}"
    record_activity_log(
        complaint_id=real_item_id,
        actor_role=current_user.get("role") or "employee",
        actor_id=actor_id,
        actor_name=actor_name,
        action=log_action,
        previous_status=old_status,
        new_status=new_status,
        comments=log_comment
    )

    final_result = updated_record

    # Update in Supabase
    if supabase is not None:
        try:
            update_body = {"status": new_status, "updated_at": now_str}
            if payload.notes:
                update_body["resolution_notes"] = payload.notes
            if payload.resolution_proof_url:
                update_body["resolution_proof_url"] = payload.resolution_proof_url
            if new_status == "resolved":
                update_body["resolved_at"] = now_str
            res = supabase.table("complaints").update(update_body).eq("id", real_item_id).execute()
            if res.data and len(res.data) > 0:
                item = res.data[0]
                if updated_record:
                    item.update(updated_record)
                final_result = item
        except Exception as e:
            print(f"Supabase complaint status update note: {e}")

    if not final_result:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if new_status == "resolved":
        try:
            send_complaint_resolution(final_result)
        except Exception as res_err:
            print(f"Resolution notification dispatch note: {res_err}")

    enriched = _enrich_complaint_sla(final_result)
    return _apply_privacy_mask(enriched, current_user)


@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: str,
    payload: ComplaintAssignRequest,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Assigns or reassigns a complaint to a municipal employee.
    Maintains immutable reassignment logs with recorded reasons (Rule 6.3).
    """
    now_str = datetime.utcnow().isoformat() + "Z"
    increment_employee_workload(payload.employee_id, supabase)

    updated_record = None
    real_item_id = complaint_id
    old_assigned_emp = None

    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id) or _matches_complaint_id(m.get("grievance_ref_number", ""), complaint_id):
            real_item_id = m.get("id") or complaint_id
            old_assigned_emp = m.get("assigned_employee_id")
            m["assigned_employee_id"] = payload.employee_id
            if payload.assigned_team:
                m["assigned_team"] = payload.assigned_team
            if m.get("status") == "pending":
                m["status"] = "in_progress"
            m["updated_at"] = now_str
            updated_record = m
            break

    if updated_record:
        _save_all_local_complaints(_MEMORY_COMPLAINTS)
        try:
            from data_manager import save_complaint_isolated
            save_complaint_isolated(updated_record)
        except Exception:
            pass

    # Record Immutable Assignment / Reassignment Log
    actor_name = current_user.get("name") or "Department Head"
    action_label = "Employee Reassigned" if old_assigned_emp else "Employee Assigned"
    comment_text = f"Assigned to {payload.employee_id} ({payload.assigned_team or 'Field Team'})."
    if payload.reassignment_reason:
        comment_text += f" Reason: {payload.reassignment_reason}"

    record_activity_log(
        complaint_id=real_item_id,
        actor_role="department",
        actor_id=current_user.get("id") or "DEPT-HEAD",
        actor_name=actor_name,
        action=action_label,
        previous_status=updated_record.get("status") if updated_record else "pending",
        new_status="in_progress",
        comments=comment_text
    )

    if supabase is not None:
        try:
            update_body = {
                "assigned_employee_id": payload.employee_id,
                "status": "in_progress",
                "updated_at": now_str
            }
            if payload.assigned_team:
                update_body["assigned_team"] = payload.assigned_team
            supabase.table("complaints").update(update_body).eq("id", real_item_id).execute()
        except Exception as e:
            print(f"Supabase complaint assignment note: {e}")

    if updated_record:
        enriched = _enrich_complaint_sla(updated_record)
        return _apply_privacy_mask(enriched, current_user)

    raise HTTPException(status_code=404, detail="Complaint not found")


@router.post("/{complaint_id}/upvote")
def upvote_complaint(
    complaint_id: str,
    supabase: Client = Depends(get_supabase)
):
    updated_record = None
    real_item_id = complaint_id
    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id):
            real_item_id = m.get("id") or complaint_id
            m["upvote_count"] = m.get("upvote_count", 1) + 1
            updated_record = m
            break

    if updated_record:
        _save_all_local_complaints(_MEMORY_COMPLAINTS)

    if supabase is not None:
        try:
            supabase.rpc("increment_upvote", {"row_id": real_item_id}).execute()
        except Exception:
            pass

    if updated_record:
        return {"id": real_item_id, "upvote_count": updated_record.get("upvote_count", 1)}

    return {"id": complaint_id, "upvote_count": 2}
