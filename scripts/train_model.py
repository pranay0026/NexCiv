import os
import random
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DEPARTMENTS = {
    'road': {
        'name': 'Roads & Buildings Department (R&B / Municipal)',
        'code': 'road',
        'short': 'Roads & Buildings',
        'head': 'Superintending Engineer (R&B / Municipal Corporation)'
    },
    'drainage': {
        'name': 'Public Health & Drainage Department',
        'code': 'drainage',
        'short': 'Drainage & Sewerage',
        'head': 'Executive Engineer (Public Health & Sewerage)'
    },
    'water_supply': {
        'name': 'Water Supply & Quality Department',
        'code': 'water_supply',
        'short': 'Water Supply Board',
        'head': 'Chief Water Works Engineer (CPWS / Municipal)'
    },
    'street_lights': {
        'name': 'Electrical & Street Lighting Wing',
        'code': 'street_lights',
        'short': 'Electrical & Lighting',
        'head': 'Executive Engineer (APEPDCL / APSPDCL / Municipal)'
    },
    'others': {
        'name': 'Sanitation & Solid Waste Management Wing',
        'code': 'others',
        'short': 'Sanitation & SWM',
        'head': 'Chief Municipal Health Officer (CMHO)'
    }
}

WINGS = list(DEPARTMENTS.keys())
PRIORITIES = ['Critical', 'High', 'Medium', 'Low']

BENCHMARK_LOCATIONS = [
    {'name': 'King George Hospital (KGH) Casualty Gate, Maharanipeta, Visakhapatnam', 'lat': 17.7102, 'lng': 83.3050, 'zone_type': 'hospital', 'vulnerability_weight': 1.50},
    {'name': 'Government General Hospital (GGH) Emergency Ward, Hanumanpet, Vijayawada', 'lat': 16.5120, 'lng': 80.6270, 'zone_type': 'hospital', 'vulnerability_weight': 1.50},
    {'name': 'AIIMS Mangalagiri Emergency Approach Road, Amaravati Capital Region', 'lat': 16.4420, 'lng': 80.5640, 'zone_type': 'hospital', 'vulnerability_weight': 1.50},
    {'name': 'SVIMS & Ruia Government Hospital Road, Alipiri, Tirupati', 'lat': 13.6380, 'lng': 79.4080, 'zone_type': 'hospital', 'vulnerability_weight': 1.50},
    {'name': 'Andhra University High School & Campus Gate, Siripuram, Visakhapatnam', 'lat': 17.7290, 'lng': 83.3190, 'zone_type': 'school', 'vulnerability_weight': 1.35},
    {'name': 'ZP High School & St. Joseph College Zone, Arundelpet, Guntur', 'lat': 16.3060, 'lng': 80.4350, 'zone_type': 'school', 'vulnerability_weight': 1.35},
    {'name': 'NH-16 National Highway / Benz Circle Flyover, Vijayawada', 'lat': 16.4990, 'lng': 80.6540, 'zone_type': 'highway', 'vulnerability_weight': 1.30},
    {'name': 'Kanaka Durga Flyover Approach & Ghat Road, Vijayawada', 'lat': 16.5170, 'lng': 80.6130, 'zone_type': 'highway', 'vulnerability_weight': 1.30},
    {'name': 'Pandit Nehru Bus Station (PNBS) & Central Railway Station, Vijayawada', 'lat': 16.5080, 'lng': 80.6210, 'zone_type': 'transit_hub', 'vulnerability_weight': 1.25},
    {'name': 'Maddilapalem RTC Bus Complex & Jagadamba Junction, Visakhapatnam', 'lat': 17.7340, 'lng': 83.3240, 'zone_type': 'transit_hub', 'vulnerability_weight': 1.25},
    {'name': 'MVP Colony Sector 4, Visakhapatnam (GVMC)', 'lat': 17.7420, 'lng': 83.3370, 'zone_type': 'residential', 'vulnerability_weight': 1.00},
    {'name': 'Brodipet 4th Line, Guntur Municipal Corporation', 'lat': 16.3010, 'lng': 80.4410, 'zone_type': 'residential', 'vulnerability_weight': 1.00}
]

