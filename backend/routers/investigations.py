"""
NEX-CIV Investigations, Audit Trail & Citizen Accountability Router
Implements:
- Structured Employee Investigation & Action-Taken Reports
- Immutable Activity Logs / Audit Trail
- Citizen Feedback & Reopen Requests (with auditable event creation)
- Multi-Level Administrative Escalations
- Statutory Appeals (AP Act No. 6 of 2018 Sections 10 & 11)
- Official Acknowledgement Receipt Generation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime

from auth import get_optional_current_user
from schemas import (
    InvestigationCreate, InvestigationResponse,
    CitizenFeedbackCreate, ReopenComplaintRequest,
    EscalationRequest, AppealRequest, AcknowledgementReceipt
)
from data_manager import (
    save_investigation, get_investigations_by_complaint,
    record_activity_log, get_complaint_activity_logs,
    save_citizen_feedback, get_feedback_by_complaint,
    save_escalation, get_escalations_by_complaint,
    save_appeal, get_appeals_by_complaint,
    _read_table, _write_table, save_complaint_isolated
)

router = APIRouter(prefix="/api/grievance", tags=["investigations_and_governance"])


@router.post("/investigations", response_model=Dict[str, Any])
def record_investigation(
    payload: InvestigationCreate,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Submits a structured employee field investigation & action-taken report.
    Mandatory fields: investigation performed, findings, action taken, resolution status.
    """
    emp_id = payload.employee_id or current_user.get("id") or "EMP-101"
    emp_name = payload.employee_name or current_user.get("name") or "Municipal Engineer"

    inv_dict = payload.dict()
    inv_dict["employee_id"] = emp_id
    inv_dict["employee_name"] = emp_name

    saved = save_investigation(inv_dict)

    # Update complaint status and re-evaluate dynamic queue priority
    complaints = _read_table("complaints")
    for c in complaints:
        if c.get("id") == payload.complaint_id:
            if payload.is_resolved:
                c["status"] = "resolved"
                c["action_taken"] = payload.action_taken
                c["resolution_summary"] = payload.findings
                c["resolution_notes"] = payload.action_taken
                c["resolved_at"] = datetime.utcnow().isoformat() + "Z"
                inv_step = "field_investigation_resolved"
            else:
                c["status"] = "in_progress"
                c["action_taken"] = payload.action_taken
                if payload.inability_reason:
                    c["rejection_reason"] = payload.inability_reason
                inv_step = "field_investigation_in_progress"

            # Dynamic Queue Prioritization & Timeline Refresh
            try:
                from dynamic_priority_timeline_engine import evaluate_complaint_and_update_department_queue
                evaluate_complaint_and_update_department_queue(
                    complaint=c,
                    all_complaints=complaints,
                    current_step=inv_step,
                    step_notes=f"Ground investigation filed by {emp_name}. Findings: {payload.findings[:60]}"
                )
            except Exception as e_prio:
                print(f"Dynamic priority investigation update note: {e_prio}")

            save_complaint_isolated(c)
            break
    _write_table("complaints", complaints)

    return saved


@router.get("/investigations/{complaint_id}")
def get_complaint_investigations(complaint_id: str):
    """
    Returns all investigation reports associated with a grievance.
    """
    return get_investigations_by_complaint(complaint_id)


@router.get("/timeline/{complaint_id}")
def get_complaint_timeline(complaint_id: str):
    """
    Returns the immutable chronological activity audit trail for a grievance.
    Provides complete transparency into status transitions, employee assignments, and notes.
    """
    return get_complaint_activity_logs(complaint_id)


