"""
NEX-CIV LightGBM Grievance Priority Scoring & Triage Engine (Audited & Retrained)
Redirects to the leak-free, cluster-isolated priority training pipeline.
"""
from priority_engine.train_clean_priority import run_priority_training_and_evaluation

if __name__ == "__main__":
    run_priority_training_and_evaluation()
