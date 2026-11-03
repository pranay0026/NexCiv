"""
NEX-CIV: Rigorous Multi-Task & Disaggregated Language Evaluation
Evaluates:
1. Overall Performance on Test Split (Accuracy, Macro F1, Precision, Recall)
2. Task 1: Department Classification (5 classes)
3. Task 2: Complaint Type Classification (20 classes)
4. Critical Experiment: Disaggregated Per-Language Evaluation:
   - Pure Telugu (te)
   - Pure English (en)
   - Romanized Telugu (te_latn)
5. Confusion Matrices for error diagnosis
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

def evaluate_nexciv_model(model_bundle_path: str, test_csv_path: str):
    print("=" * 70)
    print("🏛️ NEX-CIV RESEARCH EVALUATION: MULTI-TASK & DISAGGREGATED BENCHMARK")
    print("=" * 70)

    if not os.path.exists(model_bundle_path):
        raise FileNotFoundError(f"Model file not found: {model_bundle_path}")
    if not os.path.exists(test_csv_path):
        raise FileNotFoundError(f"Test CSV not found: {test_csv_path}")

    bundle = joblib.load(model_bundle_path)
    dept_pipe = bundle.get('wing_pipeline') or bundle.get('pipeline')
    type_pipe = bundle.get('complaint_type_pipeline')

    test_df = pd.read_csv(test_csv_path)
    print(f"Loaded Test Dataset: {len(test_df)} records")
    print("Language breakdown in test set:")
    print(test_df['language_style'].value_counts())

    # Overall Evaluation
    y_dept_true = test_df['department'].values
    y_type_true = test_df['complaint_type'].values

    dept_preds = dept_pipe.predict(test_df['complaint_text'])
    print("\n" + "=" * 60)
    print("TASK 1: DEPARTMENT CLASSIFICATION REPORT (OVERALL TEST SET)")
    print("=" * 60)
    print(classification_report(y_dept_true, dept_preds, digits=4, zero_division=0))

    if type_pipe:
        type_preds = type_pipe.predict(test_df['complaint_text'])
        print("\n" + "=" * 60)
        print("TASK 2: COMPLAINT TYPE CLASSIFICATION REPORT (OVERALL TEST SET)")
        print("=" * 60)
        print(classification_report(y_type_true, type_preds, digits=4, zero_division=0))

    # CRITICAL EXPERIMENT: DISAGGREGATED PER-LANGUAGE EVALUATION
    print("\n" + "=" * 70)
    print("🔬 CRITICAL EXPERIMENT: DISAGGREGATED LANGUAGE-WISE EVALUATION")
    print("=" * 70)
    print("Evaluates whether NexCiv independently understands Pure Telugu, English, and Romanized Telugu.")

    languages = ['te', 'en', 'te_latn']
    lang_names = {'te': 'Pure Telugu (తెలుగు)', 'en': 'Pure English', 'te_latn': 'Romanized Telugu (Tenglish)'}

    lang_results = []
    for lang in languages:
        sub_df = test_df[test_df['language_style'] == lang]
        if len(sub_df) == 0:
            continue

        sub_dept_preds = dept_pipe.predict(sub_df['complaint_text'])
        dept_acc = accuracy_score(sub_df['department'], sub_dept_preds)
        dept_f1 = f1_score(sub_df['department'], sub_dept_preds, average='macro', zero_division=0)

        if type_pipe:
            sub_type_preds = type_pipe.predict(sub_df['complaint_text'])
            type_acc = accuracy_score(sub_df['complaint_type'], sub_type_preds)
            type_f1 = f1_score(sub_df['complaint_type'], sub_type_preds, average='macro', zero_division=0)
        else:
            type_acc, type_f1 = 0.0, 0.0

        lang_results.append({
            'Language Style': lang_names[lang],
            'Samples': len(sub_df),
            'Dept Accuracy': f"{dept_acc*100:.1f}%",
            'Dept Macro F1': f"{dept_f1:.4f}",
            'Type Accuracy': f"{type_acc*100:.1f}%",
            'Type Macro F1': f"{type_f1:.4f}"
        })

    res_df = pd.DataFrame(lang_results)
    print("\n" + res_df.to_string(index=False))
    print("\n" + "=" * 70)
    return res_df


if __name__ == '__main__':
    model_p = os.path.join("models", "complaint_classifier", "complaint_classifier.pkl")
    test_p = os.path.join("ai", "datasets", "test.csv")
    evaluate_nexciv_model(model_p, test_p)
