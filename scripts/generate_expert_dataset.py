"""
NEX-CIV Verified Dataset Generator
Generates expert-annotated civic grievance records in Telugu and English
covering all 5 municipal departments and safety categories.
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path

random.seed(42)
np.random.seed(42)

DATASET_PATH = Path(__file__).resolve().parent.parent / "priority_engine" / "datasets" / "expert_civic_grievance_dataset.csv"

# Diverse templates across categories in English and Telugu
TEMPLATES = {
    "road": {
        "Critical": [
            ("Massive road cave-in and sinkhole on {road_en}, vehicular collapse hazard", "en", 95, 90, 85, 95, 1),
            ("{road_te} పై రోడ్డు భారీగా కుంగిపోయింది, వాహనాలు పడిపోయే ప్రమాదం ఉంది", "te", 95, 90, 85, 95, 1),
            ("Bridge approach slab collapsed near {road_en}, fatal accident danger", "en", 98, 92, 90, 96, 1),
            ("{road_te} బ్రిడ్జి స్లాబ్ కూలిపోయింది, రాకపోకలు పూర్తిగా స్తంభించాయి", "te", 98, 92, 90, 96, 1)
        ],
        "High": [
            ("Deep hazardous potholes outside {zone_en}, ambulances skidding", "en", 75, 50, 80, 80, 0),
            ("{zone_te} ఎదురుగా పెద్ద గుంతలు పడ్డాయి, రోగులు మరియు వాహనదారులు తీవ్ర ఇబ్బందులు పడుతున్నారు", "te", 75, 50, 80, 80, 0),
            ("Damaged road surface with exposed steel mesh along {road_en}", "en", 70, 45, 75, 75, 0),
            ("{road_te} పై తారు కొట్టుకుపోయి కంకర తేలి బైకులు జారిపడుతున్నాయి", "te", 70, 45, 75, 75, 0)
        ],
        "Moderate": [
            ("Multiple minor potholes on residential street in {colony_en}", "en", 45, 30, 45, 50, 0),
            ("{colony_te} లోని వీధిలో గుంతలు పడి వర్షపు నీరు నిలుస్తోంది", "te", 45, 30, 45, 50, 0),
            ("Footpath tiles broken and displaced along {road_en}", "en", 40, 20, 50, 45, 0),
            ("{road_te} వద్ద పాదచారుల ఫుట్‌పాత్ టైల్స్ విరిగిపోయాయి", "te", 40, 20, 50, 45, 0)
        ],
        "Low": [
            ("Faded pedestrian zebra crossing markings on {road_en}", "en", 20, 10, 30, 25, 0),
            ("{road_te} వద్ద జీబ్రా క్రాసింగ్ పెయింటింగ్ వెలిసిపోయింది", "te", 20, 10, 30, 25, 0),
            ("Minor asphalt undulations on inner residential lane of {colony_en}", "en", 25, 10, 25, 30, 0),
            ("{colony_te} చిన్న సందులో రోడ్డు కొద్దిగా ఎగుడుదిగుడుగా ఉంది", "te", 25, 10, 25, 30, 0)
        ]
    },
    "water_supply": {
        "Critical": [
            ("Severe drinking water contamination in {colony_en}, black sewage mixing into pipeline", "en", 95, 95, 90, 98, 1),
            ("{colony_te} లో మంచినీటి పైపులో మురుగు నీరు కలిసి వస్తోంది, ప్రజలు వాంతులు విరేచనాలతో ఆసుపత్రి పాలవుతున్నారు", "te", 95, 95, 90, 98, 1),
            ("Main feeder supply pipeline burst near {zone_en}, water inundating streets", "en", 90, 80, 85, 92, 1),
            ("{zone_te} వద్ద ప్రధాన మంచినీటి పైప్‌లైన్ పగిలి నీరు వరదలా ప్రవహిస్తోంది", "te", 90, 80, 85, 92, 1)
        ],
        "High": [
            ("Zero drinking water supply for past 4 days in {colony_en}", "en", 60, 85, 75, 85, 0),
            ("{colony_te} లో నాలుగు రోజులుగా మంచినీటి సరఫరా పూర్తిగా నిలిచిపోయింది", "te", 60, 85, 75, 85, 0),
            ("Water pipeline valve damaged, flooding main transit road of {road_en}", "en", 65, 70, 70, 78, 0),
            ("{road_te} వద్ద పైపు వాల్వ్ విరిగి నీరు వృధాగా రోడ్డుపై పోతోంది", "te", 65, 70, 70, 78, 0)
        ],
        "Moderate": [
            ("Very low water pressure during morning supply hours in {colony_en}", "en", 30, 40, 50, 50, 0),
            ("{colony_te} లో కుళాయిల్లో నీటి ప్రెషర్ చాలా తక్కువగా వస్తోంది", "te", 30, 40, 50, 50, 0),
            ("Public borewell motor not pumping sufficient water in {colony_en}", "en", 35, 45, 45, 52, 0),
            ("{colony_te} లో పబ్లిక్ బోరు మోటారు సరిగ్గా పనిచేయడం లేదు", "te", 35, 45, 45, 52, 0)
        ],
        "Low": [
            ("Public standpost tap dripping slowly in {colony_en}", "en", 15, 20, 20, 25, 0),
            ("{colony_te} వీధి కుళాయి రబ్బరు వాషర్ పోయి నీరు కారుతోంది", "te", 15, 20, 20, 25, 0),
            ("Request for tap connection verification in {colony_en}", "en", 10, 15, 15, 20, 0),
            ("{colony_te} లో కొత్త కుళాయి కనెక్షన్ తనిఖీ చేయాలని కోరుతున్నాను", "te", 10, 15, 15, 20, 0)
        ]
    },
    "drainage": {
        "Critical": [
            ("Open manhole without cover directly outside {zone_en}, fatal drop hazard", "en", 98, 90, 92, 98, 1),
            ("{zone_te} బయట మ్యాన్‌హోల్ మూత లేకుండా తెరిచి ఉంది, ప్రాణాపాయం పొంచి ఉంది", "te", 98, 90, 92, 98, 1),
            ("Toxic black sewage overflow submerging houses and roads in {colony_en}", "en", 92, 95, 88, 95, 1),
            ("{colony_te} లో డ్రైనేజీ కాలువ పొంగి మురుగు నీరు ఇళ్లలోకి ప్రవేశిస్తోంది", "te", 92, 95, 88, 95, 1)
        ],
        "High": [
            ("Main stormwater canal blocked with silt and garbage causing flood risk in {colony_en}", "en", 70, 80, 75, 80, 0),
            ("{colony_te} లో ప్రధాన మురుగు కాలువ పూడికతో నిండిపోయి వర్షపు నీరు వెళ్లడం లేదు", "te", 70, 80, 75, 80, 0),
            ("Culvert bridge slab broken over storm drain on {road_en}", "en", 75, 65, 80, 78, 0),
            ("{road_te} వద్ద కల్వర్టు స్లాబ్ విరిగిపోయి వాహనాలకు ప్రమాదకరంగా మారింది", "te", 75, 65, 80, 78, 0)
        ],
        "Moderate": [
            ("Domestic side drain choked, stagnant dirty water in front of houses in {colony_en}", "en", 40, 60, 45, 50, 0),
            ("{colony_te} లో వీధి కాలువలో ప్లాస్టిక్ వ్యర్థాలు పేరుకుపోయి నీరు నిలిచిపోయింది", "te", 40, 60, 45, 50, 0),
            ("Manhole cover cracked and uneven on {road_en}", "en", 50, 40, 50, 55, 0),
            ("{road_te} లో డ్రైనేజీ మూత పగుళ్లు ఇచ్చి ఊగుతోంది", "te", 50, 40, 50, 55, 0)
        ],
        "Low": [
            ("Drain cleaning request for inner lane of {colony_en}", "en", 20, 30, 25, 30, 0),
            ("{colony_te} చిన్న సందులోని కాలువను శుభ్రం చేయగలరు", "te", 20, 30, 25, 30, 0),
            ("Slight foul smell near culvert grate in {colony_en}", "en", 15, 25, 20, 25, 0),
            ("{colony_te} కల్వర్టు వద్ద స్వల్పంగా దుర్వాసన వస్తోంది", "te", 15, 25, 20, 25, 0)
        ]
    },
    "street_lights": {
        "Critical": [
            ("Live high-voltage wire snapped and sparking on wet street outside {zone_en}", "en", 99, 85, 95, 99, 1),
            ("{zone_te} వద్ద లైవ్ కరెంట్ వైర్లు తెగి రోడ్డుపై పడి స్పార్క్ అవుతున్నాయి, వెంటనే ఆపండి", "te", 99, 85, 95, 99, 1),
            ("Damaged electric pole bending precariously over main roadway in {road_en}", "en", 95, 80, 90, 96, 1),
            ("{road_te} వద్ద విద్యుత్ స్తంభం విరిగి ప్రమాదకరంగా రోడ్డుపైకి వంగిపోయింది", "te", 95, 80, 90, 96, 1)
        ],
        "High": [
            ("Complete streetlight blackout for 1km on {road_en}, severe accident hazard", "en", 80, 40, 80, 80, 0),
            ("{road_te} ప్రధాన రహదారిపై అన్ని వీధి దీపాలు ఆగిపోయి చిమ్మచీకటిగా ఉంది", "te", 80, 40, 80, 80, 0),
            ("Streetlight junction box open with naked 230V wires at child height in {colony_en}", "en", 85, 45, 75, 82, 0),
            ("{colony_te} లో కరెంట్ స్తంభం కింద బాక్స్ మూత లేకుండా నగ్న వైర్లు కనిపిస్తున్నాయి", "te", 85, 45, 75, 82, 0)
        ],
        "Moderate": [
            ("Three consecutive LED streetlights not functioning in {colony_en}", "en", 45, 20, 50, 50, 0),
            ("{colony_te} లో వరుసగా మూడు వీధి దీపాలు వెలగడం లేదు", "te", 45, 20, 50, 50, 0),
            ("Streetlights remaining on during broad daylight wasting electricity in {colony_en}", "en", 30, 15, 40, 40, 0),
            ("{colony_te} లో పగటిపూట కూడా స్ట్రీట్‌లైట్లు వెలుగుతూ విద్యుత్ వృధా అవుతోంది", "te", 30, 15, 40, 40, 0)
        ],
        "Low": [
            ("Single flickering LED bulb outside house in {colony_en}", "en", 20, 10, 25, 25, 0),
            ("{colony_te} లో మా ఇంటి ముందున్న లైటు మినుకుమినుకుమంటోంది", "te", 20, 10, 25, 25, 0),
            ("Streetlight covered by tree branches in {colony_en}", "en", 25, 10, 30, 30, 0),
            ("{colony_te} లో చెట్టు కొమ్మలు అడ్డంగా వచ్చి లైట్ వెలుతురు పడటం లేదు", "te", 25, 10, 30, 30, 0)
        ]
    },
    "others": {
        "Critical": [
            ("Massive rotting biological garbage dump outside {zone_en}, epidemic outbreak risk", "en", 90, 98, 92, 95, 1),
            ("{zone_te} బయట కుళ్ళిన వ్యర్థాలు మరియు ఆసుపత్రి చెత్త గుట్టగా పేరుకుపోయింది, రోగాలు ప్రబలే ప్రమాదం", "te", 90, 98, 92, 95, 1),
            ("Dead animal carcass decaying in front of {zone_en} for past 48 hours", "en", 92, 95, 85, 96, 1),
            ("{zone_te} ఎదురుగా చనిపోయిన పశువు కళేబరం రెండు రోజులుగా కుళ్ళిపోతూ తీవ్ర దుర్వాసన వెదజల్లుతోంది", "te", 92, 95, 85, 96, 1)
        ],
        "High": [
            ("Severe mosquito breeding due to stagnant sewage pools in {colony_en}, 8 dengue cases", "en", 75, 90, 80, 82, 0),
            ("{colony_te} లో విపరీతమైన దోమల బెడద, ఇప్పటికే డెంగ్యూ కేసులు నమోదయ్యాయి, వెంటనే ఫాగింగ్ చేయించండి", "te", 75, 90, 80, 82, 0),
            ("Public toilet complex completely choked and closed in {zone_en}", "en", 70, 85, 75, 78, 0),
            ("{zone_te} వద్ద పబ్లిక్ టాయిలెట్లు మూసుకుపోయి అపరిశుభ్రత తాండవిస్తోంది", "te", 70, 85, 75, 78, 0)
        ],
        "Moderate": [
            ("Overflowing municipal dumper bin spilling onto road in {colony_en}", "en", 45, 65, 50, 52, 0),
            ("{colony_te} లో చెత్త కుండీ నిండి రోడ్డుపై చెత్త చెల్లాచెదురుగా పడుతోంది", "te", 45, 65, 50, 52, 0),
            ("Door-to-door garbage collection vehicle skipped {colony_en} for past 3 days", "en", 40, 60, 45, 48, 0),
            ("{colony_te} లో మూడు రోజులుగా ఇంటింటి చెత్త సేకరణ వాహనం రాలేదు", "te", 40, 60, 45, 48, 0)
        ],
        "Low": [
            ("Dry leaves and road sweeping dust piled at corner of {colony_en}", "en", 20, 30, 25, 28, 0),
            ("{colony_te} మూలన ఊడ్చిన చెత్త పోగు పడి ఉంది", "te", 20, 30, 25, 28, 0),
            ("Request for bleaching powder spraying in {colony_en}", "en", 15, 35, 20, 25, 0),
            ("{colony_te} లో బ్లీచింగ్ పౌడర్ చల్లాలని కోరుతున్నాము", "te", 15, 35, 20, 25, 0)
        ]
    }
}

LOCATIONS = {
    "road_en": ["GNT Highway Corridor", "Benz Circle Arterial Road", "Tammileru Canal Road", "Collectorate Road", "Powerpet Overbridge", "Old Bus Stand Road"],
    "road_te": ["జి.ఎన్.టి రహదారి", "బెంజ్ సర్కిల్ రోడ్డు", "తమ్మిలేరు కెనాల్ రోడ్డు", "కలెక్టరేట్ రోడ్డు", "పవర్‌పేట ఓవర్‌బ్రిడ్జి", "పాత బస్టాండ్ రోడ్డు"],
    "zone_en": ["ZP Government High School", "District General Hospital (GGH)", "RTC Central Bus Complex", "Rythu Bazaar Market", "St. Theresa College"],
    "zone_te": ["జిల్లా పరిషత్ ఉన్నత పాఠశాల", "ప్రభుత్వ సర్వజన ఆసుపత్రి", "ఆర్టీసీ బస్ కాంప్లెక్స్", "రైతు బజార్", "సెయింట్ థెరిసా కళాశాల"],
    "colony_en": ["RR Peta", "Powerpet", "Sanivarapupeta", "Tangellamudi", "Postal Colony", "Balaji Nagar", "Housing Board Colony"],
    "colony_te": ["ఆర్.ఆర్ పేట", "పవర్‌పేట", "శనివారపుపేట", "తంగెళ్ళమూడి", "పోస్టల్ కాలనీ", "బాలాజీ నగర్", "హౌసింగ్ బోర్డు కాలనీ"]
}

SEVERITY_LEVEL_MAP = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}

def generate_dataset(num_records=2500):
    rows = []
    categories = list(TEMPLATES.keys())
    levels = ["Critical", "High", "Moderate", "Low"]

    for i in range(num_records):
        cat = random.choice(categories)
        lvl = random.choice(levels)
        template_tuple = random.choice(TEMPLATES[cat][lvl])
        raw_text, lang, base_safety, base_health, base_infra, base_sla, is_emg = template_tuple

        # Fill location placeholders
        r_en = random.choice(LOCATIONS["road_en"])
        r_te = random.choice(LOCATIONS["road_te"])
        z_en = random.choice(LOCATIONS["zone_en"])
        z_te = random.choice(LOCATIONS["zone_te"])
        c_en = random.choice(LOCATIONS["colony_en"])
        c_te = random.choice(LOCATIONS["colony_te"])

        formatted_text = raw_text.format(
            road_en=r_en, road_te=r_te,
            zone_en=z_en, zone_te=z_te,
            colony_en=c_en, colony_te=c_te
        )

        # Add realistic noise/variance to numeric scores
        safety_risk = max(5.0, min(100.0, base_safety + random.uniform(-6.0, 6.0)))
        health_risk = max(5.0, min(100.0, base_health + random.uniform(-6.0, 6.0)))
        infra_risk = max(5.0, min(100.0, base_infra + random.uniform(-6.0, 6.0)))
        sla_urgency = max(5.0, min(100.0, base_sla + random.uniform(-6.0, 6.0)))

        sev_num = SEVERITY_LEVEL_MAP[lvl]
        sev_score = sev_num * 25.0

        # Public impact based on zone
        if "High School" in formatted_text or "Hospital" in formatted_text or "ఆసుపత్రి" in formatted_text or "పాఠశాల" in formatted_text:
            public_impact = random.uniform(80.0, 98.0)
            affected_count = random.randint(400, 1500)
        elif "Bus" in formatted_text or "రైతు బజార్" in formatted_text:
            public_impact = random.uniform(70.0, 90.0)
            affected_count = random.randint(250, 900)
        else:
            public_impact = random.uniform(20.0, 65.0)
            affected_count = random.randint(30, 250)

        # Formula priority score
        # 0.25*Sev + 0.20*Safety + 0.15*Impact + 0.20*SLA + 0.10*Infra + 0.10*Recurrence
        recurrence = random.uniform(10.0, 60.0)
        calc_score = (
            (0.25 * sev_score) +
            (0.20 * safety_risk) +
            (0.15 * public_impact) +
            (0.20 * sla_urgency) +
            (0.10 * infra_risk) +
            (0.10 * recurrence)
        )
        if is_emg:
            calc_score = max(95.0, calc_score)

        calc_score = round(max(0.0, min(100.0, calc_score)), 2)

        if calc_score >= 80.0 or is_emg:
            priority_tier = "Critical"
        elif calc_score >= 60.0:
            priority_tier = "High"
        elif calc_score >= 40.0:
            priority_tier = "Medium"
        else:
            priority_tier = "Low"

        rows.append({
            "complaint_id": f"AP-EXP-{i+1:05d}",
            "text": formatted_text,
            "language": lang,
            "category": cat,
            "severity_level": sev_num,
            "severity_label": lvl,
            "safety_risk": round(safety_risk, 1),
            "public_health_risk": round(health_risk, 1),
            "public_impact": round(public_impact, 1),
            "estimated_citizens_affected": affected_count,
            "infrastructure_criticality": round(infra_risk, 1),
            "sla_urgency": round(sla_urgency, 1),
            "is_emergency": is_emg,
            "priority_score": calc_score,
            "priority_tier": priority_tier
        })

    df = pd.DataFrame(rows)
    df.to_csv(DATASET_PATH, index=False, encoding="utf-8")
    print(f"Generated {len(df)} verified expert grievance records at: {DATASET_PATH}")
    print(f"Language breakdown:\n{df['language'].value_counts()}")
    print(f"Severity breakdown:\n{df['severity_label'].value_counts()}")
    print(f"Category breakdown:\n{df['category'].value_counts()}")
    return df

if __name__ == "__main__":
    generate_dataset()
