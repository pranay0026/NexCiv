import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from classifier import ComplaintClassifier

def run_tests():
    clf = ComplaintClassifier()
    clf.load_model()
    
    test_cases = [
        {
            "tag": "Road - Residential",
            "text": "Potholes on road near our house with loose gravel",
            "loc": "MVP Colony, Visakhapatnam",
            "lat": 17.742, "lng": 83.337
        },
        {
            "tag": "Road - Highway / Critical",
            "text": "Massive road cave-in and 4-foot sinkhole on BT road outside Benz Circle Flyover",
            "loc": "Benz Circle Flyover, Vijayawada",
            "lat": 16.499, "lng": 80.654
        },
        {
            "tag": "Water Supply - Hospital Zone",
            "text": "Drinking water main pipeline burst and brown contaminated water near KGH casualty ward",
            "loc": "King George Hospital (KGH) Maharanipeta, Visakhapatnam",
            "lat": 17.7102, "lng": 83.3050
        },
        {
            "tag": "Drainage - Sewerage Overflow",
            "text": "Black toxic sewage water flooding from choked municipal nala onto main road",
            "loc": "Brodipet, Guntur",
            "lat": 16.301, "lng": 80.441
        },
        {
            "tag": "Electrical - High Danger",
            "text": "Live electric wire snapped from APEPDCL street pole sparking on wet road",
            "loc": "Near Bus Stand, Vijayawada",
            "lat": 16.508, "lng": 80.621
        },
        {
            "tag": "Sanitation - Solid Waste",
            "text": "Gigantic open rotting garbage mound dumped illegally on pedestrian walkway",
            "loc": "Arundelpet, Guntur",
            "lat": 16.306, "lng": 80.435
        }
    ]

    print("\n" + "="*80)
    print("NEXCIV AI COMPLAINT CLASSIFIER - VERIFICATION TEST SUITE")
    print("="*80)

    for tc in test_cases:
        res = clf.classify_complaint(
            text=tc["text"],
            location_address=tc["loc"],
            location_lat=tc["lat"],
            location_lng=tc["lng"]
        )
        print(f"\n[{tc['tag']}]")
        print(f"  Input Text:      \"{tc['text']}\"")
        print(f"  Location:        {tc['loc']} (Zone: {res['location_info']['zone_type']}, Mult: {res['location_info']['vulnerability_multiplier']}x)")
        print(f"  Dept Routed:     {res['department']} (code: {res['department_code']})")
        print(f"  Confidence:      {res['confidence']*100:.2f}%")
        print(f"  Priority:        {res['priority']} | Score: {res['priority_score']} / 100")
        print(f"  SLA Window:      {res['municipal_sla']}")
        print(f"  Head In Charge:  {res['department_head']}")

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)

if __name__ == "__main__":
    run_tests()
