from pydantic import BaseModel
from typing import Optional, Any, Dict, List

class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    department: Optional[str] = None
    department_code: Optional[str] = None
    municipal_corporation: Optional[str] = "GVMC"  # GVMC, VMC, GMC, TMC, etc. (17 AP Corporations)
    ward: Optional[str] = None
    landmark: Optional[str] = None
    confidence: Optional[float] = None
    priority: Optional[str] = None
    priority_score: Optional[float] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    images: Optional[List[str]] = None  # Multiple photos support
    zone_type: Optional[str] = None
    vulnerability_multiplier: Optional[float] = None
    municipal_sla: Optional[str] = None
    assigned_team: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    citizen_name: Optional[str] = None
    citizen_email: Optional[str] = None
    citizen_phone: Optional[str] = None
    image_hash: Optional[str] = None
    defect_type: Optional[str] = None
    visual_score: Optional[float] = None

class ComplaintResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    description: str
    category: str
    status: str
    department: Optional[str] = None
    department_code: Optional[str] = None
    municipal_corporation: Optional[str] = "GVMC"
    ward: Optional[str] = None
    landmark: Optional[str] = None
    confidence: Optional[float] = None
    priority: Optional[str] = 'Medium'
    priority_score: Optional[float] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None  # Multiple photos support
    zone_type: Optional[str] = None
    vulnerability_multiplier: Optional[float] = None
    municipal_sla: Optional[str] = None
    assigned_team: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    citizen_name: Optional[str] = None
    citizen_email: Optional[str] = None
    citizen_phone: Optional[str] = None
    is_duplicate: Optional[bool] = False
    master_complaint_id: Optional[str] = None
    duplicate_count: Optional[int] = 0
    upvote_count: Optional[int] = 1
    image_hash: Optional[str] = None
    defect_type: Optional[str] = None
    visual_score: Optional[float] = None
    cluster_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolution_proof_url: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: str

class ImageVerificationRequest(BaseModel):
    image_data: str

class ImageVerificationResponse(BaseModel):
    is_valid_civic_image: bool
    defect_type: str
    visual_severity_score: float
    visual_priority_tier: str
    visual_confidence: float
    image_hash: str
    authenticity_passed: bool
    rejection_reason: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class DuplicateCheckRequest(BaseModel):
    title: Optional[str] = ""
    description: str
    category: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    image_data: Optional[str] = None

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    master_complaint_id: Optional[str] = None
    master_title: Optional[str] = None
    similarity_score: Optional[float] = None
    distance_meters: Optional[float] = None
    reasons: Optional[List[str]] = None
    upvote_count: Optional[int] = 1

class ClassifyRequest(BaseModel):
    text: Optional[str] = ""
    image_data: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class ClassifyResponse(BaseModel):
    wing: str
    wing_label: str
    wing_confidence: float
    priority: str
    priority_confidence: float
    priority_score: Optional[float] = None
    category: str
    confidence: float
    department: str
    department_code: str
    department_head: Optional[str] = None
    all_probabilities: Optional[Dict[str, float]] = None
    top_keywords: Optional[List[str]] = None
    image_analysis: Optional[Dict[str, Any]] = None
    location_info: Optional[Dict[str, Any]] = None
    municipal_sla: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: str  # 'pending', 'in_progress', 'resolved'
    notes: Optional[str] = None
    resolution_proof_url: Optional[str] = None
    resolved_by_employee_id: Optional[str] = None

class ComplaintAssignRequest(BaseModel):
    employee_id: str
    assigned_team: Optional[str] = None
    notes: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str
    employee_code: str
    name: str
    initials: Optional[str] = None
    email: str
    phone: Optional[str] = None
    department: str
    department_name: str
    designation: str
    zone: str
    municipality_code: Optional[str] = 'ELR'
    status: Optional[str] = 'active'
    assigned_count: Optional[int] = 0
    completed_count: Optional[int] = 0
    pending_count: Optional[int] = 0
    overdue_count: Optional[int] = 0
    avg_resolution_days: Optional[float] = 2.4
    completion_rate: Optional[float] = 80.0
    rating: Optional[float] = 4.5
    performance: Optional[str] = 'On track'
    skills: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EmployeeCreate(BaseModel):
    employee_code: Optional[str] = None
    name: str
    email: Optional[str] = None
    department: str
    department_name: Optional[str] = None
    designation: Optional[str] = 'Municipal Engineer'
    zone: Optional[str] = 'Central Zone'
    phone: Optional[str] = None
    initials: Optional[str] = None
    skills: Optional[str] = None
    municipality_code: Optional[str] = 'ELR'
    password: Optional[str] = 'pass123'

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    zone: Optional[str] = None
    status: Optional[str] = None
    assigned_count: Optional[int] = None
    completed_count: Optional[int] = None
    pending_count: Optional[int] = None
    overdue_count: Optional[int] = None
    avg_resolution_days: Optional[float] = None
    rating: Optional[float] = None

class DepartmentLoginRequest(BaseModel):
    corporation_id: str  # e.g., 'GVMC', 'VMC', 'GMC', 'TMC'
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = 'citizen'
    department: Optional[str] = None
    corporation: Optional[str] = None
