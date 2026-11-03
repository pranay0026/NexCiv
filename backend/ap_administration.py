"""
NEX-CIV Andhra Pradesh Municipal Administration Structure & Cadre Registry
Compliant with:
- Andhra Pradesh Municipalities Act, 1965
- Andhra Pradesh Municipal Corporations Act, 1994
- G.O.Ms.No.217, MA&UD Department, dated 20-07-2019 (Ward Secretariat System)
- Andhra Pradesh Municipal Engineering Service Rules
- AP Municipal Cadre Recruitment Rules & CDMA Citizen Charter
"""

from typing import Dict, Any, List, Optional

# -----------------------------------------------------------------------------
# 1. MUNICIPAL DEPARTMENTS & FUNCTIONAL WINGS CONFIGURATION
# -----------------------------------------------------------------------------
AP_DEPARTMENTS_CONFIG: Dict[str, Dict[str, Any]] = {
    "engineering": {
        "id": "dept_engineering",
        "code": "engineering",
        "name": "Engineering Department",
        "head_designation": "Superintending Engineer (SE) / Executive Engineer (EE)",
        "legal_basis": "AP Municipal Corporations Act 1994, Sec. 132 & AP Municipal Engineering Service Rules",
        "functional_wings": {
            "road": {
                "id": "wing_roads",
                "code": "road",
                "name": "Roads and Pavements Wing",
                "categories": ["potholes", "damaged_roads", "footpath_damage", "road_obstruction", "road_cave_in"],
                "default_officer": "Assistant Executive Engineer (AEE - Roads)",
                "statutory_sla_days": 7,
                "calendar_type": "working_days"
            },
            "drainage": {
                "id": "wing_drainage",
                "code": "drainage",
                "name": "Stormwater Drains & Culverts Wing",
                "categories": ["blocked_drainage", "drainage_overflow", "open_manhole", "culvert_damage", "desilting"],
                "default_officer": "Assistant Executive Engineer (AEE - Drainage)",
                "statutory_sla_days": 3,
                "calendar_type": "working_days"
            },
            "water_supply": {
                "id": "wing_water_supply",
                "code": "water_supply",
                "name": "Water Supply and Distribution Wing",
                "categories": ["pipeline_leakage", "no_water_supply", "water_contamination", "low_water_pressure", "borewell_repair"],
                "default_officer": "Assistant Executive Engineer (AEE - Water Works)",
                "statutory_sla_days": 3,
                "calendar_type": "calendar_days"
            },
            "sewerage": {
                "id": "wing_sewerage",
                "code": "sewerage",
                "name": "Sewerage & Underground Drainage (UGD) Wing",
                "categories": ["sewage_overflow", "sewer_pipeline_choke", "manhole_overflow"],
                "default_officer": "Assistant Engineer (AE - UGD)",
                "statutory_sla_days": 3,
                "calendar_type": "working_days"
            },
            "street_lights": {
                "id": "wing_street_lights",
                "code": "street_lights",
                "name": "Street Lighting & Electrical Maintenance Wing",
                "categories": ["street_light_failure", "exposed_electrical_wires", "damaged_electric_pole", "transformer_spark"],
                "default_officer": "Assistant Engineer (AE - Electrical)",
                "statutory_sla_days": 2,
                "calendar_type": "calendar_days"
            },
            "public_buildings": {
                "id": "wing_public_buildings",
                "code": "public_buildings",
                "name": "Public Buildings and Civic Infrastructure Wing",
                "categories": ["community_hall_repair", "municipal_market_maintenance", "public_infrastructure_damage"],
                "default_officer": "Assistant Engineer (AE - Buildings)",
                "statutory_sla_days": 15,
                "calendar_type": "working_days"
            },
            "parks": {
                "id": "wing_parks",
                "code": "parks",
                "name": "Parks & Public Amenities Wing",
                "categories": ["park_maintenance", "tree_cutting_hazard", "public_garden_lighting"],
                "default_officer": "Horticulture Officer / AE (Parks)",
                "statutory_sla_days": 7,
                "calendar_type": "working_days"
            }
        }
    },
    "public_health": {
        "id": "dept_public_health",
        "code": "public_health",
        "name": "Public Health and Sanitation Department",
        "head_designation": "Chief Municipal Health Officer (CMHO) / Municipal Health Officer (MHO)",
        "legal_basis": "AP Municipalities Act 1965, Sec. 124 & CDMA Citizen Charter",
        "functional_wings": {
            "solid_waste": {
                "id": "wing_solid_waste",
                "code": "others",  # mapped to existing category 'others'
                "name": "Solid Waste Management & Garbage Collection Wing",
                "categories": ["garbage_dump", "overflowing_dustbin", "dead_animal_removal", "biomedical_waste"],
                "default_officer": "Sanitary Inspector (SI)",
                "statutory_sla_days": 1,
                "calendar_type": "calendar_days"
            },
            "street_cleaning": {
                "id": "wing_street_cleaning",
                "code": "street_cleaning",
                "name": "Street Sweeping & Public Sanitation Wing",
                "categories": ["street_sweeping", "debris_clearing", "litter_removal"],
                "default_officer": "Sanitary Inspector (SI)",
                "statutory_sla_days": 1,
                "calendar_type": "calendar_days"
            },
            "public_toilets": {
                "id": "wing_public_toilets",
                "code": "public_toilets",
                "name": "Public Toilets & Community Sanitation Wing",
                "categories": ["toilet_cleaning", "toilet_water_shortage", "broken_toilet_fitting"],
                "default_officer": "Sanitary Inspector (SI)",
                "statutory_sla_days": 1,
                "calendar_type": "calendar_days"
            },
            "vector_control": {
                "id": "wing_vector_control",
                "code": "vector_control",
                "name": "Vector Control & Anti-Larval Operations Wing",
                "categories": ["mosquito_breeding", "fogging_request", "stagnant_water_pest"],
                "default_officer": "Health Assistant / Vector Control Officer",
                "statutory_sla_days": 2,
                "calendar_type": "working_days"
            }
        }
    },
    "town_planning": {
        "id": "dept_town_planning",
        "code": "town_planning",
        "name": "Town Planning Department",
        "head_designation": "City Planner (CP) / Assistant City Planner (ACP)",
        "legal_basis": "Andhra Pradesh Metropolitan Region and Urban Development Authorities Act & Municipal Building Rules",
        "functional_wings": {
            "building_permissions": {
                "id": "wing_building_permissions",
                "code": "building_permissions",
                "name": "Building Permissions & Layout Clearances Wing",
                "categories": ["plan_approval_delay", "layout_verification", "occupancy_certificate"],
                "default_officer": "Town Planning Officer (TPO)",
                "statutory_sla_days": 21,
                "calendar_type": "working_days"
            },
            "unauthorized_construction": {
                "id": "wing_unauthorized_construction",
                "code": "unauthorized_construction",
                "name": "Unauthorized Construction & Encroachment Wing",
                "categories": ["unauthorized_building", "road_encroachment", "drain_encroachment", "setback_violation"],
                "default_officer": "Town Planning Supervisor (TPS)",
                "statutory_sla_days": 7,
                "calendar_type": "working_days"
            }
        }
    },
    "revenue": {
        "id": "dept_revenue",
        "code": "revenue",
        "name": "Revenue Department",
        "head_designation": "Revenue Officer (RO) / Assistant Commissioner (Revenue)",
        "legal_basis": "AP Municipalities Act 1965, Property Tax Assessment Rules",
        "functional_wings": {
            "property_tax": {
                "id": "wing_property_tax",
                "code": "property_tax",
                "name": "Property Tax & Mutation Wing",
                "categories": ["tax_assessment_error", "name_transfer_delay", "door_number_allocation"],
                "default_officer": "Revenue Inspector (RI)",
                "statutory_sla_days": 15,
                "calendar_type": "working_days"
            },
            "trade_license": {
                "id": "wing_trade_license",
                "code": "trade_license",
                "name": "Trade Licenses & Municipal Leases Wing",
                "categories": ["trade_license_issuance", "advertisement_fee_issue", "municipal_shop_rent"],
                "default_officer": "Revenue Inspector (RI)",
                "statutory_sla_days": 10,
                "calendar_type": "working_days"
            }
        }
    },
    "administration": {
        "id": "dept_administration",
        "code": "administration",
        "name": "Administration & Citizen Services Department",
        "head_designation": "Municipal Commissioner / Additional Commissioner",
        "legal_basis": "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
        "functional_wings": {
            "pgrs_coordination": {
                "id": "wing_pgrs",
                "code": "pgrs",
                "name": "Public Grievance Redressal System (PGRS) Cell",
                "categories": ["interdepartmental_escalation", "grievance_appeal", "spandana_case"],
                "default_officer": "Grievance Redressal Officer (GRO)",
                "statutory_sla_days": 7,
                "calendar_type": "working_days"
            },
            "birth_death": {
                "id": "wing_birth_death",
                "code": "birth_death",
                "name": "Birth & Death Registration Wing",
                "categories": ["birth_certificate", "death_certificate", "record_correction"],
                "default_officer": "Sub-Registrar (Births & Deaths)",
                "statutory_sla_days": 7,
                "calendar_type": "working_days"
            }
        }
    }
}

