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
    workflow_type: Optional[str] = None  # 'notified_service' | 'ordinary_grievance' | 'specialized'


class ComplaintResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    grievance_ref_number: Optional[str] = None
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
    resolution_summary: Optional[str] = None
    action_taken: Optional[str] = None
    rejection_reason: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: str
    # Legal compliance & SLA extensions
    workflow_type: Optional[str] = "ordinary_grievance"
    legal_rule_id: Optional[str] = None
    legal_source: Optional[str] = None
    designated_officer: Optional[str] = None
    appellate_authority: Optional[str] = None
    expected_resolution_date: Optional[str] = None
    deadline_formatted: Optional[str] = None
    sla_remaining_hours: Optional[int] = None
    sla_is_overdue: Optional[bool] = False
    sla_overdue_hours: Optional[int] = 0
    escalation_level: Optional[int] = 1
    reopened_count: Optional[int] = 0
    reopened_at: Optional[str] = None
    appealed: Optional[bool] = False


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
    title: Optional[str] = None
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
    complaint_type: Optional[str] = None
    complaint_type_confidence: Optional[float] = None
    all_probabilities: Optional[Dict[str, float]] = None
    top_keywords: Optional[List[str]] = None
    image_analysis: Optional[Dict[str, Any]] = None
    location_info: Optional[Dict[str, Any]] = None
    municipal_sla: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: str  # 'pending', 'in_progress', 'resolved', 'rejected', 'under_investigation'
    notes: Optional[str] = None
    resolution_proof_url: Optional[str] = None
    action_taken: Optional[str] = None
    resolution_summary: Optional[str] = None
    rejection_reason: Optional[str] = None
    resolved_by_employee_id: Optional[str] = None


class ComplaintAssignRequest(BaseModel):
    employee_id: str
    assigned_team: Optional[str] = None
    reassignment_reason: Optional[str] = None
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
    reopened_count: Optional[int] = 0
    escalated_count: Optional[int] = 0
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


# ------------------------------------------------------------------------------
# LEGAL COMPLIANCE, SLA & INVESTIGATION SCHEMAS
# ------------------------------------------------------------------------------

class InvestigationCreate(BaseModel):
    complaint_id: str
    investigation_performed: str
    location_inspected: Optional[str] = None
    findings: str
    action_taken: str
    supporting_evidence_urls: Optional[List[str]] = []
    is_resolved: bool
    inability_reason: Optional[str] = None
    further_action_required: Optional[str] = None
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: str
    complaint_id: str
    employee_id: str
    employee_name: str
    investigation_performed: str
    location_inspected: Optional[str] = None
    findings: str
    action_taken: str
    supporting_evidence_urls: List[str] = []
    is_resolved: bool
    inability_reason: Optional[str] = None
    further_action_required: Optional[str] = None
    created_at: str


class ActivityLogResponse(BaseModel):
    id: str
    complaint_id: str
    actor_role: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    action: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    comments: Optional[str] = None
    created_at: str


class CitizenFeedbackCreate(BaseModel):
    complaint_id: str
    citizen_name: Optional[str] = None
    rating: int  # 1 to 5
    is_resolved_confirmed: bool
    comments: Optional[str] = None


class ReopenComplaintRequest(BaseModel):
    complaint_id: str
    reopen_reason: str
    evidence_url: Optional[str] = None
    citizen_name: Optional[str] = None


class EscalationRequest(BaseModel):
    complaint_id: str
    escalation_level: int  # 1: Assigned Officer, 2: Supervising Officer, 3: Dept Head, 4: Higher Authority
    reason: str
    escalated_to_title: str


class AppealRequest(BaseModel):
    complaint_id: str
    appeal_level: int  # 1 = First Appellate Authority, 2 = Second Appellate Authority
    appellant_name: str
    appellant_email: Optional[str] = None
    appeal_ground: str
    supporting_doc_urls: Optional[List[str]] = []


class LegalRuleCreate(BaseModel):
    department_code: str
    department_name: str
    service_key: str
    service_name: str
    workflow_type: str  # 'notified_service' | 'ordinary_grievance'
    legal_source: str
    go_reference: str
    prescribed_timeline_days: int
    calculation_method: str  # 'working_days' | 'calendar_days'
    designated_officer_title: str
    first_appellate_authority: str
    second_appellate_authority: str
    appeal_deadline_days: Optional[int] = 30
    compensation_applicable: Optional[bool] = False
    compensation_rate_per_day: Optional[int] = 0
    max_compensation: Optional[int] = 0
    description: Optional[str] = None


class LegalRuleUpdate(BaseModel):
    service_name: Optional[str] = None
    legal_source: Optional[str] = None
    go_reference: Optional[str] = None
    prescribed_timeline_days: Optional[int] = None
    calculation_method: Optional[str] = None
    designated_officer_title: Optional[str] = None
    first_appellate_authority: Optional[str] = None
    second_appellate_authority: Optional[str] = None
    appeal_deadline_days: Optional[int] = None
    compensation_applicable: Optional[bool] = None
    is_active: Optional[bool] = None
    change_reason: Optional[str] = "Administrative Revision"
    updated_by: Optional[str] = "Department Head"


class AcknowledgementReceipt(BaseModel):
    grievance_ref_number: str
    complaint_id: str
    title: str
    citizen_name: str
    citizen_email: Optional[str] = None
    citizen_phone: Optional[str] = None
    submission_time: str
    department: str
    department_code: str
    category: str
    workflow_type: str
    legal_source: str
    go_reference: Optional[str] = None
    designated_officer: str
    expected_resolution_date: str
    timeline_calculation_method: str
    current_status: str
    first_appellate_authority: str
    appeal_deadline_days: int
    compensation_applicable: bool
