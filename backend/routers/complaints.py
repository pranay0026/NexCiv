from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import uuid
from supabase import Client

from database import get_supabase
from auth import get_current_user, get_optional_current_user
from classifier import get_classifier, ComplaintClassifier, DEPARTMENTS
from vision_engine import get_vision_engine
from clustering import get_clustering_engine
from notifications import send_complaint_acknowledgment, send_complaint_resolution
from schemas import (
    ComplaintCreate, ComplaintResponse, StatusUpdateRequest,
    ComplaintAssignRequest, DuplicateCheckRequest, DuplicateCheckResponse,
    ImageVerificationRequest, ImageVerificationResponse
)
from routers.employees import increment_employee_workload, record_employee_resolution

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
            "user_id": None,
            "title": "Massive road cave-in and sinkhole near Benz Circle Flyover",
            "description": "Deep dangerous trench and sinkhole formed on the main NH-16 highway approach slab after heavy downpour. Two-wheelers skidding and fatal accident hazard.",
            "category": "road",
            "department": "Roads & Buildings Department (R&B / Municipal)",
            "department_code": "road",
            "priority": "Critical",
            "priority_score": 98.5,
            "confidence": 0.994,
            "location_lat": 16.4990,
            "location_lng": 80.6540,
            "location_address": "NH-16 Benz Circle Flyover, Vijayawada",
            "zone_type": "highway",
            "vulnerability_multiplier": 1.30,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
            "assigned_team": "Roads & Buildings Rapid Response Team",
            "assigned_employee_id": "EMP-101",
            "citizen_name": "Citizen",
            "citizen_email": "citizen@nexciv.org",
            "citizen_phone": "+91 98480 12345",
            "status": "pending",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 3,
            "image_hash": "c1f0a8d432b1e7f9",
            "defect_type": "pothole_crater",
            "visual_score": 92.0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "b2222222-2222-2222-2222-222222222222",
            "user_id": None,
            "title": "Drinking water pipeline burst and yellow contaminated supply near KGH Casualty",
            "description": "Main drinking water pipeline burst open and contaminated sewage is seeping in outside KGH Casualty Gate. Zero potable water for hospital wards.",
            "category": "water_supply",
            "department": "Water Supply & Quality Department",
            "department_code": "water_supply",
            "priority": "Critical",
            "priority_score": 99.2,
            "confidence": 0.998,
            "location_lat": 17.7102,
            "location_lng": 83.3050,
            "location_address": "King George Hospital (KGH) Casualty Gate, Visakhapatnam",
            "zone_type": "hospital",
            "vulnerability_multiplier": 1.50,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
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
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "c3333333-3333-3333-3333-333333333333",
            "user_id": None,
            "title": "Live electric wire snapped and sparking on wet road outside bus terminal",
            "description": "High voltage electrical transmission line snapped from concrete pole and sparking in water puddle outside RTC Bus Terminal entrance.",
            "category": "street_lights",
            "department": "Electrical & Street Lighting Wing",
            "department_code": "street_lights",
            "priority": "Critical",
            "priority_score": 99.8,
            "confidence": 0.997,
            "location_lat": 16.5080,
            "location_lng": 80.6210,
            "location_address": "Pandit Nehru Bus Station (PNBS), Vijayawada",
            "zone_type": "transit_hub",
            "vulnerability_multiplier": 1.25,
            "municipal_sla": "0 - 4 Hours (Emergency Dispatch)",
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
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "d4444444-4444-4444-4444-444444444444",
            "user_id": None,
            "title": "Toxic sewage overflow from blocked storm water nala",
            "description": "Main municipal canal choked with plastic waste, black sewage backflow submerging residential street and spreading foul stench.",
            "category": "drainage",
            "department": "Public Health & Drainage Department",
            "department_code": "drainage",
            "priority": "High",
            "priority_score": 82.0,
            "confidence": 0.985,
            "location_lat": 16.3010,
            "location_lng": 80.4410,
            "location_address": "Brodipet 4th Line, Guntur",
            "zone_type": "residential",
            "vulnerability_multiplier": 1.00,
            "municipal_sla": "24 Hours (Next Shift Field Team)",
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
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": "e5555555-5555-5555-5555-555555555555",
            "user_id": None,
            "title": "Overflowing community garbage dumper bin and illegal roadside dumping",
            "description": "Commercial garbage bin overflowing for three days with stray cattle littering plastic across the street.",
            "category": "others",
            "department": "Sanitation & Solid Waste Management Wing",
            "department_code": "others",
            "priority": "Medium",
            "priority_score": 55.0,
            "confidence": 0.996,
            "location_lat": 17.7420,
            "location_lng": 83.3370,
            "location_address": "MVP Colony Sector 4, Visakhapatnam",
            "zone_type": "residential",
            "vulnerability_multiplier": 1.00,
            "municipal_sla": "48 - 72 Hours (Standard Municipal Maintenance)",
            "assigned_team": "GVMC Sanitation Wing Zone 2",
            "assigned_employee_id": "EMP-133",
            "citizen_name": "P. Govind",
            "citizen_email": "govind.p@gmail.com",
            "citizen_phone": "+91 98660 45678",
            "status": "resolved",
            "is_duplicate": False,
            "master_complaint_id": None,
            "duplicate_count": 0,
            "upvote_count": 1,
            "image_hash": "99bb11aa22cc33dd",
            "defect_type": "road_debris_or_pavement_damage",
            "visual_score": 52.0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    ]
    _save_all_local_complaints(_MEMORY_COMPLAINTS)


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    complaint: ComplaintCreate,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase),
    classifier: ComplaintClassifier = Depends(get_classifier)
):
    """
    Creates a new civic complaint.
    Executes multimodal AI classification, computer vision damage inspection,
    geospatial duplicate detection, and notification dispatch.
    Persists to Supabase and resilient local storage.
    """
    # 1. Multimodal AI Classification
    classification = classifier.classify_complaint(
        text=complaint.description,
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

    # 2. Computer Vision Damage Verification (Phase 2)
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

    # 3. Duplicate Detection across Active Complaints (Phase 2)
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

    candidate_obj = {
        'title': complaint.title,
        'description': complaint.description,
        'category': category,
        'department_code': department_code,
        'location_lat': complaint.location_lat,
        'location_lng': complaint.location_lng,
        'location_address': complaint.location_address,
        'image_hash': image_hash,
        'image_url': image_url
    }

    duplicate_match = clustering_engine.find_duplicate(candidate_obj, active_candidates)
    is_duplicate = False
    master_complaint_id = None
    upvote_count = 1

    if duplicate_match:
        is_duplicate = True
        master_complaint_id = duplicate_match['master_complaint_id']
        for m in _MEMORY_COMPLAINTS:
            if m.get('id') == master_complaint_id:
                m['upvote_count'] = m.get('upvote_count', 1) + 1
                m['duplicate_count'] = m.get('duplicate_count', 0) + 1
                m['priority_score'] = min(100.0, m.get('priority_score', 50.0) + 5.0)
                break
        if supabase is not None:
            try:
                supabase.rpc("increment_upvote", {"row_id": master_complaint_id}).execute()
            except Exception:
                pass

    now_str = datetime.utcnow().isoformat() + "Z"
    item_id = str(uuid.uuid4())

    images = complaint.images or ([image_url] if image_url else [])
    if not image_url and images and len(images) > 0:
        image_url = images[0]

    complaint_dict = {
        "id": item_id,
        "user_id": current_user.get("id"),
        "title": complaint.title,
        "description": complaint.description,
        "category": category,
        "department": department,
        "department_code": department_code,
        "municipal_corporation": complaint.municipal_corporation or "GVMC",
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
        "created_at": now_str,
        "updated_at": now_str
    }

    final_complaint = complaint_dict

    # 4. Insert into Supabase if connected
    if supabase is not None:
        try:
            # Include corporation prefix in address so it is permanently preserved across cloud schemas
            loc_addr = complaint.location_address or ""
            corp_tag = f"[{complaint_dict['municipal_corporation']}]"
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
                for field in ["municipal_corporation", "ward", "landmark", "images", "citizen_email", "citizen_phone"]:
                    if complaint_dict.get(field):
                        final_complaint[field] = complaint_dict[field]
        except Exception as e:
            # Fall back to persistent storage
            print(f"Supabase insert note: {e}")

    # 5. Automated Citizen Notification Receipt (Email & SMS)
    try:
        send_complaint_acknowledgment(final_complaint)
    except Exception as notif_err:
        print(f"Notification dispatch note: {notif_err}")

    # 6. Save in memory and persist locally to disk
    _MEMORY_COMPLAINTS.insert(0, final_complaint)
    _save_all_local_complaints(_MEMORY_COMPLAINTS)

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
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    offset: int = Query(0),
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Lists complaints across Citizen Portal, Employee Portal, and Department Command Center.
    Combines live cloud records and persistent local storage with no duplicates.
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
                    
                    # Extract corporation from location_address if missing
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

    # 3. Comprehensive Python filtering across ALL fields
    filtered = []
    for c in results:
        cat_norm = _normalize_dept_key(c.get("category"))
        dept_norm = _normalize_dept_key(c.get("department_code") or c.get("department"))
        c_prio = (c.get("priority") or "").lower()
        c_stat = (c.get("status") or "").lower()
        c_corp = (c.get("municipal_corporation") or "GVMC").upper()
        c_addr = (c.get("location_address") or "").upper()
        c_emp = (c.get("assigned_employee_id") or "")
        c_email = (c.get("citizen_email") or "").lower()

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
        if municipal_corporation and municipal_corporation.lower() != 'all':
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

        filtered.append(c)

    # 4. Apply optional free-text search filter
    if search and search.strip():
        q = search.strip().lower()
        filtered = [
            r for r in filtered
            if q in (r.get("title") or "").lower()
            or q in (r.get("description") or "").lower()
            or q in (r.get("location_address") or "").lower()
            or q in (r.get("assigned_team") or "").lower()
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
    Used by Department Heads for operations monitoring.
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

    if municipal_corporation and municipal_corporation.lower() != 'all':
        target_mc = municipal_corporation.strip().upper()
        all_items = [c for c in all_items if (c.get("municipal_corporation") or "GVMC").upper() == target_mc]

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
            "resolution_rate": 0.0,
            "avg_confidence": 0.92
        }

    status_counts = {"pending": 0, "in_progress": 0, "resolved": 0}
    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for item in all_items:
        raw_cat = (item.get("category") or item.get("department_code") or "others").lower().replace(" ", "_")
        code = raw_cat if raw_cat in DEPARTMENTS else "others"
        item_status = (item.get("status") or "pending").lower()
        item_priority = item.get("priority") or "Medium"

        if item_status not in status_counts:
            item_status = "pending"
        status_counts[item_status] += 1

        if item_priority in priority_counts:
            priority_counts[item_priority] += 1

        d = dept_stats[code]
        d["total"] += 1
        if item_status == "pending":
            d["pending"] += 1
        elif item_status == "in_progress":
            d["in_progress"] += 1
        elif item_status == "resolved":
            d["resolved"] += 1

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
    """Checks if a proposed complaint is a duplicate of any active complaint in the city."""
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
    """Analyzes photo for defect authenticity, damage severity, and perceptual fingerprint."""
    vision_engine = get_vision_engine()
    res = vision_engine.verify_and_analyze_image(req.image_data)
    return ImageVerificationResponse(**res)


def _matches_complaint_id(item_id: str, target: str) -> bool:
    if not item_id or not target:
        return False
    clean_target = target.strip()
    if clean_target.upper().startswith("NXC-") or clean_target.upper().startswith("NEX-"):
        clean_target = clean_target[4:].strip()
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
    Fetches single complaint by ID for tracking.
    Supports full UUID, short code (e.g. NXC-62A65F), or prefix.
    """
    # 1. Search in local / memory complaints first for speed and certainty
    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id):
            return m

    # 2. Try Supabase
    if supabase is not None:
        try:
            # Exact match
            res = supabase.table("complaints").select("*").eq("id", complaint_id.strip()).execute()
            if res.data and len(res.data) > 0:
                item = res.data[0]
                cat = item.get("category", "others")
                dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                item["department"] = item.get("department") or dept_info["name"]
                item["department_code"] = item.get("department_code") or dept_info["code"]
                return item

            # Scan recent complaints to match prefix/short ID
            res2 = supabase.table("complaints").select("*").order("created_at", desc=True).limit(200).execute()
            if res2.data:
                for item in res2.data:
                    if _matches_complaint_id(item.get("id"), complaint_id):
                        cat = item.get("category", "others")
                        dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                        item["department"] = item.get("department") or dept_info["name"]
                        item["department_code"] = item.get("department_code") or dept_info["code"]
                        return item
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
    Updates complaint status ('pending', 'in_progress', 'resolved').
    Saves work notes, proof of resolution, and updates employee workload math automatically.
    """
    new_status = payload.status.lower()
    now_str = datetime.utcnow().isoformat() + "Z"

    # Update in memory
    updated_record = None
    real_item_id = complaint_id
    emp_to_resolve = payload.resolved_by_employee_id

    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id):
            real_item_id = m.get("id") or complaint_id
            old_status = m.get("status")
            m["status"] = new_status
            m["updated_at"] = now_str
            if payload.notes:
                m["resolution_notes"] = payload.notes
            if payload.resolution_proof_url:
                m["resolution_proof_url"] = payload.resolution_proof_url
            if new_status == "resolved":
                m["resolved_at"] = now_str
                if not emp_to_resolve:
                    emp_to_resolve = m.get("assigned_employee_id")
                # Trigger math resolution update if transitioning to resolved
                if old_status != "resolved" and emp_to_resolve:
                    record_employee_resolution(emp_to_resolve, supabase)
            updated_record = m
            break

    if updated_record:
        _save_all_local_complaints(_MEMORY_COMPLAINTS)

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
            try:
                res = supabase.table("complaints").update(update_body).eq("id", real_item_id).execute()
            except Exception:
                # Fallback to standard columns if optional columns not yet migrated in remote schema cache
                res = supabase.table("complaints").update({"status": new_status, "updated_at": now_str}).eq("id", real_item_id).execute()

            if res.data and len(res.data) > 0:
                item = res.data[0]
                cat = item.get("category", "others")
                dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                item["department"] = dept_info["name"]
                item["department_code"] = dept_info["code"]
                if updated_record:
                    # Enrich with local resolution proof and notes
                    item["resolution_notes"] = updated_record.get("resolution_notes")
                    item["resolution_proof_url"] = updated_record.get("resolution_proof_url")
                    if not item.get("citizen_email"):
                        item["citizen_email"] = updated_record.get("citizen_email")
                final_result = item
        except Exception as e:
            print(f"Supabase complaint status update note: {e}")

    if not final_result and updated_record:
        final_result = updated_record

    if not final_result:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Automated Grievance Resolution Email Notice
    if new_status == "resolved":
        try:
            send_complaint_resolution(final_result)
        except Exception as res_err:
            print(f"Resolution notification dispatch note: {res_err}")

    return final_result


