"""
NEX-CIV Legal Compliance & Regulatory Monitoring Router
Implements endpoints for:
- AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)
- Departmental Citizen Charters & PGRS compliance tracking
- Versioned Legal Rules Management
- Monthly Department Compliance Reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from auth import get_optional_current_user
from database import get_supabase
from schemas import LegalRuleCreate, LegalRuleUpdate
from data_manager import (
    get_all_legal_rules, get_legal_rule_by_id, update_legal_rule,
    get_rule_versions, _read_table, _write_table
)

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/rules")
def list_legal_rules(
    department_code: Optional[str] = Query(None),
    workflow_type: Optional[str] = Query(None)
):
    """
    Returns all configurable legal service rules.
    Supports filtering by department and workflow type (notified_service vs ordinary_grievance).
    """
    rules = get_all_legal_rules()
    filtered = []
    for r in rules:
        if department_code and department_code.lower() != "all":
            if r.get("department_code") != department_code.lower():
                continue
        if workflow_type and workflow_type.lower() != "all":
            if r.get("workflow_type") != workflow_type.lower():
                continue
        filtered.append(r)
    return filtered


@router.post("/rules")
def create_legal_rule(
    payload: LegalRuleCreate,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Creates a new legal service rule for a department or service category.
    """
    rules = get_all_legal_rules()
    new_id = f"rule-{payload.department_code}-{str(uuid.uuid4())[:8]}"
    rule_dict = payload.dict()
    rule_dict["id"] = new_id
    rule_dict["version"] = 1
    rule_dict["is_active"] = True
    rule_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    rule_dict["updated_at"] = datetime.utcnow().isoformat() + "Z"

    rules.insert(0, rule_dict)
    _write_table("legal_service_rules", rules)
    return rule_dict


@router.put("/rules/{rule_id}")
def edit_legal_rule(
    rule_id: str,
    payload: LegalRuleUpdate,
    current_user: dict = Depends(get_optional_current_user)
):
    """
    Updates an existing legal service rule with version history tracking.
    Never silently changes deadlines for already-submitted grievances.
    """
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    actor_name = current_user.get("name") or "Department Head"
    try:
        updated = update_legal_rule(rule_id, update_data, updated_by=actor_name)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/rules/{rule_id}/versions")
def get_rule_version_history(rule_id: str):
    """
    Fetches the immutable version history of a legal service rule.
    """
    versions = get_rule_versions(rule_id)
    return versions