CIVIC_311_CORPUS = {
    'road': {
        'Critical': [
            "Massive road cave-in and 4-foot deep sinkhole on BT road outside {loc}! Two-wheelers falling and traffic completely jammed.",
            "Emergency: Flyover approach slab cracked and CC road collapsed at {loc}, high risk of fatal accidents!",
            "Deep dangerous trench across fast lane on NH-16 at {loc} left without barricades by contractor, multiple bikes crashed.",
            "Culvert slab collapsed on main R&B road near {loc}, emergency vehicles and ambulances completely blocked.",
            "Extreme crater on national highway bypass road at {loc}, multiple vehicle axle damage and fatal accident risk.",
            "Major road crater opened up after heavy rain at {loc}, cars getting stuck and bikes skidding into oncoming traffic."
        ],
        'High': [
            "Large deep crater pothole on main road at {loc} bursting car tires and causing severe two-wheeler skids.",
            "BT road completely damaged with sharp asphalt chunks sticking out near {loc}.",
            "Cast-iron manhole cover missing on main driving lane at {loc}, extreme accident risk at night.",
            "Unpainted broken speed breaker on {loc} causing heavy two-wheeler accidents.",
            "Series of dangerous potholes on busy junction road near {loc}, vehicles swerving into wrong lanes.",
            "Asphalt layer eroded down to foundation gravel on {loc}, dangerous slippery surface for riders."
        ],
        'Medium': [
            "Road surface is uneven with multiple moderate potholes on {loc}, resurfacing needed soon.",
            "Paver blocks on pedestrian footpath along {loc} are broken and loose.",
            "CC road divider has cracks and loose gravel scattered on {loc}.",
            "Potholes formed along the roadside shoulder near {loc} after recent heavy rains.",
            "Worn out tar road with patch work peeling off on {loc}.",
            "Depression in road surface near bus stop at {loc} causing vehicle jolts."
        ],
        'Low': [
            "Faint hairline surface cracks appearing on the newly laid CC road at {loc}.",
            "Road divider yellow and black paint has faded on {loc}, kindly repaint.",
            "Loose gravel on road shoulder near {loc}.",
            "Speed limit road sign is bent near {loc}.",
            "Minor roughness on pavement surface near {loc}."
        ]
    },
    'drainage': {
        'Critical': [
            "Black toxic drainage sewage water flooding into houses and shops at {loc}! Major health emergency!",
            "Open deep nala pit with no protective slab outside {loc}, school children could fall in and drown!",
            "Foul chemical-smelling nala overflow submerging the entire hospital road at {loc}.",
            "Main stormwater canal collapsed, black sewage water entering residential basements at {loc}."
        ],
        'High': [
            "Main drainage nala blocked with silt and plastic, knee-deep sewage water stagnating on the road at {loc}.",
            "Foul-smelling sewer water overflowing from open roadside gutters at {loc}.",
            "Heavy waterlogging across {loc} road after rain due to clogged municipal drains, knee-deep water.",
            "Drainage mori wall broken and dirty wastewater spilling onto pedestrian sidewalk at {loc}."
        ],
        'Medium': [
            "Roadside side-drain near {loc} is choked with plastic and garbage, de-silting needed before monsoon.",
            "Concrete drain cover slab cracked on {loc}, dangerous for pedestrians.",
            "Slow-draining water noticed along roadside gutters at {loc}, mosquito breeding hazard.",
            "Drain water stagnating in open ditch outside {loc}."
        ],
        'Low': [
            "Dry leaves clogging the storm drain grating slightly at {loc}.",
            "Drain inspection chamber lid is uneven with road level on {loc}.",
            "Requesting routine pre-monsoon cleaning of roadside gutter at {loc}.",
            "Faint sewer smell from drain vent at {loc}."
        ]
    },
    'water_supply': {
        'Critical': [
            "Main drinking water pipeline contaminated with black sewage water at {loc}! Residents falling sick with diarrhea!",
            "High-pressure CPWS water main pipeline burst at {loc}, clean water flooding road and eroding building foundation!",
            "Zero municipal water supply for 4 consecutive days in entire area {loc}, acute drinking water crisis.",
            "Contaminated foul-smelling yellow liquid coming out of municipal drinking water taps at {loc}."
        ],
        'High': [
            "Drinking water pipeline ruptured at {loc}, millions of liters of clean drinking water wasting onto street.",
            "No municipal tap water supply in {loc} for past 48 hours without any prior notice.",
            "Municipal tap water coming with brownish muddy color and unpleasant odor across {loc}.",
            "Very low water pressure in {loc}, unable to pump water to overhead storage tank (OHT)."
        ],
        'Medium': [
            "Underground municipal water valve leaking continuously onto road surface near {loc}.",
            "Municipal water supply timing is erratic and comes for only 20 minutes at {loc}.",
            "Public drinking water tap in park at {loc} is leaking continuously.",
            "Water pressure reduced over the past one week across {loc}."
        ],
        'Low': [
            "Public tap handle is slightly loose at {loc}.",
            "Requesting water meter inspection at {loc}.",
            "Water pipeline air valve whistling loudly near {loc}.",
            "Minor moisture seepage around municipal water valve box at {loc}."
        ]
    },
    'street_lights': {
        'Critical': [
            "Live high-voltage electric wire snapped from pole and lying across wet road at {loc}! Extreme electrocution danger!",
            "APEPDCL/APSPDCL street electric pole sparking intensely with loud explosion sparks falling on pedestrians at {loc}! ",
            "Street light pole tilted at 45 degrees, about to collapse onto moving traffic at {loc}!",
            "Underground streetlight cable box open and sparking in rain puddle near bus stop at {loc}!"
        ],
        'High': [
            "Complete blackout on busy 4-lane junction {loc}, all streetlights dark, high accident and crime zone.",
            "Entire street of 20 streetlights completely unlit at {loc} for three days in a row.",
            "Damaged street light pole with open wiring door within reach of children at {loc}.",
            "Pitch dark stretch on {loc} highway where multiple pedestrians were hit."
        ],
        'Medium': [
            "Two consecutive streetlights not working outside house near {loc}.",
            "Streetlight on {loc} keeps flickering constantly throughout the night.",
            "Street lights remain ON during daytime at {loc}, wasting electricity.",
            "LED light fixture cover broken on pole at {loc}."
        ],
        'Low': [
            "Street light LED bulb is dimmer compared to other lights on {loc}.",
            "Tree branches partially obstructing light beam from pole at {loc}.",
            "Streetlight pole sticker or poster needs cleaning at {loc}.",
            "Light timer turns ON 20 minutes late on {loc}."
        ]
    },
    'others': {
        'Critical': [
            "Huge ancient banyan tree fallen across road at {loc}, completely crushing vehicle and tearing electric lines!",
            "Hazardous toxic chemical waste dumped illegally near public hospital/school at {loc}!",
            "Commercial building wall under illegal construction cracked and about to collapse onto street at {loc}!",
            "Aggressive pack of stray dogs attacking school children and pedestrians near {loc}!"
        ],
        'High': [
            "Gigantic open rotting garbage mound on main road {loc}, unbearable stench and blocking traffic lane.",
            "Dead animal decomposing on pedestrian walkway near {loc} in summer heat, severe health hazard.",
            "Illegal encroachment blocking emergency ambulance fire lane completely at {loc}.",
            "Huge fallen tree branches blocking half the roadway at {loc} after cyclone/storm."
        ],
        'Medium': [
            "GVMC/VMC community dumper bin at {loc} overflowing onto pavement, not cleared for 3 days.",
            "Public park gate broken and plastic litter scattered all over {loc}.",
            "Loud illegal commercial loudspeaker noise after midnight at {loc}.",
            "Construction debris and gravel dumped on pedestrian sidewalk at {loc}."
        ],
        'Low': [
            "Public park bench is cracked at {loc}.",
            "Graffiti on public boundary wall near {loc}.",
            "Dry leaves swept into pile needs municipal pickup from {loc}.",
            "Stray cattle resting on road divider at {loc}."
        ]
    }
}

