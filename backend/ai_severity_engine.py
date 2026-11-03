"""
NEX-CIV Multilingual Complaint Severity & Risk AI Engine
Evaluates Telugu & English civic grievance text and multimodal evidence.
Produces:
- Complaint Severity (1: Low, 2: Moderate, 3: High, 4: Critical)
- Public Safety Risk (0 - 100)
- Public Health Risk (0 - 100)
- Critical Infrastructure Impact (0 - 100)
- Vulnerable Population Multiplier
- Estimated Citizens Affected Count
"""

import re
import os
import joblib
from typing import Dict, Any, List, Optional, Tuple

# Telugu and English Safety & Severity Indicators
CRITICAL_SAFETY_PATTERNS = [
    # English
    r'\b(live wire|exposed wire|sparking|electric shock|transformer burst|electrocution)\b',
    r'\b(cave-in|massive sinkhole|bridge collapse|deep trench|fatal accident|skidding)\b',
    r'\b(open manhole|missing manhole cover|manhole without lid|uncovered manhole)\b',
    r'\b(contaminated water|yellow water|sewage mixing with drinking water|epidemic|diarrhea|cholera)\b',
    r'\b(flash flood|submerged road|water entering houses|severe flooding|drowning)\b',
    # Telugu (తెలుగు)
    r'(కరెంట్ వైర్లు|లైవ్ వైర్|షాక్|స్పార్కింగ్|ట్రాన్స్‌ఫార్మర్|విద్యుత్ ప్రమాదం)',
    r'(రోడ్డు కుంగిపోయింది|పెద్ద గుంత|రహదారి ప్రమాదం|ప్రాణాంతక|కూలిపోయింది)',
    r'(మ్యాన్‌హోల్ మూత లేదు|ఓపెన్ మ్యాన్‌హోల్|తెరిచి ఉన్న మ్యాన్‌హోల్)',
    r'(కలుషిత నీరు|మురుగు నీరు కలుస్తోంది|దుర్వాసన|వాంతులు|అతిసారం|కలరా)',
    r'(వరద నీరు|మునిగిపోయిన రోడ్డు|ఇళ్లలోకి నీరు|ముంపు ప్రమాదం)'
]

HIGH_RISK_PATTERNS = [
    r'\b(major pothole|deep crater|traffic jam|road blocked|culvert damaged)\b',
    r'\b(drainage choked|sewage overflow|foul smell|mosquito menace|dengue|malaria)\b',
    r'\b(no drinking water for 3 days|water pipeline broken|dry tap)\b',
    r'\b(darkness at night|all streetlights off|women safety|robbery hazard)\b',
    r'(పెద్ద గుంతలు|ట్రాఫిక్ జామ్|కాలువ బ్లాక్|మురుగు పొంగుతోంది|దోమలు|డెంగ్యూ)',
    r'(మూడు రోజులుగా నీళ్లు లేవు|పైప్‌లైన్ పగిలింది|చీకటి|వీధి దీపాలు వెలగడం లేదు)'
]

VULNERABLE_ZONE_KEYWORDS = {
    "hospital": [
        "hospital", "clinic", "dispensary", "casualty", "icu", "trauma", "kgh", "ggh", "ruia", "phc", "chc",
        "ఆసుపత్రి", "దవాఖాన", "క్లినిక్"
    ],
    "school": [
        "school", "college", "university", "kindergarten", "campus", "playground", "students", "children",
        "పాఠశాల", "బడి", "కళాశాల", "విద్యార్థులు"
    ],
    "transit_hub": [
        "bus stand", "bus station", "railway station", "rtc", "pnbs", "metro", "market", "rythu bazaar",
        "బస్ స్టాండ్", "రైల్వే స్టేషన్", "రైతు బజార్", "మార్కెట్"
    ]
}

