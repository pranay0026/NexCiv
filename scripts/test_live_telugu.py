import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from backend.classifier import ComplaintClassifier

clf = ComplaintClassifier()
clf.load_model()

samples = [
    ("రోడ్డుపై పెద్ద గుంతలు పడ్డాయి వాహనాలు నడపడం చాలా కష్టంగా ఉంది ప్రమాదాలు జరుగుతున్నాయి", "road"),
    ("మురుగు కాలువ పొంగి రోడ్డుపై నల్లటి మురుగు నీరు ప్రవహిస్తోంది తీవ్ర దుర్వాసన భరించలేకపోతున్నాం", "drainage"),
    ("కుళాయిల్లో నల్లటి మురికి నీరు వస్తోంది తాగడానికి అసలు పనికి రావడం లేదు ప్రజలు అస్వస్థతకు గురవుతున్నారు", "water_supply"),
    ("మా కాలనీలో అన్ని వీధి దీపాలు వెలగడం లేదు రాత్రిపూట అంతా చిమ్మచీకటిగా ఉంది మహిళలు భయపడుతున్నారు", "street_lights"),
    ("రోడ్డు పక్కన చెత్త కుప్పలు పేరుకుపోయాయి పారిశుద్ధ్య కార్మికులు వారం రోజులుగా రాలేదు", "others")
]

print("LIVE PREDICTION TEST:")
for text, exp in samples:
    res = clf.classify_complaint(text=text)
    wing = res.get('wing')
    conf = res.get('confidence', 0)
    prio = res.get('priority')
    status = "MATCH" if wing == exp else "MISMATCH"
    print(f"[{status}] Expected: {exp:14} | Got: {wing:14} | Conf: {conf*100:5.1f}% | Priority: {prio}")