ZONE_KEYWORDS = {
    'hospital': ['hospital', 'emergency', 'ambulance', 'clinic', 'trauma', 'medical center', 'icu', 'casualty', 'kgh', 'ggh', 'ruia', 'svims', 'aiims'],
    'school': ['school', 'college', 'university', 'kindergarten', 'campus', 'institute', 'children', 'playground', 'andhra university', 'jntu'],
    'highway': ['highway', 'expressway', 'flyover', 'outer ring road', 'arterial', 'junction', 'bridge', 'bypass', 'nh-16', 'nh-65', 'nh-44', 'benz circle'],
    'transit_hub': ['metro station', 'railway', 'bus terminal', 'bus stand', 'airport', 'interchange', 'depot', 'rtc bus stand', 'apsrtc'],
    'residential': ['colony', 'apartment', 'enclave', 'gated community', 'sector', 'layout', 'street', 'cross', 'lane', 'residential']
}

BASE_SCORE_MAP = {
    'Critical': (85, 98),
    'High': (65, 84),
    'Medium': (40, 64),
    'Low': (15, 39)
}

def generate_dataset(n_samples: int = 5000) -> pd.DataFrame:
    rows = []
    prefixes = [
        "", "Urgent Citizen Alert: ", "Complaint regarding civic issue at ",
        "Emergency report: ", "Municipal grievance at ", "Please take notice: ",
        "Reporting severe problem at ", "Immediate civic attention required at "
    ]
    suffixes = [
        "", " Action needed immediately.", " Kindly resolve on priority.",
        " Highly dangerous situation.", " Requesting prompt inspection.",
        " Please dispatch team.", " Causing huge public inconvenience."
    ]

    for _ in range(n_samples):
        wing = random.choice(WINGS)
        prio = random.choice(PRIORITIES)
        loc = random.choice(BENCHMARK_LOCATIONS)
        template = random.choice(CIVIC_311_CORPUS[wing][prio])
        
        text = random.choice(prefixes) + template.format(loc=loc['name']) + random.choice(suffixes)
        score_min, score_max = BASE_SCORE_MAP[prio]
        base_score = random.uniform(score_min, score_max)
        mult = loc['vulnerability_weight']
        final_score = min(100.0, max(0.0, base_score * mult))
        
        if prio == 'Critical' and mult >= 1.3:
            final_score = max(final_score, 95.0)

        rows.append({
            'text': text,
            'wing': wing,
            'text_priority': prio,
            'base_score': round(base_score, 1),
            'final_priority_score': round(final_score, 1),
            'location_name': loc['name'],
            'zone_type': loc['zone_type'],
            'vulnerability_weight': mult
        })
    return pd.DataFrame(rows)

