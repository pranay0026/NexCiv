import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from duplicate_detection.decision_engine.hybrid_engine import get_decision_engine

engine = get_decision_engine()

complaint_a = {
    'description': 'Water pipe burst causing severe water shortage in Ram Nagar Ward 4',
    'category': 'water_supply',
    'department_code': 'water_supply',
    'complaint_type': 'no_water_supply',
    'location_lat': 16.7120,
    'location_lng': 81.0950,
    'ward': 'Ward 4',
    'location_address': 'Ram Nagar, Ward 4, Eluru',
    'created_at': '2026-10-15T09:00:00Z'
}

complaint_b = {
    'description': 'Heavy pipeline leakage, no drinking water in Ram Nagar street',
    'category': 'water_supply',
    'department_code': 'water_supply',
    'complaint_type': 'pipeline_leakage',
    'location_lat': 16.7121,
    'location_lng': 81.0951,
    'ward': 'Ward 4',
    'location_address': 'Ram Nagar, Ward 4, Eluru',
    'created_at': '2026-10-15T11:30:00Z'
}

complaint_c = {
    'description': 'Water pipe burst causing severe water shortage in Lakshmi Nagar Ward 18',
    'category': 'water_supply',
    'department_code': 'water_supply',
    'complaint_type': 'no_water_supply',
    'location_lat': 16.7620,
    'location_lng': 81.1450,
    'ward': 'Ward 18',
    'location_address': 'Lakshmi Nagar, Ward 18, Eluru',
    'created_at': '2026-10-15T09:00:00Z'
}

res_ab = engine.evaluate_pair(complaint_a, complaint_b, semantic_sim=0.78, cross_encoder_score=0.82)
print("--- COMPLAINT A vs COMPLAINT B (Same Incident: Ram Nagar) ---")
print("Composite Score:", res_ab['composite_score'])
print("Decision:       ", res_ab['decision'])
print("Distance:       ", res_ab['distance_meters'], "m")
print("Action:         ", res_ab['recommended_action'])
print("Reasons:        ", res_ab['reasons'])

res_ac = engine.evaluate_pair(complaint_a, complaint_c, semantic_sim=0.92, cross_encoder_score=0.94)
print("\n--- COMPLAINT A vs COMPLAINT C (Different Incidents: Ram Nagar vs Lakshmi Nagar) ---")
print("Composite Score:", res_ac['composite_score'])
print("Decision:       ", res_ac['decision'])
print("Distance:       ", res_ac['distance_meters'], "m")
print("Action:         ", res_ac['recommended_action'])
print("Reasons:        ", res_ac['reasons'])