# -----------------------------------------------------------------------------
# 2. CATEGORY TO DEPARTMENT & WING MAPPER
# -----------------------------------------------------------------------------
CATEGORY_TO_DEPT_MAP: Dict[str, Dict[str, str]] = {
    # Road
    "road": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 7},
    "potholes": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 7},
    "damaged_roads": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 7},
    "footpath_damage": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 7},
    "road_obstruction": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 2},
    "road_cave_in": {"dept_code": "engineering", "wing_code": "road", "dept_name": "Roads & Buildings Department", "sla_days": 1},

    # Drainage
    "drainage": {"dept_code": "engineering", "wing_code": "drainage", "dept_name": "Public Health & Drainage Department", "sla_days": 3},
    "blocked_drainage": {"dept_code": "engineering", "wing_code": "drainage", "dept_name": "Public Health & Drainage Department", "sla_days": 3},
    "drainage_overflow": {"dept_code": "engineering", "wing_code": "drainage", "dept_name": "Public Health & Drainage Department", "sla_days": 2},
    "open_manhole": {"dept_code": "engineering", "wing_code": "drainage", "dept_name": "Public Health & Drainage Department", "sla_days": 1},
    "sewerage": {"dept_code": "engineering", "wing_code": "sewerage", "dept_name": "Public Health & Drainage Department", "sla_days": 3},

    # Water Supply
    "water_supply": {"dept_code": "engineering", "wing_code": "water_supply", "dept_name": "Water Supply & Quality Department", "sla_days": 3},
    "pipeline_leakage": {"dept_code": "engineering", "wing_code": "water_supply", "dept_name": "Water Supply & Quality Department", "sla_days": 2},
    "no_water_supply": {"dept_code": "engineering", "wing_code": "water_supply", "dept_name": "Water Supply & Quality Department", "sla_days": 1},
    "water_contamination": {"dept_code": "engineering", "wing_code": "water_supply", "dept_name": "Water Supply & Quality Department", "sla_days": 1},
    "low_water_pressure": {"dept_code": "engineering", "wing_code": "water_supply", "dept_name": "Water Supply & Quality Department", "sla_days": 3},

    # Street Lighting
    "street_lights": {"dept_code": "engineering", "wing_code": "street_lights", "dept_name": "Electrical & Street Lighting Wing", "sla_days": 2},
    "street_light_failure": {"dept_code": "engineering", "wing_code": "street_lights", "dept_name": "Electrical & Street Lighting Wing", "sla_days": 2},
    "exposed_electrical_wires": {"dept_code": "engineering", "wing_code": "street_lights", "dept_name": "Electrical & Street Lighting Wing", "sla_days": 1},
    "damaged_electric_pole": {"dept_code": "engineering", "wing_code": "street_lights", "dept_name": "Electrical & Street Lighting Wing", "sla_days": 1},

    # Public Health / Sanitation / Others
    "others": {"dept_code": "public_health", "wing_code": "solid_waste", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "garbage_dump": {"dept_code": "public_health", "wing_code": "solid_waste", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "overflowing_dustbin": {"dept_code": "public_health", "wing_code": "solid_waste", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "dead_animal_removal": {"dept_code": "public_health", "wing_code": "solid_waste", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "street_cleaning": {"dept_code": "public_health", "wing_code": "street_cleaning", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "public_toilets": {"dept_code": "public_health", "wing_code": "public_toilets", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 1},
    "vector_control": {"dept_code": "public_health", "wing_code": "vector_control", "dept_name": "Sanitation & Solid Waste Management Wing", "sla_days": 2},

    # Town Planning
    "town_planning": {"dept_code": "town_planning", "wing_code": "unauthorized_construction", "dept_name": "Town Planning Department", "sla_days": 7},
    "encroachment": {"dept_code": "town_planning", "wing_code": "unauthorized_construction", "dept_name": "Town Planning Department", "sla_days": 7},
    "unauthorized_construction": {"dept_code": "town_planning", "wing_code": "unauthorized_construction", "dept_name": "Town Planning Department", "sla_days": 7},

    # Revenue
    "revenue": {"dept_code": "revenue", "wing_code": "property_tax", "dept_name": "Revenue Department", "sla_days": 15},
    "property_tax": {"dept_code": "revenue", "wing_code": "property_tax", "dept_name": "Revenue Department", "sla_days": 15}
}

def resolve_department_and_wing(category_or_text: str) -> Dict[str, Any]:
    """
    Intelligently maps a complaint category or key to its AP administrative department,
    functional wing, and statutory deadline defaults.
    """
    cat = (category_or_text or "").lower().strip()
    if cat in CATEGORY_TO_DEPT_MAP:
        mapping = CATEGORY_TO_DEPT_MAP[cat]
        dept_info = AP_DEPARTMENTS_CONFIG.get(mapping["dept_code"], {})
        return {
            "department_id": dept_info.get("id", "dept_engineering"),
            "department_code": mapping["dept_code"],
            "department_name": mapping["dept_name"],
            "functional_wing_id": mapping["wing_code"],
            "functional_wing_name": dept_info.get("functional_wings", {}).get(mapping["wing_code"], {}).get("name", mapping["wing_code"]),
            "statutory_sla_days": mapping["sla_days"]
        }

    # Fallback to engineering or public health based on keyword
    for key, val in CATEGORY_TO_DEPT_MAP.items():
        if key in cat or cat in key:
            dept_info = AP_DEPARTMENTS_CONFIG.get(val["dept_code"], {})
            return {
                "department_id": dept_info.get("id", "dept_engineering"),
                "department_code": val["dept_code"],
                "department_name": val["dept_name"],
                "functional_wing_id": val["wing_code"],
                "functional_wing_name": dept_info.get("functional_wings", {}).get(val["wing_code"], {}).get("name", val["wing_code"]),
                "statutory_sla_days": val["sla_days"]
            }

    # Default to public health sanitation
    return {
        "department_id": "dept_public_health",
        "department_code": "public_health",
        "department_name": "Sanitation & Solid Waste Management Wing",
        "functional_wing_id": "solid_waste",
        "functional_wing_name": "Solid Waste Management & Garbage Collection Wing",
        "statutory_sla_days": 2
    }
