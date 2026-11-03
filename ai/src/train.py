"""
NEX-CIV: Two-Task Multi-Output Training Pipeline
Trains models on:
- Task 1: Department (5 classes: road, drainage, water_supply, street_lights, others)
- Task 2: Complaint Type (20 specific civic categories)

Architectures:
1. Baselines: TF-IDF + Logistic Regression and Linear SVM (Multi-output)
2. Multilingual Deep Learning: XLM-RoBERTa / IndicBERT Shared Backbone with Dual Classification Heads
   Combined Loss: L = L_department + L_complaint_type
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Try PyTorch & HuggingFace for deep learning multi-task architecture
try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoModel, AutoConfig
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

SEED = 42

DEPARTMENTS = ['road', 'drainage', 'water_supply', 'street_lights', 'others']

COMPLAINT_TYPES = [
    'potholes', 'damaged_roads', 'footpath_damage', 'road_obstruction',
    'drainage_overflow', 'blocked_drainage', 'open_manhole', 'sewage_leakage',
    'no_water_supply', 'water_contamination', 'pipeline_leakage', 'low_water_pressure',
    'street_light_failure', 'damaged_electric_pole', 'exposed_electrical_wires',
    'garbage_accumulation', 'garbage_collection_failure', 'dead_animal_removal',
    'public_sanitation_issue', 'other_civic_issue'
]

# Complaint Type to Department Deterministic Mapping
TYPE_TO_DEPT = {
    'potholes': 'road',
    'damaged_roads': 'road',
    'footpath_damage': 'road',
    'road_obstruction': 'road',
    'drainage_overflow': 'drainage',
    'blocked_drainage': 'drainage',
    'open_manhole': 'drainage',
    'sewage_leakage': 'drainage',
    'no_water_supply': 'water_supply',
    'water_contamination': 'water_supply',
    'pipeline_leakage': 'water_supply',
    'low_water_pressure': 'water_supply',
    'street_light_failure': 'street_lights',
    'damaged_electric_pole': 'street_lights',
    'exposed_electrical_wires': 'street_lights',
    'garbage_accumulation': 'others',
    'garbage_collection_failure': 'others',
    'dead_animal_removal': 'others',
    'public_sanitation_issue': 'others',
    'other_civic_issue': 'others'
}

if HAS_TORCH:
    class NexCivMultiTaskTransformer(nn.Module):
        """
        Shared Multilingual Transformer Encoder (XLM-RoBERTa / IndicBERT)
        with Dual Classification Heads for:
        1. Department (5 classes)
        2. Complaint Type (20 classes)
        """
        def __init__(self, model_name: str = "FacebookAI/xlm-roberta-base", num_depts: int = 5, num_types: int = 20, dropout_rate: float = 0.2):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(model_name)
            hidden_size = self.encoder.config.hidden_size
            self.dropout = nn.Dropout(dropout_rate)

            # Head 1: Department Classifier
            self.dept_head = nn.Linear(hidden_size, num_depts)
            # Head 2: Complaint Type Classifier
            self.type_head = nn.Linear(hidden_size, num_types)

        def forward(self, input_ids, attention_mask=None):
            outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
            # Use pooler output or mean pooling across token representations
            if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
                pooled = outputs.pooler_output
            else:
                pooled = outputs.last_hidden_state[:, 0, :]
            
            pooled = self.dropout(pooled)
            dept_logits = self.dept_head(pooled)
            type_logits = self.type_head(pooled)
            return dept_logits, type_logits


def train_baseline_models(train_df: pd.DataFrame, val_df: pd.DataFrame):
    """
    Trains standard baseline multi-output pipelines:
    1. Sublinear TF-IDF Vectorizer
    2. Department Classifier (Logistic Regression & Linear SVM)
    3. Complaint Type Classifier (Logistic Regression & Linear SVM)
    """
    print("=" * 65)
    print("TRAINING BASELINE MULTI-TASK PIPELINES (TF-IDF + CLASSIFIERS)")
    print("=" * 65)

    X_train = train_df['complaint_text'].values
    y_dept_train = train_df['department'].values
    y_type_train = train_df['complaint_type'].values

    X_val = val_df['complaint_text'].values
    y_dept_val = val_df['department'].values
    y_type_val = val_df['complaint_type'].values

    # Shared Multilingual Vectorizer
    tfidf = TfidfVectorizer(
        token_pattern=r'(?u)\b\w+\b',
        ngram_range=(1, 3),
        max_features=15000,
        sublinear_tf=True
    )
    X_train_vec = tfidf.fit_transform(X_train)
    X_val_vec = tfidf.transform(X_val)

    # 1. Department Classifiers
    dept_lr = LogisticRegression(C=2.5, max_iter=1000, class_weight='balanced', random_state=SEED)
    dept_lr.fit(X_train_vec, y_dept_train)
    dept_preds = dept_lr.predict(X_val_vec)
    dept_acc = accuracy_score(y_dept_val, dept_preds)
    dept_f1 = f1_score(y_dept_val, dept_preds, average='macro')
    print(f"Task 1 [Department]     LR Validation Acc: {dept_acc*100:.2f}% | Macro F1: {dept_f1:.4f}")

    # 2. Complaint Type Classifiers
    type_lr = LogisticRegression(C=2.0, max_iter=1000, class_weight='balanced', random_state=SEED)
    type_lr.fit(X_train_vec, y_type_train)
    type_preds = type_lr.predict(X_val_vec)
    type_acc = accuracy_score(y_type_val, type_preds)
    type_f1 = f1_score(y_type_val, type_preds, average='macro')
    print(f"Task 2 [Complaint Type] LR Validation Acc: {type_acc*100:.2f}% | Macro F1: {type_f1:.4f}")

    # Build integrated Scikit-Learn pipelines
    dept_pipe = Pipeline([('tfidf', tfidf), ('clf', dept_lr)])
    type_pipe = Pipeline([('tfidf', tfidf), ('clf', type_lr)])

    bundle = {
        'wing_pipeline': dept_pipe,
        'pipeline': dept_pipe,
        'complaint_type_pipeline': type_pipe,
        'type_to_dept': TYPE_TO_DEPT,
        'departments': DEPARTMENTS,
        'complaint_types': COMPLAINT_TYPES,
        'model_version': '1.0.0-research-multitask',
        'metrics': {
            'department_accuracy': dept_acc,
            'department_macro_f1': dept_f1,
            'complaint_type_accuracy': type_acc,
            'complaint_type_macro_f1': type_f1
        }
    }

    # Save models
    os.makedirs(os.path.join("ai", "models", "nexciv_classifier"), exist_ok=True)
    os.makedirs(os.path.join("models", "complaint_classifier"), exist_ok=True)

    joblib.dump(bundle, os.path.join("ai", "models", "nexciv_classifier", "nexciv_multitask_baseline.pkl"))
    joblib.dump(bundle, os.path.join("models", "complaint_classifier", "complaint_classifier.pkl"))
    joblib.dump(bundle, os.path.join("models", "complaint_classifier", "nexciv_multimodal_priority_model.pkl"))
    joblib.dump(bundle, "complaint_classifier.pkl")

    print(f"\n✅ Exported Baseline Model Bundle to: 'ai/models/nexciv_classifier/nexciv_multitask_baseline.pkl'")
    print(f"✅ Exported Drop-in Replacement to: 'models/complaint_classifier/complaint_classifier.pkl'")
    return bundle


if __name__ == '__main__':
    train_csv = os.path.join("ai", "datasets", "train.csv")
    val_csv = os.path.join("ai", "datasets", "validation.csv")

    if not os.path.exists(train_csv) or not os.path.exists(val_csv):
        print("Dataset files not found in ai/datasets/. Running builder...")
        import subprocess
        subprocess.run([sys.executable, "scripts/build_nexciv_research_dataset.py"], check=True)

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    train_baseline_models(train_df, val_df)
