import os
import sys
import pandas as pd
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from duplicate_detection.configs.config import cfg
from duplicate_detection.structured_matching.classifier import StructuredIncidentClassifier

def main():
    train_path = cfg.PROCESSED_DATA_DIR / "train_pairs.csv"
    val_path = cfg.PROCESSED_DATA_DIR / "validation_pairs.csv"

    if not train_path.exists() or not val_path.exists():
        print(f"Error: Missing pair datasets at {train_path} or {val_path}")
        sys.exit(1)

    print(f"Loading training data: {train_path}")
    train_df = pd.read_csv(train_path)
    print(f"Loading validation data: {val_path}")
    val_df = pd.read_csv(val_path)

    classifier = StructuredIncidentClassifier()
    metrics = classifier.train(train_df, val_df)
    print("\nTraining completed successfully!")
    print(f"Validation F1 Score: {metrics['f1']:.4f}")
    print(f"Validation Precision: {metrics['precision']:.4f}")
    print(f"Validation Recall:    {metrics['recall']:.4f}")
    print(f"Validation AUC:       {metrics['auc']:.4f}")

if __name__ == "__main__":
    main()