@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: str,
    payload: ComplaintAssignRequest,
    current_user: dict = Depends(get_optional_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Assigns a complaint to an employee (EMP-101 to EMP-140).
    Updates complaint status to 'in_progress' and automatically updates employee workload math.
    """
    now_str = datetime.utcnow().isoformat() + "Z"

    # Automatically increment employee assigned & pending counts
    increment_employee_workload(payload.employee_id, supabase)

    # Update in memory
    updated_record = None
    real_item_id = complaint_id
    for m in _MEMORY_COMPLAINTS:
        if _matches_complaint_id(m.get("id"), complaint_id):
            real_item_id = m.get("id") or complaint_id
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

    # Update in Supabase
    if supabase is not None:
        try:
            update_body = {
                "assigned_employee_id": payload.employee_id,
                "status": "in_progress",
                "updated_at": now_str
            }
            if payload.assigned_team:
                update_body["assigned_team"] = payload.assigned_team
            res = supabase.table("complaints").update(update_body).eq("id", real_item_id).execute()
            if res.data and len(res.data) > 0:
                item = res.data[0]
                cat = item.get("category", "others")
                dept_info = DEPARTMENTS.get(cat, DEPARTMENTS['others'])
                item["department"] = dept_info["name"]
                item["department_code"] = dept_info["code"]
                return item
        except Exception as e:
            print(f"Supabase complaint assignment note: {e}")

    if updated_record:
        return updated_record

    raise HTTPException(status_code=404, detail="Complaint not found")


@router.post("/{complaint_id}/upvote")
def upvote_complaint(
    complaint_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Increments citizen endorsement / upvote count for a complaint.
    """
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