@router.get("/summary")
def get_compliance_summary(
    department_code: Optional[str] = Query(None),
    municipal_corporation: Optional[str] = Query(None)
):
    """
    Computes department-wide legal compliance metrics based on actual database records.
    Differentiates between Notified Services (Act 6 of 2018) and Ordinary Civic Grievances.
    """
    complaints = _read_table("complaints")

    # Filter
    filtered = []
    for c in complaints:
        if isinstance(department_code, str) and department_code.strip() and department_code.lower() != "all":
            c_dept = (c.get("department_code") or c.get("category") or "").lower()
            if c_dept != department_code.lower():
                continue
        if isinstance(municipal_corporation, str) and municipal_corporation.strip() and municipal_corporation.lower() != "all":
            c_corp = (c.get("municipal_corporation") or "").upper()
            if c_corp != municipal_corporation.upper():
                continue
        filtered.append(c)

    total = len(filtered)
    notified_count = 0
    ordinary_count = 0

    disposed_within_time = 0
    disposed_beyond_time = 0
    pending_within_time = 0
    pending_overdue = 0

    reopened_count = 0
    escalated_count = 0
    appeals_count = 0

    for c in filtered:
        wf = c.get("workflow_type") or "ordinary_grievance"
        if wf == "notified_service":
            notified_count += 1
        else:
            ordinary_count += 1

        is_overdue = c.get("sla_is_overdue", False)
        status = (c.get("status") or "pending").lower()

        if status == "resolved":
            if is_overdue:
                disposed_beyond_time += 1
            else:
                disposed_within_time += 1
        else:
            if is_overdue:
                pending_overdue += 1
            else:
                pending_within_time += 1

        if (c.get("reopened_count") or 0) > 0:
            reopened_count += 1
        if (c.get("escalation_level") or 1) > 1:
            escalated_count += 1
        if c.get("appealed", False):
            appeals_count += 1

    total_disposed = disposed_within_time + disposed_beyond_time
    statutory_compliance_rate = round((disposed_within_time / total_disposed * 100), 1) if total_disposed > 0 else 100.0

    return {
        "total_cases": total,
        "notified_services_count": notified_count,
        "ordinary_grievances_count": ordinary_count,
        "disposed_total": total_disposed,
        "disposed_within_stipulated_time": disposed_within_time,
        "disposed_beyond_stipulated_time": disposed_beyond_time,
        "pending_total": pending_within_time + pending_overdue,
        "pending_within_deadline": pending_within_time,
        "pending_overdue": pending_overdue,
        "statutory_compliance_rate": statutory_compliance_rate,
        "reopened_cases": reopened_count,
        "escalated_cases": escalated_count,
        "statutory_appeals_count": appeals_count,
        "applicable_legal_acts": [
            "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
            "AP Municipal Citizen Charters & PGRS Guidelines",
            "Digital Personal Data Protection Act, 2023"
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/monthly-report")
def get_monthly_compliance_report(
    department_code: Optional[str] = Query(None),
    municipal_corporation: Optional[str] = Query(None),
    month_year: Optional[str] = Query("Current Month")
):
    """
    Generates structured Monthly Statutory Compliance Report according to Section 13 of Act No. 6 of 2018.
    Suitable for executive review and export to CSV/PDF.
    """
    complaints = _read_table("complaints")
    rules = get_all_legal_rules()
    rules_map = {r.get("id"): r for r in rules}

    # Department and Corp breakdown
    category_summary = {}
    for c in complaints:
        if isinstance(department_code, str) and department_code.strip() and department_code.lower() != "all":
            c_dept = (c.get("department_code") or c.get("category") or "").lower()
            if c_dept != department_code.lower():
                continue
        if isinstance(municipal_corporation, str) and municipal_corporation.strip() and municipal_corporation.lower() != "all":
            c_corp = (c.get("municipal_corporation") or "").upper()
            if c_corp != municipal_corporation.upper():
                continue

        cat = c.get("category") or "others"
        if cat not in category_summary:
            category_summary[cat] = {
                "category": cat,
                "department": c.get("department") or "Municipal Services",
                "received": 0,
                "disposed_on_time": 0,
                "disposed_delayed": 0,
                "pending": 0,
                "overdue": 0,
                "reopened": 0,
                "statutory_appeals": 0,
                "delay_reasons": []
            }
        cs = category_summary[cat]
        cs["received"] += 1
        stat = (c.get("status") or "").lower()
        is_overdue = c.get("sla_is_overdue", False)

        if stat == "resolved":
            if is_overdue:
                cs["disposed_delayed"] += 1
            else:
                cs["disposed_on_time"] += 1
        else:
            cs["pending"] += 1
            if is_overdue:
                cs["overdue"] += 1

        if (c.get("reopened_count") or 0) > 0:
            cs["reopened"] += 1
        if c.get("appealed"):
            cs["statutory_appeals"] += 1

        if c.get("rejection_reason"):
            cs["delay_reasons"].append(c.get("rejection_reason"))

    report_rows = list(category_summary.values())

    return {
        "report_title": f"Andhra Pradesh Public Services Delivery Guarantee Compliance Report - {month_year}",
        "governing_statute": "Section 13, AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
        "reporting_period": month_year if isinstance(month_year, str) else "Current Month",
        "department_code": department_code if isinstance(department_code, str) else "All Departments",
        "municipal_corporation": municipal_corporation if isinstance(municipal_corporation, str) else "All Corporations",
        "summary_table": report_rows,
        "total_categories_covered": len(report_rows),
        "generated_timestamp": datetime.utcnow().isoformat() + "Z"
    }
