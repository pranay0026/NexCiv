"""
NEX-CIV Dynamic Multi-Complaint Prioritization & Timeline AI Engine
====================================================================
Implements a structured, relative municipal grievance prioritization model.

Core Principles:
1. Multi-Complaint Relative Queue Ranking:
   Whenever a new or existing complaint is processed at any lifecycle step,
   it is dynamically evaluated against ALL active/pending complaints in the department.
2. Aging & SLA Depletion Dynamics:
   Complaints that arrived earlier naturally age; as remaining statutory hours deplete,
   their relative priority escalates so older grievances are not starved.
3. Sensitive Zone & Hazard Multipliers:
   Hospitals, schools, highways, transit hubs amplify the priority score.
4. Emergency Override Engine:
   Life-safety hazards (live wire, sinkhole, missing manhole, toxic water, flash flood)
   instantly lock the priority to Critical (95+ score) and place it at Rank #1.
5. Action Timeline Synthesis:
   Forms a deterministic, milestone-driven execution timeline based on the
   complaint's rank in the departmental queue, workforce capacity, and statutory SLA.
6. Step-by-Step Priority Auditing:
   Maintains a chronological priority trajectory at every step:
   (Submission -> Triage -> Allocation -> Investigation -> Remediation -> Escalation/Reopen).
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import uuid

# Department definitions & baseline throughput rates (hours per complaint)
DEPARTMENT_THROUGHPUT_HOURS = {
    "road": 36.0,
    "water_supply": 18.0,
    "drainage": 24.0,
    "street_lights": 12.0,
    "sanitation": 8.0,
    "others": 24.0
}

# Sensitive Zone Keywords for Spatial Vulnerability
ZONE_KEYWORDS = {
    "hospital": [
        "hospital", "clinic", "dispensary", "emergency", "icu", "trauma", "kgh", "ggh", "ruia",
        "svims", "apollo", "care hospital", "phc", "chc", "ఆసుపత్రి", "వైద్యశాల", "ఎమర్జెన్సీ"
    ],
    "school": [
        "school", "college", "university", "campus", "playground", "vidyalaya", "zp high school",
        "mpp school", "kindergarten", "academy", "పాఠశాల", "బడి", "కళాశాల"
    ],
    "highway": [
        "highway", "expressway", "flyover", "arterial", "nh-16", "nh-65", "nh-44", "bypass",
        "junction", "bridge", "benz circle", "kanaka durga", "రహదారి", "ఫ్లైఓవర్"
    ],
    "transit_hub": [
        "bus stand", "railway", "rtc", "pnbs", "metro station", "airport", "depot", "బస్ స్టాండ్", "రైల్వే"
    ]
}

# Emergency Hazards
EMERGENCY_SIGNATURES = [
    {
        "hazard_id": "EMG-01-ELEC",
        "label": "Live Electrical Wire / High Voltage Spark",
        "keywords": ["live wire", "exposed wire", "sparking", "electric pole short", "కరెంట్ వైర్లు", "విద్యుత్ ప్రమాదం"],
        "defect_types": ["exposed_electrical_wires", "fallen_pole"]
    },
    {
        "hazard_id": "EMG-02-ROAD",
        "label": "Structural Road Collapse / Major Sinkhole",
        "keywords": ["cave-in", "sinkhole", "road collapsed", "bridge collapse", "రోడ్డు కుంగిపోయింది"],
        "defect_types": ["road_cave_in", "sinkhole"]
    },
    {
        "hazard_id": "EMG-03-MANHOLE",
        "label": "Uncovered Open Manhole in Public Corridor",
        "keywords": ["open manhole", "manhole cover missing", "uncovered manhole", "మ్యాన్‌హోల్ మూత లేదు"],
        "defect_types": ["open_manhole"]
    },
    {
        "hazard_id": "EMG-04-WATER",
        "label": "Toxic / Contaminated Drinking Water Outbreak",
        "keywords": ["contaminated water", "sewage in drinking water", "yellow water", "foul smell in tap", "కలుషిత నీరు", "వాంతులు"],
        "defect_types": ["water_contamination", "pipeline_burst"]
    },
    {
        "hazard_id": "EMG-05-FLOOD",
        "label": "Flash Flood Inundation Submerging Habitations",
        "keywords": ["flash flood", "water entering houses", "drain overflowing into houses", "severe flooding", "ముంపు ప్రమాదం"],
        "defect_types": ["flood_inundation", "main_drain_clogged"]
    }
]


def _parse_iso_datetime(dt_str: Optional[str]) -> datetime:
    """Safely parses ISO timestamp into datetime object."""
    if not dt_str:
        return datetime.utcnow()
    try:
        clean_str = dt_str.replace("Z", "+00:00")
        if "+" in clean_str:
            base, tz = clean_str.split("+", 1)
            return datetime.fromisoformat(base)
        return datetime.fromisoformat(clean_str)
    except Exception:
        return datetime.utcnow()


class DynamicDepartmentQueuePriorityModel:
    """
    AI Prioritization & Dynamic Queue Scheduling Model.
    Calculates intrinsic priority, compares against department queue, and synthesizes
    actionable lifecycle timelines.
    """

    @classmethod
    def evaluate_intrinsic_features(cls, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts intrinsic priority features from complaint text, defect type, image score,
        and geospatial sensitivity.
        """
        title = complaint.get("title") or ""
        desc = complaint.get("description") or ""
        full_text = f"{title} {desc} {complaint.get('landmark', '')}".lower()
        defect = (complaint.get("defect_type") or "").lower()
        category = (complaint.get("category") or "others").lower()

        # 1. Emergency Hazard Detection
        is_emergency = False
        emergency_reason = None
        for emg in EMERGENCY_SIGNATURES:
            if defect in emg["defect_types"] or any(k in full_text for k in emg["keywords"]):
                is_emergency = True
                emergency_reason = emg["label"]
                break

        # 2. Zone Sensitivity Multiplier
        zone_type = "residential"
        zone_multiplier = 1.0
        if any(k in full_text for k in ZONE_KEYWORDS["hospital"]):
            zone_type = "hospital"
            zone_multiplier = 1.45
        elif any(k in full_text for k in ZONE_KEYWORDS["highway"]):
            zone_type = "highway"
            zone_multiplier = 1.35
        elif any(k in full_text for k in ZONE_KEYWORDS["school"]):
            zone_type = "school"
            zone_multiplier = 1.25
        elif any(k in full_text for k in ZONE_KEYWORDS["transit_hub"]):
            zone_type = "transit_hub"
            zone_multiplier = 1.20

        # 3. Base Severity Score by Category & Defect
        base_severity = 50.0
        if category in ["water_supply", "drainage"]:
            base_severity = 62.0
        elif category in ["road"]:
            base_severity = 58.0
        elif category in ["street_lights"]:
            base_severity = 45.0

        if defect in ["open_manhole", "exposed_electrical_wires", "road_cave_in", "water_contamination"]:
            base_severity = 88.0
        elif defect in ["pothole_cluster", "drain_overflow", "low_voltage_blackout"]:
            base_severity = 68.0

        # 4. Computer Vision Image Damage Score
        visual_score = float(complaint.get("visual_score") or 0.0)
        has_image = bool(complaint.get("image_url") or (complaint.get("images") and len(complaint.get("images")) > 0))

        # 5. Social & Community Demand Factor
        upvotes = int(complaint.get("upvote_count") or 1)
        duplicates = int(complaint.get("duplicate_count") or 0)
        reopened = int(complaint.get("reopened_count") or 0)
        social_weight = min(25.0, (upvotes * 3.5) + (duplicates * 7.0) + (reopened * 12.0))

        # Intrinsic Raw Score
        raw_intrinsic = (
            (base_severity * 0.40) +
            ((visual_score if has_image else base_severity) * 0.25) +
            (social_weight * 0.20) +
            (15.0 if has_image else 0.0)
        )
        scaled_intrinsic = min(100.0, raw_intrinsic * zone_multiplier)

        if is_emergency:
            scaled_intrinsic = max(96.0, scaled_intrinsic)

        return {
            "is_emergency": is_emergency,
            "emergency_reason": emergency_reason,
            "zone_type": zone_type,
            "zone_multiplier": zone_multiplier,
            "base_severity": round(base_severity, 1),
            "visual_score": round(visual_score, 1),
            "social_weight": round(social_weight, 1),
            "intrinsic_score": round(scaled_intrinsic, 1)
        }

    @classmethod
    def calculate_relative_queue_priority(
        cls,
        target_complaint: Dict[str, Any],
        all_complaints: List[Dict[str, Any]],
        current_step: str = "citizen_submission",
        step_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates the dynamic priority of target_complaint by evaluating it against
        all active/pending complaints in the same department and municipality.
        """
        target_id = target_complaint.get("id") or target_complaint.get("rawId")
        dept = (target_complaint.get("department") or target_complaint.get("category") or "road").lower()
        muni = (target_complaint.get("municipal_corporation") or "ELR").upper()
        now = datetime.utcnow()

        # Filter active complaints in this department & municipality
        active_statuses = {"pending", "new", "under review", "in_progress", "in progress", "awaiting_verification", "escalated"}
        dept_complaints: List[Dict[str, Any]] = []

        for c in all_complaints:
            c_dept = (c.get("department") or c.get("category") or "").lower()
            c_muni = (c.get("municipal_corporation") or "ELR").upper()
            c_status = (c.get("status") or "pending").lower()

            if (c_dept == dept or (dept in c_dept) or (c_dept in dept)) and c_muni == muni and c_status in active_statuses:
                dept_complaints.append(c)

        # Ensure target_complaint is in the list
        found_target = False
        for idx, c in enumerate(dept_complaints):
            if c.get("id") == target_id or (target_id and c.get("id", "").startswith(str(target_id)[:8])):
                dept_complaints[idx] = target_complaint
                found_target = True
                break
        if not found_target:
            dept_complaints.append(target_complaint)

        # Target Complaint Spatial Cluster Density
        target_ward = str(target_complaint.get("ward") or "")
        cluster_count = sum(1 for c in dept_complaints if target_ward and str(c.get("ward")) == target_ward)
        cluster_bonus = min(20.0, max(0.0, (cluster_count - 1) * 5.0))

        # Evaluate Each Complaint's Dynamic Unified Score
        scored_queue = []
        for c in dept_complaints:
            c_id = c.get("id") or str(uuid.uuid4())
            c_created = _parse_iso_datetime(c.get("created_at"))
            elapsed_hours = max(0.1, (now - c_created).total_seconds() / 3600.0)

            # Statutory SLA baseline hours
            sla_days = float(c.get("prescribed_timeline_days") or 3.0)
            total_sla_hours = max(12.0, sla_days * 24.0)

            # Aging Urgency: Older complaints gain dynamic urgency as SLA depletes
            depletion_ratio = elapsed_hours / total_sla_hours
            if depletion_ratio >= 1.0:
                aging_urgency = 35.0 + min(15.0, (depletion_ratio - 1.0) * 10.0)  # Overdue escalation
                is_overdue = True
            else:
                aging_urgency = depletion_ratio * 30.0
                is_overdue = False

            # Intrinsic Score
            feat = cls.evaluate_intrinsic_features(c)
            intrinsic = feat["intrinsic_score"]

            # Step Specific Modifiers
            step_boost = 0.0
            c_escalation = int(c.get("escalation_level") or 1)
            if c_escalation == 2:
                step_boost += 15.0
            elif c_escalation >= 3:
                step_boost += 30.0

            if (c.get("reopened_count") or 0) > 0:
                step_boost += 18.0

            # Dynamic Unified Score
            unified_score = (
                (intrinsic * 0.55) +
                (aging_urgency * 0.25) +
                (cluster_bonus * 0.10) +
                (step_boost * 0.10)
            )

            if feat["is_emergency"]:
                unified_score = max(95.0, unified_score)

            unified_score = round(max(5.0, min(100.0, unified_score)), 2)

            # Assign Priority Label
            if unified_score >= 82.0 or feat["is_emergency"]:
                tier = "Critical"
            elif unified_score >= 65.0:
                tier = "High"
            elif unified_score >= 45.0:
                tier = "Medium"
            else:
                tier = "Low"

            scored_queue.append({
                "complaint_id": c_id,
                "title": c.get("title", ""),
                "dynamic_priority_score": unified_score,
                "priority_tier": tier,
                "is_emergency": feat["is_emergency"],
                "emergency_reason": feat["emergency_reason"],
                "aging_urgency": round(aging_urgency, 1),
                "elapsed_hours": round(elapsed_hours, 1),
                "is_overdue": is_overdue,
                "zone_type": feat["zone_type"],
                "ward": c.get("ward"),
                "status": c.get("status", "pending"),
                "record": c
            })

        # Sort entire department queue in descending order of priority
        # Emergencies and highest scores come first
        scored_queue.sort(
            key=lambda x: (1 if x["is_emergency"] else 0, x["dynamic_priority_score"]),
            reverse=True
        )

        total_queue_count = len(scored_queue)
        target_rank = 1
        target_item = scored_queue[0]

        for rank_idx, item in enumerate(scored_queue, start=1):
            if item["complaint_id"] == target_id or (target_id and item["complaint_id"].startswith(str(target_id)[:8])):
                target_rank = rank_idx
                target_item = item
                break

        # Calculate Percentile in Department Queue
        if total_queue_count > 1:
            lower_count = total_queue_count - target_rank
            relative_percentile = round((lower_count / (total_queue_count - 1)) * 100.0, 1)
        else:
            relative_percentile = 100.0

        avg_dept_score = round(sum(i["dynamic_priority_score"] for i in scored_queue) / max(1, total_queue_count), 1)

        # Synthesize Detailed Action Timeline
        timeline_data = cls.synthesize_dynamic_timeline(
            target_item=target_item,
            target_rank=target_rank,
            total_queue_count=total_queue_count,
            current_step=current_step,
            step_notes=step_notes,
            department=dept
        )

        return {
            "complaint_id": target_id,
            "priority_score": target_item["dynamic_priority_score"],
            "priority_tier": target_item["priority_tier"],
            "is_emergency": target_item["is_emergency"],
            "emergency_reason": target_item["emergency_reason"],
            "department": dept,
            "municipality": muni,
            "queue_rank": target_rank,
            "queue_total": total_queue_count,
            "relative_percentile": relative_percentile,
            "department_average_priority": avg_dept_score,
            "active_cases_ahead_in_queue": max(0, target_rank - 1),
            "cluster_co_located_cases": cluster_count,
            "aging_urgency_score": target_item["aging_urgency"],
            "action_timeline": timeline_data,
            "explanation": (
                f"Ranked #{target_rank} of {total_queue_count} active {dept.replace('_', ' ').title()} complaints "
                f"({relative_percentile}th percentile). Unified Score: {target_item['dynamic_priority_score']}/100. "
                + (f"Statutory Emergency Override: {target_item['emergency_reason']}. " if target_item['is_emergency'] else "")
                + f"Aging Urgency: +{target_item['aging_urgency']} pts over {target_item['elapsed_hours']}h."
            )
        }

    @classmethod
    def synthesize_dynamic_timeline(
        cls,
        target_item: Dict[str, Any],
        target_rank: int,
        total_queue_count: int,
        current_step: str,
        step_notes: Optional[str],
        department: str
    ) -> Dict[str, Any]:
        """
        Synthesizes a realistic, statutory operational timeline based on queue rank,
        department throughput speed, and current lifecycle step.
        """
        now = datetime.utcnow()
        created_at = _parse_iso_datetime(target_item["record"].get("created_at"))
        throughput = DEPARTMENT_THROUGHPUT_HOURS.get(department, 24.0)

        # Estimated dispatch delay based on queue position
        # Critical cases dispatch within 0-2 hours; High within 4-8h; Lower ranks scheduled in sequence
        if target_item["is_emergency"] or target_item["priority_tier"] == "Critical":
            dispatch_hours = 0.5 + (target_rank - 1) * 0.75
            work_duration_hours = min(4.0, throughput * 0.25)
        elif target_item["priority_tier"] == "High":
            dispatch_hours = 2.0 + (target_rank - 1) * 1.5
            work_duration_hours = min(12.0, throughput * 0.4)
        else:
            dispatch_hours = 6.0 + (target_rank - 1) * 3.0
            work_duration_hours = throughput * 0.6

        scheduled_inspection_time = created_at + timedelta(hours=dispatch_hours)
        scheduled_remediation_start = scheduled_inspection_time + timedelta(hours=2.0)
        estimated_resolution_time = scheduled_remediation_start + timedelta(hours=work_duration_hours)

        # Statutory SLA deadline
        sla_days = float(target_item["record"].get("prescribed_timeline_days") or 3.0)
        statutory_deadline = created_at + timedelta(days=sla_days)

        phases = [
            {
                "phase_id": "phase_1_triage",
                "label": "Grievance Trigger & Multimodal AI Ingestion",
                "timestamp": created_at.isoformat() + "Z",
                "status": "completed",
                "priority_snapshot": target_item["dynamic_priority_score"],
                "details": f"Registered in {department.replace('_', ' ').title()} division. AI initial triage complete."
            },
            {
                "phase_id": "phase_2_queue",
                "label": "Department Multi-Complaint Queue Placement",
                "timestamp": (created_at + timedelta(minutes=10)).isoformat() + "Z",
                "status": "completed",
                "priority_snapshot": target_item["dynamic_priority_score"],
                "details": f"Evaluated against all {total_queue_count} active division cases. Assigned Queue Rank #{target_rank}."
            },
            {
                "phase_id": "phase_3_inspection",
                "label": "Cadre Field Inspection & Ground Assessment",
                "timestamp": scheduled_inspection_time.isoformat() + "Z",
                "status": "in_progress" if target_item["status"] in ["in_progress", "under review"] else "scheduled",
                "priority_snapshot": target_item["dynamic_priority_score"],
                "details": (
                    step_notes if (current_step == "field_investigation" and step_notes)
                    else f"Dispatched to cadre engineer. Target inspection slot: {scheduled_inspection_time.strftime('%b %d, %I:%M %p')}."
                )
            },
            {
                "phase_id": "phase_4_work_order",
                "label": "Remedial Civil / Maintenance Works Window",
                "timestamp": scheduled_remediation_start.isoformat() + "Z",
                "status": "in_progress" if target_item["status"] == "in_progress" else "pending",
                "priority_snapshot": target_item["dynamic_priority_score"],
                "details": f"Materials, machinery and labor mobilized. Estimated execution window: {round(work_duration_hours, 1)} hours."
            },
            {
                "phase_id": "phase_5_statutory_closure",
                "label": "Statutory Disposal & Citizen Verification",
                "timestamp": estimated_resolution_time.isoformat() + "Z",
                "deadline": statutory_deadline.isoformat() + "Z",
                "status": "completed" if target_item["status"] == "resolved" else "pending",
                "priority_snapshot": target_item["dynamic_priority_score"],
                "details": (
                    f"Targeted resolution by {estimated_resolution_time.strftime('%b %d, %I:%M %p')}. "
                    f"Statutory disposal ceiling under AP Act No. 6 of 2018: {statutory_deadline.strftime('%b %d, %Y')}."
                )
            }
        ]

        return {
            "scheduled_inspection_time": scheduled_inspection_time.isoformat() + "Z",
            "scheduled_remediation_start": scheduled_remediation_start.isoformat() + "Z",
            "estimated_resolution_time": estimated_resolution_time.isoformat() + "Z",
            "statutory_deadline": statutory_deadline.isoformat() + "Z",
            "queue_position_summary": f"Rank #{target_rank} of {total_queue_count} in {department.replace('_', ' ').title()}",
            "phases": phases
        }


# Singleton Model Instance
queue_priority_model = DynamicDepartmentQueuePriorityModel()


def evaluate_complaint_and_update_department_queue(
    complaint: Dict[str, Any],
    all_complaints: Optional[List[Dict[str, Any]]] = None,
    current_step: str = "citizen_submission",
    step_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for calculating dynamic multi-complaint priority and updating
    the complaint's execution timeline at any lifecycle step.
    """
    if all_complaints is None:
        try:
            from data_manager import _read_table
            all_complaints = _read_table("complaints")
        except Exception:
            all_complaints = []

    res = queue_priority_model.calculate_relative_queue_priority(
        target_complaint=complaint,
        all_complaints=all_complaints,
        current_step=current_step,
        step_notes=step_notes
    )

    # Attach dynamic metrics directly into the complaint record
    complaint["priority"] = res["priority_tier"]
    complaint["priority_score"] = res["priority_score"]
    complaint["queue_rank"] = res["queue_rank"]
    complaint["queue_total"] = res["queue_total"]
    complaint["relative_percentile"] = res["relative_percentile"]
    complaint["priority_explanation"] = res["explanation"]
    complaint["is_emergency_override"] = res["is_emergency"]
    complaint["action_timeline"] = res["action_timeline"]
    complaint["estimated_resolution_time"] = res["action_timeline"]["estimated_resolution_time"]

    # Append to chronological priority trajectory
    trajectory = complaint.get("priority_trajectory") or []
    trajectory.append({
        "step": current_step,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "priority_score": res["priority_score"],
        "priority_tier": res["priority_tier"],
        "queue_rank": res["queue_rank"],
        "queue_total": res["queue_total"],
        "step_notes": step_notes or res["explanation"]
    })
    complaint["priority_trajectory"] = trajectory

    return res