print("Synthesizing 5,000 comprehensive Indian municipal grievance records...")
df = generate_dataset(5000)

X = df['text']
y_wing = df['wing']
y_prio = df['text_priority']

X_train, X_test, y_w_train, y_w_test, y_p_train, y_p_test = train_test_split(
    X, y_wing, y_prio, test_size=0.15, random_state=SEED, stratify=y_wing
)

print(f"Dataset split: {len(X_train)} train, {len(X_test)} test.")

# Train Calibrated N-Gram Pipeline for Department Classification
wing_base = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 3), sublinear_tf=True, max_features=10000)),
    ('clf', LogisticRegression(random_state=SEED, max_iter=1500, C=3.0, class_weight='balanced'))
])
wing_calibrated = CalibratedClassifierCV(estimator=wing_base, cv=3)
wing_calibrated.fit(X_train, y_w_train)

y_w_pred = wing_calibrated.predict(X_test)
acc_wing = accuracy_score(y_w_test, y_w_pred)
print(f"\n=======================================================")
print(f"DEPARTMENT CLASSIFICATION TEST ACCURACY: {acc_wing * 100:.2f}%")
print(f"=======================================================")
print(classification_report(y_w_test, y_w_pred, digits=4))

# Train Priority Pipeline
prio_base = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 3), sublinear_tf=True, max_features=10000)),
    ('clf', LogisticRegression(random_state=SEED, max_iter=1500, C=3.0, class_weight='balanced'))
])
prio_calibrated = CalibratedClassifierCV(estimator=prio_base, cv=3)
prio_calibrated.fit(X_train, y_p_train)

y_p_pred = prio_calibrated.predict(X_test)
acc_prio = accuracy_score(y_p_test, y_p_pred)
print(f"\n=======================================================")
print(f"PRIORITY URGENCY TEST ACCURACY: {acc_prio * 100:.2f}%")
print(f"=======================================================")
print(classification_report(y_p_test, y_p_pred, digits=4))

# Package into project model directory
bundle = {
    'wing_pipeline': wing_calibrated,
    'prio_pipeline': prio_calibrated,
    'priority_pipeline': prio_calibrated,
    'departments': DEPARTMENTS,
    'zone_keywords': ZONE_KEYWORDS,
    'base_score_map': BASE_SCORE_MAP,
    'version': '3.0.0-production-ap-roads'
}

out_dir = os.path.join(os.path.dirname(__file__), "..", "models", "complaint_classifier")
os.makedirs(out_dir, exist_ok=True)

out_file1 = os.path.join(out_dir, "nexciv_multimodal_priority_model.pkl")
out_file2 = os.path.join(out_dir, "complaint_classifier.pkl")

joblib.dump(bundle, out_file1)
joblib.dump(bundle, out_file2)

print(f"\nSaved production models:")
print(f" - {out_file1} ({os.path.getsize(out_file1) / 1024:.2f} KB)")
print(f" - {out_file2} ({os.path.getsize(out_file2) / 1024:.2f} KB)")
print("Training complete successfully!")