@router.post("/feedback")
def submit_citizen_feedback(
    payload: CitizenFeedbackCreate,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Records citizen feedback on resolution and satisfaction rating.
    """
    name = payload.citizen_name or current_user.get("name") or "Citizen"
    fb_dict = payload.dict()
    fb_dict["citizen_name"] = name
    return save_citizen_feedback(fb_dict)


@router.post("/reopen")
def reopen_complaint(
    payload: ReopenComplaintRequest,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Allows a citizen to request reopening of a closed/resolved grievance with an explanation.
    Creates an immutable audit event without erasing prior resolution history.
    """
    complaints = _read_table("complaints")
    matched = None
    now_str = datetime.utcnow().isoformat() + "Z"

    for c in complaints:
        if c.get("id") == payload.complaint_id:
            c["status"] = "pending"
            c["reopened_count"] = (c.get("reopened_count") or 0) + 1
            c["reopened_at"] = now_str
            c["reopen_reason"] = payload.reopen_reason
            c["updated_at"] = now_str

            # Re-evaluate dynamic queue priority upon reopening
            try:
                from dynamic_priority_timeline_engine import evaluate_complaint_and_update_department_queue
                evaluate_complaint_and_update_department_queue(
                    complaint=c,
                    all_complaints=complaints,
                    current_step="citizen_reopen",
                    step_notes=f"Reopened by citizen: {payload.reopen_reason}"
                )
            except Exception as e_reopen:
                print(f"Reopen dynamic priority update note: {e_reopen}")

            save_complaint_isolated(c)
            matched = c
            break

    if not matched:
        raise HTTPException(status_code=404, detail="Complaint not found")

    _write_table("complaints", complaints)

    # Record immutable audit event
    actor_name = payload.citizen_name or current_user.get("name") or "Citizen"
    record_activity_log(
        complaint_id=payload.complaint_id,
        actor_role="citizen",
        actor_name=actor_name,
        action="Grievance Reopened & Priority Re-evaluated",
        previous_status="resolved",
        new_status="pending",
        comments=(
            f"Reopened: {payload.reopen_reason}. "
            f"Re-evaluated Priority: {matched.get('priority')} ({matched.get('priority_score')}/100). "
            f"Queue Rank #{matched.get('queue_rank', 1)} of {matched.get('queue_total', 1)}."
        ),
        metadata={
            "evidence_url": payload.evidence_url,
            "priority_score": matched.get("priority_score"),
            "queue_rank": matched.get("queue_rank")
        }
    )

    return {"message": "Grievance successfully reopened for investigation", "complaint": matched}


@router.post("/escalate")
def escalate_complaint(
    payload: EscalationRequest,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Triggers administrative escalation (Level 1 Assigned Officer -> Level 2 Supervising Officer
    -> Level 3 Department Head -> Level 4 Designated Higher Authority).
    """
    complaints = _read_table("complaints")
    matched = None
    for c in complaints:
        if c.get("id") == payload.complaint_id:
            c["escalation_level"] = payload.escalation_level
            c["updated_at"] = datetime.utcnow().isoformat() + "Z"

            # Dynamic Queue Prioritization & Timeline Shift on Escalation
            try:
                from dynamic_priority_timeline_engine import evaluate_complaint_and_update_department_queue
                evaluate_complaint_and_update_department_queue(
                    complaint=c,
                    all_complaints=complaints,
                    current_step=f"statutory_escalation_tier_{payload.escalation_level}",
                    step_notes=f"Administrative escalation to Level {payload.escalation_level}: {payload.reason}"
                )
            except Exception as e_esc:
                print(f"Escalation dynamic priority update note: {e_esc}")

            save_complaint_isolated(c)
            matched = c
            break

    if not matched:
        raise HTTPException(status_code=404, detail="Complaint not found")

    _write_table("complaints", complaints)

    esc_dict = payload.dict()
    esc_dict["escalated_from_id"] = current_user.get("id") or "system"
    saved = save_escalation(esc_dict)

    record_activity_log(
        complaint_id=payload.complaint_id,
        actor_role="administration",
        actor_name=current_user.get("name") or "Administrative Authority",
        action=f"Escalation Level {payload.escalation_level} Dispatched",
        comments=(
            f"Escalated to Tier {payload.escalation_level}: {payload.reason}. "
            f"Dynamic Priority Escalated: {matched.get('priority')} ({matched.get('priority_score')}/100), "
            f"Queue Rank #{matched.get('queue_rank', 1)} of {matched.get('queue_total', 1)}."
        ),
        metadata={
            "escalation_level": payload.escalation_level,
            "priority_score": matched.get("priority_score"),
            "queue_rank": matched.get("queue_rank")
        }
    )

    return {"message": "Administrative escalation dispatched", "escalation": saved}


@router.post("/appeal")
def file_statutory_appeal(
    payload: AppealRequest,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Files a formal statutory appeal under Section 10 or Section 11 of the
    Andhra Pradesh Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018).
    """
    complaints = _read_table("complaints")
    for c in complaints:
        if c.get("id") == payload.complaint_id:
            c["appealed"] = True
            c["updated_at"] = datetime.utcnow().isoformat() + "Z"
            save_complaint_isolated(c)
            break
    _write_table("complaints", complaints)

    appeal_dict = payload.dict()
    saved = save_appeal(appeal_dict)
    return {"message": "Statutory appeal successfully filed under Act No. 6 of 2018", "appeal": saved}


@router.get("/acknowledgement/{complaint_id}", response_model=AcknowledgementReceipt)
def get_acknowledgement_receipt(complaint_id: str):
    """
    Generates downloadable official grievance acknowledgement receipt compliant with
    AP Public Services Delivery Guarantee Act Section 3 & Departmental Citizen Charters.
    """
    complaints = _read_table("complaints")
    c = None
    for item in complaints:
        if item.get("id") == complaint_id:
            c = item
            break

    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    ref_num = c.get("grievance_ref_number") or f"AP-NXC-{c.get('id')[:6].upper()}"
    wf_type = c.get("workflow_type") or "ordinary_grievance"

    legal_src = c.get("legal_source") or (
        "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)"
        if wf_type == "notified_service"
        else "AP Municipal Citizen Charter & PGRS Guidelines"
    )

    return AcknowledgementReceipt(
        grievance_ref_number=ref_num,
        complaint_id=c.get("id"),
        title=c.get("title", ""),
        citizen_name=c.get("citizen_name") or "Citizen",
        citizen_email=c.get("citizen_email"),
        citizen_phone=c.get("citizen_phone"),
        submission_time=c.get("created_at") or datetime.utcnow().isoformat() + "Z",
        department=c.get("department") or "Municipal Services",
        department_code=c.get("department_code") or "others",
        category=c.get("category") or "others",
        workflow_type=wf_type,
        legal_source=legal_src,
        go_reference=c.get("go_reference") or "Standing Order 118",
        designated_officer=c.get("designated_officer") or "Municipal Engineer / Designated Officer",
        expected_resolution_date=c.get("expected_resolution_date") or c.get("deadline_formatted") or "Under Administrative Review",
        timeline_calculation_method=c.get("sla_calculation_method") or "working_days",
        current_status=c.get("status") or "pending",
        first_appellate_authority=c.get("first_appellate_authority") or "Executive Engineer / Superintending Engineer",
        appeal_deadline_days=30 if wf_type == "notified_service" else 15,
        compensation_applicable=True if wf_type == "notified_service" else False
    )
