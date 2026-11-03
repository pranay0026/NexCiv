import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ai.src.predict import NexCivPredictor

pred = NexCivPredictor()
pred.load_model('models/complaint_classifier/complaint_classifier.pkl')

tests = [
    "మా వీధిలో తాగునీరు రావడం లేదు",
    "There is no drinking water in our street",
    "Maa veedhilo drinking water ravatledu",
    "రోడ్డుపై పెద్ద గుంతలు పడ్డాయి నిన్న బైకర్లు పడిపోయారు",
    "మా కాలనీలో డ్రైనేజీ పొంగి నల్లటి మురుగు నీరు వస్తోంది",
    "Current pole bend ayindi road painaki eppudaina padachu replace urgently"
]

print("PREDICTION TEST ON TWO-TASK CLASSIFICATION:")
for t in tests:
    res = pred.predict(t)
    print(f"Input:  {res['text']}")
    print(f"Style:  {res['language_style']} | Dept: {res['department']['id']} ({res['department']['name']}) [{res['department']['confidence']*100:.1f}%]")
    print(f"Type:   {res['complaint_type']['id']} ({res['complaint_type']['name']}) [{res['complaint_type']['confidence']*100:.1f}%]")
    print("-" * 65)