def analyze_complaint_severity(
    text: str,
    category: Optional[str] = None,
    defect_type: Optional[str] = None,
    zone_type: Optional[str] = "residential",
    location_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates multi-dimensional risk and assigns severity level (1 to 4)
    along with transparent explainability signals.
    """
    content = (text or "").lower()
    loc = (location_address or "").lower()
    full_text = f"{content} {loc}"

    # 1. Detect Safety Risk
    safety_risk = 20.0
    is_life_threatening = False
    safety_triggers = []

    for pattern in CRITICAL_SAFETY_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            safety_risk = 95.0
            is_life_threatening = True
            safety_triggers.append(match.group(0))
            break

    if not is_life_threatening:
        for pattern in HIGH_RISK_PATTERNS:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                safety_risk = 70.0
                safety_triggers.append(match.group(0))
                break

    # 2. Detect Public Health Risk
    public_health_risk = 15.0
    if category in ["drainage", "water_supply", "others"] or defect_type in [
        "water_contamination", "drainage_overflow", "open_manhole", "garbage_dump", "dead_animal_removal"
    ]:
        if "contamination" in full_text or "కలుషిత" in full_text or "cholera" in full_text:
            public_health_risk = 95.0
        elif "overflow" in full_text or "మురుగు" in full_text or "stagnant" in full_text:
            public_health_risk = 80.0
        else:
            public_health_risk = 60.0

    # 3. Detect Infrastructure Criticality
    infrastructure_criticality = 30.0
    if category == "road":
        if "highway" in full_text or "nh-16" in full_text or "nh-65" in full_text or "flyover" in full_text or "bridge" in full_text:
            infrastructure_criticality = 90.0
        elif "main road" in full_text or "arterial" in full_text or "bus route" in full_text:
            infrastructure_criticality = 75.0
        else:
            infrastructure_criticality = 50.0
    elif category == "water_supply":
        if "main pipeline" in full_text or "feeder" in full_text or "tank" in full_text:
            infrastructure_criticality = 85.0
        else:
            infrastructure_criticality = 60.0
    elif category == "street_lights":
        if "high tension" in full_text or "transformer" in full_text or "substation" in full_text:
            infrastructure_criticality = 90.0
        else:
            infrastructure_criticality = 45.0

    # 4. Vulnerable Population & Density Impact
    vulnerability_multiplier = 1.0
    vulnerable_tag = "Standard Civic Zone"
    for zone_cat, kw_list in VULNERABLE_ZONE_KEYWORDS.items():
        for kw in kw_list:
            if kw in full_text:
                if zone_cat == "hospital":
                    vulnerability_multiplier = 1.50
                    vulnerable_tag = "Hospital / Healthcare Emergency Zone"
                    break
                elif zone_cat == "school":
                    vulnerability_multiplier = 1.35
                    vulnerable_tag = "School / Educational Corridor"
                    break
                elif zone_cat == "transit_hub":
                    vulnerability_multiplier = 1.25
                    vulnerable_tag = "Transit Hub / Public Concourse"
                    break
        if vulnerability_multiplier > 1.0:
            break

    # 5. Estimate Citizens Affected
    base_affected = 50
    if "entire colony" in full_text or "whole area" in full_text or "కాలనీ అంతా" in full_text:
        base_affected = 1500
    elif "main road" in full_text or "junction" in full_text or "street" in full_text:
        base_affected = 400
    elif "hospital" in full_text or "school" in full_text:
        base_affected = 800

    estimated_affected = int(base_affected * vulnerability_multiplier)
    public_impact_score = min(100.0, round((estimated_affected / 1000.0) * 100.0, 1))

    # 6. Final Severity Calculation
    if is_life_threatening or safety_risk >= 90.0 or public_health_risk >= 90.0:
        severity_level = 4
        severity_label = "Critical"
    elif safety_risk >= 65.0 or public_health_risk >= 70.0 or infrastructure_criticality >= 80.0:
        severity_level = 3
        severity_label = "High"
    elif safety_risk >= 40.0 or public_health_risk >= 40.0 or public_impact_score >= 40.0:
        severity_level = 2
        severity_label = "Moderate"
    else:
        severity_level = 1
        severity_label = "Low"

    return {
        "severity_level": severity_level,  # 1 to 4
        "severity_label": severity_label,  # Low, Moderate, High, Critical
        "severity_score": round((severity_level / 4.0) * 100.0, 1),  # 25, 50, 75, 100
        "safety_risk": safety_risk,
        "public_health_risk": public_health_risk,
        "infrastructure_criticality": infrastructure_criticality,
        "public_impact_score": public_impact_score,
        "estimated_citizens_affected": estimated_affected,
        "vulnerability_multiplier": vulnerability_multiplier,
        "vulnerable_tag": vulnerable_tag,
        "is_life_threatening": is_life_threatening,
        "triggers_found": safety_triggers,
        "language_detected": "te" if any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in text) else "en"
    }
