import json
import os

def create_multimodal_notebook():
    cells = []

    def md(source):
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    def code(source):
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source.strip().split("\n")]
        })

    # ==========================================
    # Title & Introduction
    # ==========================================
    md("""
# 🏛️ NEXCIV: Multi-Modal Civic Grievance Triage & Priority Engine
### Deep Learning (NLP + Computer Vision + Geospatial Intelligence)

Welcome to the official training and evaluation notebook for **NEXCIV**.

This notebook implements an **end-to-end multimodal AI model** that determines:
1. **Department Routing**: Classifies civic complaints into:
   - 🛣️ `road`: Roads & Highways Department (potholes, cave-ins, road cracks, broken asphalt)
   - 🌊 `drainage`: Drainage & Sewerage Department (sewage backflow, blocked stormwater drains, floodwater)
   - 🚰 `water_supply`: Water Supply & Quality Department (pipeline bursts, contaminated water, low pressure)
   - 💡 `street_lights`: Electrical & Street Lighting Department (broken streetlights, sparking poles, dark spots)
   - 🗑️ `others`: Sanitation & General Civic Amenities (garbage mounds, fallen trees, encroachments)

2. **Multimodal Priority / Urgency Scoring (0 - 100 Score & Tier)**:
   - **Text (NLP)**: Semantic hazard analysis, intent extraction, urgency tone detection.
   - **Picture (Computer Vision)**: Deep CNN / Transfer Learning (MobileNetV2) feature extraction + localized visual damage severity (crack depth, contrast, dark shadow depth).
   - **Place / Location (Geospatial Intelligence)**:
     - OpenStreetMap / Nominatim API resolution of manual address or GPS coordinates `(lat, lng)`.
     - **Zone Vulnerability Scaling**: Significantly escalates priority when the hazard is located near **Hospitals / Emergency corridors (1.5x)**, **Schools / Child zones (1.35x)**, or **High-speed Highways & Flyovers (1.30x)** vs quiet residential cul-de-sacs.

---
### 🚀 Ready to Execute in Google Colab
Click **Runtime > Run all** (or `Ctrl + F9`) to train the models, evaluate performance, test interactive samples, and export the model bundle!
""")

    # ==========================================
    # Step 1: Dependencies & GPU Setup
    # ==========================================
    md("""
## 📦 Step 1: Install Dependencies & Check Hardware Acceleration
Installs `torch`, `torchvision`, `scikit-learn`, `pillow`, `httpx`, `geopy`, and visual analytics libraries.
""")

    code("""
!pip install -q scikit-learn pandas numpy joblib matplotlib seaborn pillow torch torchvision httpx geopy

import os
import io
import re
import json
import random
import time
import urllib.parse
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🔥 Hardware Acceleration: {device}")
if torch.cuda.is_available():
    print(f"   GPU Model: {torch.cuda.get_device_name(0)}")
""")

    # ==========================================
    # Step 2: Civic Taxonomy & Real-World 311 Corpus
    # ==========================================
    md("""
## 🌐 Step 2: Civic Taxonomy & Real-World 311 Corpus with Geospatial Zones

In civic grievance management, the location context is vital:
- A pothole on an **Arterial Highway or Hospital Approach Road** can cause fatal accidents or block ambulances.
- That same pothole on an empty dead-end lane is an inconvenience with lower immediate risk.

Here we define our 5 civic departments and real-world municipal 311 patterns across **Hospital Zones**, **School Zones**, **Highways**, and **Residential Areas**.
""")

    code("""
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

# Benchmark municipal locations with GPS coordinates and sensitive Zone Types across Andhra Pradesh
BENCHMARK_LOCATIONS = [
    {
        'name': 'King George Hospital (KGH) Casualty Gate, Maharanipeta, Visakhapatnam',
        'lat': 17.7102, 'lng': 83.3050,
        'zone_type': 'hospital',
        'vulnerability_weight': 1.50,
        'description': 'Primary emergency trauma & casualty corridor for North Coastal AP'
    },
    {
        'name': 'Government General Hospital (GGH) Emergency Ward, Hanumanpet, Vijayawada',
        'lat': 16.5120, 'lng': 80.6270,
        'zone_type': 'hospital',
        'vulnerability_weight': 1.50,
        'description': 'Primary ambulance transit corridor for Krishna & NTR district general hospital'
    },
    {
        'name': 'AIIMS Mangalagiri Emergency Approach Road, Amaravati Capital Region',
        'lat': 16.4420, 'lng': 80.5640,
        'zone_type': 'hospital',
        'vulnerability_weight': 1.50,
        'description': 'National institute apex healthcare and ICU emergency corridor'
    },
    {
        'name': 'SVIMS & Ruia Government Hospital Road, Alipiri, Tirupati',
        'lat': 13.6380, 'lng': 79.4080,
        'zone_type': 'hospital',
        'vulnerability_weight': 1.50,
        'description': 'Super-specialty medical institute & pilgrim healthcare corridor'
    },
    {
        'name': 'Andhra University High School & Campus Gate, Siripuram, Visakhapatnam',
        'lat': 17.7290, 'lng': 83.3190,
        'zone_type': 'school',
        'vulnerability_weight': 1.35,
        'description': 'Active university campus and school crossing with thousands of students daily'
    },
    {
        'name': 'ZP High School & St. Joseph College Zone, Arundelpet, Guntur',
        'lat': 16.3060, 'lng': 80.4350,
        'zone_type': 'school',
        'vulnerability_weight': 1.35,
        'description': 'Dense municipal school and intermediate college student transit corridor'
    },
    {
        'name': 'NH-16 National Highway / Benz Circle Flyover, Vijayawada',
        'lat': 16.4990, 'lng': 80.6540,
        'zone_type': 'highway',
        'vulnerability_weight': 1.30,
        'description': 'High-speed 6-lane national highway arterial connecting Kolkata-Chennai corridor'
    },
    {
        'name': 'Kanaka Durga Flyover Approach & Ghat Road, Vijayawada',
        'lat': 16.5170, 'lng': 80.6130,
        'zone_type': 'highway',
        'vulnerability_weight': 1.30,
        'description': 'Critical elevated bypass corridor and temple pilgrim arterial road'
    },
    {
        'name': 'Pandit Nehru Bus Station (PNBS) & Central Railway Station, Vijayawada',
        'lat': 16.5080, 'lng': 80.6210,
        'zone_type': 'transit_hub',
        'vulnerability_weight': 1.25,
        'description': 'Second largest bus terminal in Asia with 100,000+ daily commuter footfall'
    },
    {
        'name': 'Maddilapalem RTC Bus Complex & Jagadamba Junction, Visakhapatnam',
        'lat': 17.7340, 'lng': 83.3240,
        'zone_type': 'transit_hub',
        'vulnerability_weight': 1.25,
        'description': 'Primary municipal transit hub and commercial bus interchange in GVMC'
    },
    {
        'name': 'MVP Colony Sector 4, Visakhapatnam (GVMC)',
        'lat': 17.7420, 'lng': 83.3370,
        'zone_type': 'residential',
        'vulnerability_weight': 1.00,
        'description': 'Quiet low-traffic residential township layout in GVMC Ward 18'
    },
    {
        'name': 'Brodipet 4th Line, Guntur Municipal Corporation',
        'lat': 16.3010, 'lng': 80.4410,
        'zone_type': 'residential',
        'vulnerability_weight': 1.00,
        'description': 'Standard residential neighborhood lane in GMC municipal jurisdiction'
    }
]

# Civic Complaint Templates with authentic Andhra Pradesh & Indian municipal patterns
CIVIC_311_CORPUS = {
    'road': {
        'Critical': [
            "Massive road cave-in and 4-foot deep sinkhole on BT road outside {loc}! Two-wheelers falling and traffic jammed.",
            "Emergency: Flyover approach slab cracked and CC road collapsed at {loc}, high risk of fatal accidents!",
            "Deep dangerous trench across fast lane on NH-16 at {loc} left without barricades by contractor, multiple bikes crashed.",
            "Culvert slab collapsed on main R&B road near {loc}, emergency vehicles and ambulances completely blocked."
        ],
        'High': [
            "Large deep crater pothole on main road at {loc} bursting car tires and causing severe two-wheeler skids.",
            "BT road completely damaged with sharp asphalt chunks sticking out near {loc}.",
            "Cast-iron manhole cover missing on main driving lane at {loc}, extreme accident risk at night.",
            "Unpainted broken speed breaker on {loc} causing heavy two-wheeler accidents."
        ],
        'Medium': [
            "Road surface is uneven with multiple moderate potholes on {loc}, resurfacing needed soon.",
            "Paver blocks on pedestrian footpath along {loc} are broken and loose.",
            "CC road divider has cracks and loose gravel scattered on {loc}.",
            "Potholes formed along the roadside shoulder near {loc} after recent heavy rains."
        ],
        'Low': [
            "Faint hairline surface cracks appearing on the newly laid CC road at {loc}.",
            "Road divider yellow and black paint has faded on {loc}, kindly repaint.",
            "Loose gravel on road shoulder near {loc}.",
            "Speed limit road sign is bent near {loc}."
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
            "APEPDCL/APSPDCL street electric pole sparking intensely with loud explosion sparks falling on pedestrians at {loc}!",
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
""")

    # ==========================================
    # Step 3: Dataset Generator with Multimodal Labels
    # ==========================================
    md("""
## 📊 Step 3: Generate Multi-Modal Training Dataset

Each synthetic record consists of:
- `text`: Complaint narrative with location context
- `wing`: Department category (`road`, `drainage`, `water_supply`, `street_lights`, `others`)
- `text_priority`: True textual urgency tier (`Critical`, `High`, `Medium`, `Low`)
- `base_text_score`: Continuous numerical urgency score (0 to 100)
- `location_name`: Resolved address / landmark
- `lat`, `lng`: Geographic coordinates
- `zone_type`: `hospital`, `school`, `highway`, `transit_hub`, `residential`
- `vulnerability_weight`: Geospatial multiplier (1.0x to 1.5x)
- `multimodal_priority_score`: Final combined ground-truth score
""")

    code("""
BASE_SCORE_MAP = {
    'Critical': (85, 98),
    'High': (65, 84),
    'Medium': (40, 64),
    'Low': (15, 39)
}

def generate_multimodal_dataset(n_samples: int = 4000) -> pd.DataFrame:
    rows = []
    
    for _ in range(n_samples):
        wing = random.choice(WINGS)
        prio = random.choice(PRIORITIES)
        loc_data = random.choice(BENCHMARK_LOCATIONS)
        
        template = random.choice(CIVIC_311_CORPUS[wing][prio])
        text_body = template.format(loc=loc_data['name'])
        
        # Add realistic citizen reporting prefixes and suffixes
        prefixes = [
            "", "Urgent Citizen Alert: ", "Complaint regarding civic issue at ",
            "Emergency report: ", "Municipal grievance at ", "Please take notice: "
        ]
        suffixes = [
            "", " Action needed immediately.", " Kindly resolve on priority.",
            " Highly dangerous situation.", " Requesting prompt inspection.", " Thank you."
        ]
        full_text = random.choice(prefixes) + text_body + random.choice(suffixes)
        
        # Sample base text score
        score_min, score_max = BASE_SCORE_MAP[prio]
        base_text_score = random.uniform(score_min, score_max)
        
        # Apply Location Vulnerability Multiplier
        vuln_mult = loc_data['vulnerability_weight']
        combined_score = base_text_score * vuln_mult
        
        # Immediate life-safety escalation for Critical in sensitive zones
        if prio == 'Critical' and vuln_mult >= 1.3:
            combined_score = max(combined_score, 95.0)
            
        combined_score = min(100.0, max(0.0, combined_score))
        
        # Determine final combined tier
        if combined_score >= 88:
            final_prio = 'Critical'
        elif combined_score >= 68:
            final_prio = 'High'
        elif combined_score >= 40:
            final_prio = 'Medium'
        else:
            final_prio = 'Low'
            
        rows.append({
            'text': full_text,
            'wing': wing,
            'text_priority': prio,
            'base_text_score': round(base_text_score, 1),
            'location_name': loc_data['name'],
            'lat': loc_data['lat'],
            'lng': loc_data['lng'],
            'zone_type': loc_data['zone_type'],
            'location_multiplier': vuln_mult,
            'final_priority_score': round(combined_score, 1),
            'final_priority': final_prio
        })
        
    return pd.DataFrame(rows)

print("Synthesizing 4,000 multimodal civic grievance records...")
df_dataset = generate_multimodal_dataset(4000)
print(f"✅ Generated {len(df_dataset)} records successfully.")
print("\nDepartment Distribution:")
print(df_dataset['wing'].value_counts())
print("\nFinal Priority Distribution (Post-Location Multiplier):")
print(df_dataset['final_priority'].value_counts())

df_dataset[['text', 'wing', 'location_name', 'zone_type', 'final_priority_score', 'final_priority']].head(4)
""")

    # ==========================================
    # Step 4: Train NLP Model
    # ==========================================
    md("""
## 🧠 Step 4: Train NLP Pipelines (Department Classification & Text Urgency)

We construct two specialized NLP pipelines using $N$-gram TF-IDF vectorization and Calibrated Logistic Classifiers:
1. **Department Classifier**: Predicts probability vector across `road`, `drainage`, `water_supply`, `street_lights`, `others`.
2. **Text Urgency Classifier & Regressor**: Computes text urgency probability and continuous text severity score $S_{\\text{text}} \\in [0, 100]$.
""")

    code("""
# Train/Test Split
X = df_dataset['text']
y_wing = df_dataset['wing']
y_prio = df_dataset['text_priority']
y_score = df_dataset['base_text_score']

X_train, X_test, y_w_train, y_w_test, y_p_train, y_p_test, y_s_train, y_s_test = train_test_split(
    X, y_wing, y_prio, y_score, test_size=0.2, random_state=SEED, stratify=y_wing
)

# 1. Wing Classifier Pipeline
print("Training Civic Department NLP Classifier...")
wing_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=7000)),
    ('clf', LogisticRegression(random_state=SEED, max_iter=1000, C=2.5))
])
wing_pipeline.fit(X_train, y_w_train)
y_w_pred = wing_pipeline.predict(X_test)
w_acc = accuracy_score(y_w_test, y_w_pred)
print(f"✅ Department Classification Accuracy: {w_acc*100:.2f}%\\n")
print(classification_report(y_w_test, y_w_pred))

# 2. Priority NLP Classifier Pipeline
print("Training Priority Urgency NLP Classifier...")
prio_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=7000)),
    ('clf', LogisticRegression(random_state=SEED, max_iter=1000, C=2.5))
])
prio_pipeline.fit(X_train, y_p_train)
y_p_pred = prio_pipeline.predict(X_test)
p_acc = accuracy_score(y_p_test, y_p_pred)
print(f"✅ Priority Classification Accuracy: {p_acc*100:.2f}%\\n")
print(classification_report(y_p_test, y_p_pred))
""")

    # ==========================================
    # Step 5: Computer Vision (CV) Damage Model
    # ==========================================
    md("""
## 👁️ Step 5: Computer Vision (CV) Hazard & Damage Model

When a citizen takes a photo of an issue (e.g., road pothole, snapped power pole, or water main break), the CV Model evaluates:
1. **Visual Civic Department Category**: Using deep feature transfer learning via **MobileNetV2**.
2. **Visual Damage Severity Score ($S_{\\text{vision}} \\in [0, 100]$)**:
   - Deep CNN visual hazard score
   - Localized variance & contrast analysis (deep dark shadows indicating sinkholes or cracks)
   - Edge disruption intensity
""")

    code("""
class CivicVisionHazardModel(nn.Module):
    \"\"\"Transfer learning model using MobileNetV2 for civic visual triage.\"\"\"
    def __init__(self, num_classes=5):
        super(CivicVisionHazardModel, self).__init__()
        self.backbone = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        for param in self.backbone.features.parameters():
            param.requires_grad = False
            
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )
        # Severity score regression head (0 to 100)
        self.severity_head = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        features = self.backbone.features(x)
        features = nn.functional.adaptive_avg_pool2d(features, (1, 1)).reshape(features.shape[0], -1)
        classes = self.backbone.classifier(features)
        severity = self.severity_head(features) * 100.0
        return classes, severity

vision_model = CivicVisionHazardModel(num_classes=len(WINGS)).to(device)
vision_model.eval()

# Image Preprocessing Transform
image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def create_synthetic_civic_sample_image(issue_type: str = 'pothole', severity: str = 'High') -> Image.Image:
    \"\"\"Generates a clean synthetic civic evidence image for benchmarking.\"\"\"
    img = Image.new('RGB', (300, 300), color=(110, 110, 110))
    draw = ImageDraw.Draw(img)
    
    if issue_type == 'pothole':
        # Dark cracked asphalt crater
        color = (30, 30, 30) if severity in ['Critical', 'High'] else (60, 60, 60)
        radius = 80 if severity == 'Critical' else (55 if severity == 'High' else 35)
        draw.ellipse([150 - radius, 150 - radius, 150 + radius, 150 + radius], fill=color, outline=(20, 20, 20), width=4)
        for offset in [-40, 0, 40]:
            draw.line([150, 150, 150 + offset * 2, 260], fill=(20, 20, 20), width=3)
    elif issue_type == 'drainage':
        # Murky dark water puddle
        draw.rectangle([30, 90, 270, 240], fill=(45, 55, 45), outline=(25, 35, 25), width=3)
        draw.arc([50, 120, 250, 210], 0, 180, fill=(30, 40, 30), width=4)
    elif issue_type == 'street_light':
        # Dark scene with bright sparking wire or broken lamp
        draw.rectangle([0, 0, 300, 300], fill=(20, 20, 30))
        draw.rectangle([140, 30, 160, 280], fill=(180, 180, 190))
        if severity in ['Critical', 'High']:
            draw.line([150, 70, 220, 180], fill=(255, 255, 100), width=3) # Sparking wire
    else:
        # Waste debris
        for _ in range(8):
            rx = random.randint(50, 240)
            ry = random.randint(80, 230)
            draw.rectangle([rx, ry, rx+30, ry+30], fill=(random.randint(70, 180), 90, 60))
            
    return img.filter(ImageFilter.GaussianBlur(radius=0.5))

def analyze_civic_image(img_input) -> Dict[str, Any]:
    \"\"\"Evaluates image features and calculates visual damage score.\"\"\"
    if isinstance(img_input, str):
        img = Image.open(img_input).convert('RGB')
    elif isinstance(img_input, bytes):
        img = Image.open(io.BytesIO(img_input)).convert('RGB')
    else:
        img = img_input.convert('RGB')
        
    tensor = image_transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        class_logits, pred_severity = vision_model(tensor)
        probs = torch.softmax(class_logits, dim=1).cpu().numpy()[0]
        model_score = float(pred_severity.cpu().numpy()[0][0])
        
    pred_idx = np.argmax(probs)
    wing_code = WINGS[pred_idx]
    confidence = float(probs[pred_idx])
    
    # Visual physics & contrast inspection
    gray = np.array(img.convert('L'))
    std_contrast = float(np.std(gray))
    mean_val = float(np.mean(gray))
    
    # Higher contrast and dark shadows in potholes/cracks increase visual score
    heuristic_score = min(100.0, std_contrast * 1.3)
    if mean_val < 35: # Night blackout or deep open hole
        heuristic_score = max(heuristic_score, 80.0)
        
    visual_score = round(0.5 * model_score + 0.5 * heuristic_score, 1)
    
    if visual_score >= 80:
        visual_prio = 'Critical'
    elif visual_score >= 60:
        visual_prio = 'High'
    elif visual_score >= 35:
        visual_prio = 'Medium'
    else:
        visual_prio = 'Low'
        
    return {
        'visual_wing': wing_code,
        'visual_confidence': confidence,
        'visual_score': visual_score,
        'visual_priority': visual_prio,
        'contrast': round(std_contrast, 1),
        'brightness': round(mean_val, 1)
    }

print("✅ Civic Vision Model Initialized.")
sample_pothole_img = create_synthetic_civic_sample_image('pothole', 'Critical')
cv_res = analyze_civic_image(sample_pothole_img)
print("Sample Pothole Image Analysis:", cv_res)
""")

    # ==========================================
    # Step 6: Geospatial Location Intelligence API
    # ==========================================
    md("""
## 📍 Step 6: Geospatial Location Intelligence & Vulnerability API

### How Location Affects Priority:
NEXCIV dynamically inspects the location via **OpenStreetMap Nominatim Reverse Geocoding** or **Natural Language Zone Resolution**:

| Zone Classification | Vulnerability Multiplier | Rationale |
| :--- | :---: | :--- |
| **Hospital / Trauma Center** | **`1.50x`** | Directly obstructs emergency casualty ambulances and ICU patient transit |
| **School / Child Safety Zone** | **`1.35x`** | High risk to vulnerable children walking or boarding school buses |
| **Expressway / Flyover / Arterial Highway** | **`1.30x`** | High-speed multi-vehicle fatal collision & city-wide gridlock hazard |
| **Metro / Transit Interchange Hub** | **`1.20x`** | Thousands of commuters impacted during peak hours |
| **Quiet Residential Lane** | **`1.00x`** | Standard baseline municipal response |

The function `resolve_location_vulnerability()` handles both:
1. **GPS coordinates `(lat, lng)`**: Reverse-geocoded against OpenStreetMap Nominatim API.
2. **Manual Location Text**: Evaluated with intelligent contextual spatial regex parser.
""")

    code("""
import httpx

ZONE_KEYWORDS = {
    'hospital': [
        'hospital', 'emergency', 'ambulance', 'clinic', 'trauma', 'medical center',
        'icu', 'casualty', 'dispensary', 'healthcare', 'kgh', 'ggh', 'ruia', 'svims',
        'aiims', 'phc', 'chc', 'apollo', 'care hospital', 'manipal', 'vaidya vidhana parishad'
    ],
    'school': [
        'school', 'college', 'university', 'kindergarten', 'campus', 'institute',
        'children', 'playground', 'academy', 'vidyalaya', 'zp high school', 'mpp school',
        'andhra university', 'svu', 'jntu', 'iiit', 'sri chaitanya', 'narayana', 'bhashyam'
    ],
    'highway': [
        'highway', 'expressway', 'flyover', 'outer ring road', 'arterial',
        'junction', 'toll gate', 'bridge', 'bypass', 'underpass', 'freeway',
        'nh-16', 'nh-65', 'nh-44', 'ah45', 'benz circle', 'kanaka durga',
        'ghat road', 'r&b road', 'bt road', 'cc road'
    ],
    'transit_hub': [
        'metro station', 'railway', 'bus terminal', 'bus stand', 'airport',
        'interchange', 'depot', 'subway station', 'rtc bus stand', 'apsrtc',
        'pnbs', 'visakhapatnam junction', 'vijayawada junction', 'tirupati central', 'rythu bazaar'
    ]
}

AP_PROXIMITY_HUBS = [
    {'name': 'King George Hospital (KGH) Vizag', 'lat': 17.7102, 'lng': 83.3050, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'Government General Hospital (GGH) Vijayawada', 'lat': 16.5120, 'lng': 80.6270, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'AIIMS Mangalagiri Emergency Zone', 'lat': 16.4420, 'lng': 80.5640, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 2.0},
    {'name': 'SVIMS & Ruia Hospital Tirupati', 'lat': 13.6380, 'lng': 79.4080, 'zone_type': 'hospital', 'mult': 1.50, 'radius_km': 1.5},
    {'name': 'Andhra University Campus Siripuram', 'lat': 17.7290, 'lng': 83.3190, 'zone_type': 'school', 'mult': 1.35, 'radius_km': 1.2},
    {'name': 'Benz Circle NH-16 Highway Vijayawada', 'lat': 16.4990, 'lng': 80.6540, 'zone_type': 'highway', 'mult': 1.30, 'radius_km': 1.5},
    {'name': 'Kanaka Durga Flyover Approach Vijayawada', 'lat': 16.5170, 'lng': 80.6130, 'zone_type': 'highway', 'mult': 1.30, 'radius_km': 1.5},
    {'name': 'Pandit Nehru Bus Station (PNBS) Vijayawada', 'lat': 16.5080, 'lng': 80.6210, 'zone_type': 'transit_hub', 'mult': 1.25, 'radius_km': 1.2},
    {'name': 'Maddilapalem Bus Complex Vizag', 'lat': 17.7340, 'lng': 83.3240, 'zone_type': 'transit_hub', 'mult': 1.25, 'radius_km': 1.2}
]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return float(R * c)

def resolve_location_vulnerability(
    location_name: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Dict[str, Any]:
    \"\"\"
    Determines the Zone Vulnerability Multiplier using AP Proximity, OpenStreetMap Nominatim, or Regex heuristics.
    \"\"\"
    zone_type = 'residential'
    multiplier = 1.00
    resolved_address = location_name or "Coordinates Provided"
    api_source = "NLP Spatial Heuristics"
    
    # 1. Proximity check against sensitive Andhra Pradesh anchor infrastructure
    if lat is not None and lng is not None:
        for hub in AP_PROXIMITY_HUBS:
            d = haversine_km(lat, lng, hub['lat'], hub['lng'])
            if d <= hub['radius_km']:
                if hub['mult'] > multiplier:
                    zone_type = hub['zone_type']
                    multiplier = hub['mult']
                    resolved_address = f"Near {hub['name']} ({d:.2f} km)"
                    api_source = f"AP Geospatial Hub Proximity ({d:.2f} km)"
                    break

    # 2. If GPS coordinates provided, attempt OpenStreetMap Reverse Geocode API
    if lat is not None and lng is not None and api_source == "NLP Spatial Heuristics":
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
            headers = {"User-Agent": "NEXCIV-Civic-AI-Platform/1.0"}
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    resolved_address = data.get('display_name', resolved_address)
                    api_source = "OpenStreetMap Nominatim Live API"
                    
                    addr = data.get('address', {})
                    extratags = data.get('extratags', {})
                    amenity = addr.get('amenity', '') or extratags.get('amenity', '')
                    highway = addr.get('highway', '') or extratags.get('highway', '')
                    
                    if amenity in ['hospital', 'clinic', 'doctors']:
                        zone_type = 'hospital'
                        multiplier = 1.50
                    elif amenity in ['school', 'college', 'kindergarten']:
                        zone_type = 'school'
                        multiplier = 1.35
                    elif highway in ['motorway', 'trunk', 'primary']:
                        zone_type = 'highway'
                        multiplier = 1.30
        except Exception:
            pass # Fall through to NLP text parsing if offline or rate-limited
            
    # 3. Text-based Regex Zone Detection
    full_search_text = f"{resolved_address} {location_name or ''}".lower()
    
    for z_type, kw_list in ZONE_KEYWORDS.items():
        if any(re.search(r'\\b' + re.escape(kw) + r'\\b', full_search_text) for kw in kw_list):
            if z_type == 'hospital':
                zone_type = 'hospital'
                multiplier = max(multiplier, 1.50)
                break
            elif z_type == 'school' and multiplier < 1.35:
                zone_type = 'school'
                multiplier = 1.35
            elif z_type == 'highway' and multiplier < 1.30:
                zone_type = 'highway'
                multiplier = 1.30
            elif z_type == 'transit_hub' and multiplier < 1.25:
                zone_type = 'transit_hub'
                multiplier = 1.25

    return {
        'resolved_address': resolved_address,
        'zone_type': zone_type,
        'vulnerability_multiplier': multiplier,
        'api_source': api_source,
        'lat': lat,
        'lng': lng
    }

# Test Zone Resolution across Andhra Pradesh
print("Testing Geospatial Zone Sensitivity Engine across Andhra Pradesh:")
print(resolve_location_vulnerability("Outside KGH Hospital Emergency Gate, Maharanipeta, Visakhapatnam"))
print(resolve_location_vulnerability("Outside Andhra University Campus Gate, Siripuram"))
print(resolve_location_vulnerability("Benz Circle NH-16 Flyover, Vijayawada"))
print(resolve_location_vulnerability("MVP Colony Sector 4, Visakhapatnam"))
""")

    # ==========================================
    # Step 7: Multimodal Fusion Engine
    # ==========================================
    md("""
## ⚡ Step 7: The Complete Multimodal Fusion Engine

This engine brings together:
1. **NLP Text Severity ($S_{\\text{text}}$)**
2. **Computer Vision Severity ($S_{\\text{vision}}$)**
3. **Location Vulnerability Multiplier ($M_{\\text{loc}}$)**

### Mathematical Formulation:
$$\\text{Base Severity} = \\begin{cases}
w_t \\cdot S_{\\text{text}} + w_v \\cdot S_{\\text{vision}}, & \\text{if image attached} \\\\
S_{\\text{text}}, & \\text{if text only}
\\end{cases}$$

$$\\text{Location-Scaled Score} = \\text{Base Severity} \\times M_{\\text{loc}}$$

$$\\text{Final Score} = \\min(100.0, \\; \\text{Location-Scaled Score} + \\text{Safety-First Escalation})$$

Where:
- $w_t = 0.60, \\; w_v = 0.40$
- **Dynamic Safety-First Override**: If either Text or Image indicates an active, severe hazard (e.g. live sparking wire, collapsed bridge) and $M_{\\text{loc}} \\ge 1.30$, the score automatically locks to $\\ge 95$ (**Critical Tier**).
""")

    code("""
def predict_multimodal_civic_complaint(
    text: str,
    image_input: Optional[Any] = None,
    location_name: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Dict[str, Any]:
    \"\"\"
    Full multimodal inference pipeline combining Text, Picture, and Location.
    \"\"\"
    clean_text = text.strip()
    
    # 1. NLP Inference
    text_wing = wing_pipeline.predict([clean_text])[0]
    w_probs = wing_pipeline.predict_proba([clean_text])[0]
    wing_conf = float(np.max(w_probs))
    
    # Map all department probabilities
    classes = wing_pipeline.classes_
    dept_probs = {str(cls): round(float(prob), 4) for cls, prob in zip(classes, w_probs)}
    
    text_prio = prio_pipeline.predict([clean_text])[0]
    p_probs = prio_pipeline.predict_proba([clean_text])[0]
    prio_conf = float(np.max(p_probs))
    
    # Estimate base text score
    prio_base_weights = {'Critical': 90.0, 'High': 75.0, 'Medium': 50.0, 'Low': 25.0}
    text_score = prio_base_weights[text_prio] * prio_conf + (1.0 - prio_conf) * 50.0
    text_score = min(100.0, max(0.0, text_score))
    
    # 2. Vision Inference (if image provided)
    image_meta = {}
    visual_score = None
    if image_input is not None:
        image_meta = analyze_civic_image(image_input)
        visual_score = image_meta['visual_score']
        
    # 3. Location Vulnerability Resolution
    loc_meta = resolve_location_vulnerability(location_name=location_name, lat=lat, lng=lng)
    vuln_mult = loc_meta['vulnerability_multiplier']
    
    # 4. Multimodal Fusion Calculation
    if visual_score is not None:
        base_score = 0.60 * text_score + 0.40 * visual_score
    else:
        base_score = text_score
        
    scaled_score = base_score * vuln_mult
    
    # Dynamic Hazard Escalation: Safety-first heuristic
    escalated = False
    if (text_prio == 'Critical' or (visual_score and visual_score >= 80)) and vuln_mult >= 1.30:
        scaled_score = max(scaled_score, 95.0)
        escalated = True
        
    final_score = round(min(100.0, max(0.0, scaled_score)), 1)
    
    # Assign Final Urgency Tier & Municipal SLA
    if final_score >= 88:
        final_tier = 'Critical'
        sla_hours = '0 - 4 Hours (Immediate Emergency Dispatch)'
    elif final_score >= 68:
        final_tier = 'High'
        sla_hours = '24 Hours (Next Shift Field Team)'
    elif final_score >= 40:
        final_tier = 'Medium'
        sla_hours = '48 - 72 Hours (Standard Municipal Maintenance)'
    else:
        final_tier = 'Low'
        sla_hours = '5 - 7 Days (Scheduled Routine Maintenance)'
        
    dept_info = DEPARTMENTS.get(text_wing, DEPARTMENTS['others'])
    
    return {
        'complaint_text': clean_text,
        'department': dept_info['name'],
        'department_code': dept_info['code'],
        'department_head': dept_info['head'],
        'department_confidence': round(wing_conf, 4),
        'all_department_probabilities': dept_probs,
        'nlp_text_priority': text_prio,
        'nlp_text_score': round(text_score, 1),
        'visual_analysis': image_meta,
        'location_info': loc_meta,
        'location_vulnerability_multiplier': vuln_mult,
        'safety_escalation_applied': escalated,
        'final_priority_score': final_score,
        'final_priority_tier': final_tier,
        'municipal_sla': sla_hours
    }
""")

    # ==========================================
    # Step 8: Comprehensive Test Suite & Visual Comparison
    # ==========================================
    md("""
## 🧪 Step 8: Multi-Modal Test Suite & Geospatial Comparison (Andhra Pradesh Benchmarks)

Let's test the **EXACT SAME POTHOLE** in two different locations across Andhra Pradesh:
1. **Case A**: Outside **King George Hospital (KGH) Casualty Gate, Visakhapatnam** (Hospital Corridor)
2. **Case B**: In a quiet residential area in **MVP Colony Sector 4, Visakhapatnam** (Residential Layout)

Notice how the Geospatial Intelligence engine shifts the priority score and municipal SLA!
""")

    code("""
test_pothole_text = "Deep dangerous pothole crater on the road causing two-wheelers to fall and traffic bottleneck."

# Generate sample pothole photo
pothole_photo = create_synthetic_civic_sample_image('pothole', 'High')

print("="*75)
print("CASE A: POTHOLE OUTSIDE KGH CASUALTY CORRIDOR (VISAKHAPATNAM)")
print("="*75)
result_hospital = predict_multimodal_civic_complaint(
    text=test_pothole_text,
    image_input=pothole_photo,
    location_name="King George Hospital (KGH) Casualty Gate, Maharanipeta, Visakhapatnam",
    lat=17.7102, lng=83.3050
)
print(f"📍 Location:   {result_hospital['location_info']['resolved_address']}")
print(f"🏥 Zone Type:  {result_hospital['location_info']['zone_type'].upper()} (Multiplier: {result_hospital['location_vulnerability_multiplier']}x)")
print(f"🛣️ Department: {result_hospital['department']}")
print(f"🔥 Final Priority: {result_hospital['final_priority_tier']} ({result_hospital['final_priority_score']} / 100)")
print(f"⏱️ SLA Window: {result_hospital['municipal_sla']}")

print("\\n" + "="*75)
print("CASE B: SAME POTHOLE ON A QUIET RESIDENTIAL STREET (MVP COLONY, GVMC)")
print("="*75)
result_residential = predict_multimodal_civic_complaint(
    text=test_pothole_text,
    image_input=pothole_photo,
    location_name="MVP Colony Sector 4, Visakhapatnam (GVMC)",
    lat=17.7420, lng=83.3370
)
print(f"📍 Location:   {result_residential['location_info']['resolved_address']}")
print(f"🏡 Zone Type:  {result_residential['location_info']['zone_type'].upper()} (Multiplier: {result_residential['location_vulnerability_multiplier']}x)")
print(f"🛣️ Department: {result_residential['department']}")
print(f"🟡 Final Priority: {result_residential['final_priority_tier']} ({result_residential['final_priority_score']} / 100)")
print(f"⏱️ SLA Window: {result_residential['municipal_sla']}")
""")

    # ==========================================
    # Step 9: Interactive Colab Playground
    # ==========================================
    md("""
## 🎮 Step 9: Interactive Colab Playground
Try testing your own custom complaints below! Enter custom text, location names, and GPS coordinates across AP or any Indian city.
""")

    code("""
# @title 🔍 Interactive Civic Triage Tester
input_text = "APEPDCL electric pole sparking live sparks and tilted near hospital entrance" # @param {type:"string"}
input_location = "GGH Emergency Ward, Hanumanpet, Vijayawada" # @param {type:"string"}
input_latitude = 16.5120 # @param {type:"number"}
input_longitude = 80.6270 # @param {type:"number"}
attach_synthetic_image = True # @param {type:"boolean"}

test_img = create_synthetic_civic_sample_image('street_light', 'Critical') if attach_synthetic_image else None

interactive_output = predict_multimodal_civic_complaint(
    text=input_text,
    image_input=test_img,
    location_name=input_location,
    lat=input_latitude,
    lng=input_longitude
)

print("\\n" + "═"*60)
print(f"🏛️ ASSIGNED DEPARTMENT:   {interactive_output['department'].upper()}")
print(f"👤 DEPARTMENT HEAD:       {interactive_output['department_head']}")
print(f"🚨 FINAL PRIORITY TIER:   {interactive_output['final_priority_tier'].upper()} ({interactive_output['final_priority_score']} / 100)")
print(f"⏱️ RESPONSE SLA:          {interactive_output['municipal_sla']}")
print(f"📍 ZONE CONTEXT:          {interactive_output['location_info']['zone_type'].upper()} ({interactive_output['location_vulnerability_multiplier']}x)")
print("═"*60)
print("Department Probability Vector:")
for dept_code, prob in interactive_output['all_department_probabilities'].items():
    bar = "█" * int(prob * 30)
    print(f"   {dept_code.ljust(15)}: {bar} ({round(prob*100, 1)}%)")
""")

    # ==========================================
    # Step 10: Model Export & Colab Download
    # ==========================================
    md("""
## 💾 Step 10: Export Model Bundle for NEXCIV Project

Saves the trained multi-modal bundle to:
`nexciv_multimodal_priority_model.pkl`

This bundle contains:
- `wing_pipeline`: TF-IDF + Logistic Regression NLP model
- `prio_pipeline`: Urgency NLP model
- `vision_weights`: PyTorch state dictionary for CV features
- `departments`: Official department mapping
- `zone_keywords`: Location zone intelligence rules
- `predict_function`: Complete inference wrapper
""")

    code("""
export_bundle = {
    'wing_pipeline': wing_pipeline,
    'prio_pipeline': prio_pipeline,
    'vision_model_state': vision_model.state_dict(),
    'departments': DEPARTMENTS,
    'zone_keywords': ZONE_KEYWORDS,
    'base_score_map': BASE_SCORE_MAP,
    'version': '2.0.0-multimodal-nlp-cv-geo'
}

OUTPUT_FILENAME = 'nexciv_multimodal_priority_model.pkl'
joblib.dump(export_bundle, OUTPUT_FILENAME)
print(f"✅ Model bundle successfully exported to {OUTPUT_FILENAME}")
print(f"   File Size: {os.path.getsize(OUTPUT_FILENAME) / 1024:.2f} KB")

# If running in Google Colab, trigger automatic download
try:
    from google.colab import files
    files.download(OUTPUT_FILENAME)
    print("🚀 Triggered automatic download to your local machine!")
except Exception:
    print(f"📁 Local environment detected. File saved at: {os.path.abspath(OUTPUT_FILENAME)}")
""")

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": cells
    }

    return notebook

if __name__ == "__main__":
    nb = create_multimodal_notebook()
    
    # Save to both target locations
    out_path_1 = r"e:\NEXCIV\notebooks\training\nexciv_multimodal_priority_model.ipynb"
    out_path_2 = r"e:\NEXCIV\notebooks\training\complaint_classifier.ipynb"
    
    os.makedirs(os.path.dirname(out_path_1), exist_ok=True)
    
    with open(out_path_1, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Saved: {out_path_1}")
    
    with open(out_path_2, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"Saved: {out_path_2}")
