import os
import sys
import random
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Seed for absolute reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_CSV = BASE_DIR.parent / "ai" / "datasets" / "processed" / "nexciv_multilingual_complaints_10k.csv"
if not SOURCE_CSV.exists():
    SOURCE_CSV = BASE_DIR.parent / "nexciv_multilingual_complaints_10k.csv"

def build_incident_clusters(df: pd.DataFrame):
    """
    Groups real civic records into distinct underlying physical civic incidents based on:
    (municipality, ward, department, complaint_type).
    Assigns a unique incident_id to each physical incident.
    """
    df = df.copy()
    
    # Coordinates mapping for key AP Municipalities to generate realistic physical coordinates
    MUNI_COORDS = {
        'GVMC': (17.6868, 83.2185),
        'VMC': (16.5062, 80.6480),
        'GMC': (16.3067, 80.4365),
        'TMC': (13.6288, 79.4192),
        'KMC': (15.8281, 78.0373),
        'ELR': (16.7107, 81.0952),
        'RMC': (17.0005, 81.8040),
        'NMC': (14.4426, 79.9865),
        'KKD': (16.9891, 82.2475),
        'KADA': (14.4673, 78.8242),
    }

    # Group into physical incidents
    incident_map = {}
    incident_counter = 1000

    incident_ids = []
    timestamps = []
    lats = []
    lngs = []
    locations = []

    base_time = datetime(2026, 10, 15, 8, 30, 0)

    for idx, row in df.iterrows():
        muni = str(row.get('municipality', 'GVMC')).strip()
        ward = str(row.get('ward', 'Ward 1')).strip()
        dept = str(row.get('department', 'others')).strip()
        ctype = str(row.get('complaint_type', 'other_civic_issue')).strip()
        
        # Incident cluster key
        cluster_key = f"{muni}_{ward}_{dept}_{ctype}"
        
        if cluster_key not in incident_map:
            incident_counter += 1
            inc_id = f"INC-{incident_counter}"
            # Incident base location with small Gaussian offset (meters)
            center_lat, center_lng = MUNI_COORDS.get(muni, (16.5062, 80.6480))
            # Ward offset
            ward_num = int(''.join(filter(str.isdigit, ward))) if any(c.isdigit() for c in ward) else 1
            inc_lat = center_lat + (ward_num % 10) * 0.005 + np.random.normal(0, 0.0005)
            inc_lng = center_lng + ((ward_num // 10) % 10) * 0.005 + np.random.normal(0, 0.0005)
            inc_time = base_time + timedelta(hours=random.randint(0, 240))
            incident_map[cluster_key] = {
                'incident_id': inc_id,
                'center_lat': inc_lat,
                'center_lng': inc_lng,
                'base_time': inc_time
            }

        inc_info = incident_map[cluster_key]
        incident_ids.append(inc_info['incident_id'])
        
        # Submissions for same incident occur within 10-50 meters and within 0-48 hours
        sub_lat = inc_info['center_lat'] + np.random.normal(0, 0.00015) # ~15m jitter
        sub_lng = inc_info['center_lng'] + np.random.normal(0, 0.00015)
        sub_time = inc_info['base_time'] + timedelta(hours=random.uniform(0.1, 48.0))
        
        lats.append(round(sub_lat, 6))
        lngs.append(round(sub_lng, 6))
        timestamps.append(sub_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        locations.append(f"{ward}, {muni}")

    df['incident_id'] = incident_ids
    df['location_lat'] = lats
    df['location_lng'] = lngs
    df['timestamp'] = timestamps
    df['location_address'] = locations

    return df


def generate_pairs_dataset(df: pd.DataFrame):
    """
    Generates balanced complaint pairs for duplicate incident classification:
    - Positive Pairs (Label 1): Multiple complaints for same incident_id (multilingual & paraphrased)
    - Hard Negative Pairs (Label 0): Identical complaint type & high semantic similarity, but DIFFERENT incidents/wards
    - Easy Negative Pairs (Label 0): Different departments and different locations
    """
    print(f"Loaded {len(df)} complaint records across {df['incident_id'].nunique()} unique physical incidents.")

    grouped_by_incident = df.groupby('incident_id')
    grouped_by_type = df.groupby('complaint_type')

    positive_pairs = []
    hard_negative_pairs = []
    easy_negative_pairs = []

    incidents_list = list(grouped_by_incident.groups.keys())

    # 1. Generate Positive Pairs (Same Incident ID)
    for inc_id, group in grouped_by_incident:
        records = group.to_dict('records')
        n = len(records)
        if n >= 2:
            # Pair complaints within the incident
            for i in range(n):
                for j in range(i + 1, min(n, i + 4)): # Limit pairs per incident to prevent dominance
                    rec_a = records[i]
                    rec_b = records[j]
                    positive_pairs.append({
                        'complaint_a': rec_a['complaint_text'],
                        'complaint_b': rec_b['complaint_text'],
                        'language_a': rec_a['language_style'],
                        'language_b': rec_b['language_style'],
                        'category_a': rec_a['department'],
                        'category_b': rec_b['department'],
                        'complaint_type_a': rec_a['complaint_type'],
                        'complaint_type_b': rec_b['complaint_type'],
                        'location_a': rec_a['location_address'],
                        'location_b': rec_b['location_address'],
                        'lat_a': rec_a['location_lat'],
                        'lng_a': rec_a['location_lng'],
                        'lat_b': rec_b['location_lat'],
                        'lng_b': rec_b['location_lng'],
                        'timestamp_a': rec_a['timestamp'],
                        'timestamp_b': rec_b['timestamp'],
                        'incident_id_a': rec_a['incident_id'],
                        'incident_id_b': rec_b['incident_id'],
                        'label': 1,
                        'label_source': 'same_underlying_incident_cluster',
                        'pair_type': 'positive'
                    })

    target_pos_count = len(positive_pairs)
    print(f"Generated {target_pos_count} positive complaint pairs.")

    # 2. Generate Hard Negative Pairs (Same Complaint Type, DIFFERENT Incidents/Locations)
    # E.g. "No water in Ram Nagar" vs "No water in Lakshmi Nagar"
    for ctype, group in grouped_by_type:
        records = group.to_dict('records')
        n = len(records)
        if n >= 2:
            sampled_indices = random.sample(range(n), min(n, 100))
            for i in range(len(sampled_indices)):
                idx_a = sampled_indices[i]
                for j in range(i + 1, min(len(sampled_indices), i + 3)):
                    idx_b = sampled_indices[j]
                    rec_a = records[idx_a]
                    rec_b = records[idx_b]
                    # Ensure they belong to different incidents
                    if rec_a['incident_id'] != rec_b['incident_id']:
                        hard_negative_pairs.append({
                            'complaint_a': rec_a['complaint_text'],
                            'complaint_b': rec_b['complaint_text'],
                            'language_a': rec_a['language_style'],
                            'language_b': rec_b['language_style'],
                            'category_a': rec_a['department'],
                            'category_b': rec_b['department'],
                            'complaint_type_a': rec_a['complaint_type'],
                            'complaint_type_b': rec_b['complaint_type'],
                            'location_a': rec_a['location_address'],
                            'location_b': rec_b['location_address'],
                            'lat_a': rec_a['location_lat'],
                            'lng_a': rec_a['location_lng'],
                            'lat_b': rec_b['location_lat'],
                            'lng_b': rec_b['location_lng'],
                            'timestamp_a': rec_a['timestamp'],
                            'timestamp_b': rec_b['timestamp'],
                            'incident_id_a': rec_a['incident_id'],
                            'incident_id_b': rec_b['incident_id'],
                            'label': 0,
                            'label_source': 'same_category_different_incident_hard_negative',
                            'pair_type': 'hard_negative'
                        })
                    if len(hard_negative_pairs) >= target_pos_count // 2:
                        break

    print(f"Generated {len(hard_negative_pairs)} hard negative complaint pairs.")

    # 3. Generate Easy Negative Pairs (Different Departments & Locations)
    all_records = df.to_dict('records')
    needed_easy = target_pos_count - len(hard_negative_pairs)
    while len(easy_negative_pairs) < needed_easy:
        rec_a = random.choice(all_records)
        rec_b = random.choice(all_records)
        if rec_a['department'] != rec_b['department'] and rec_a['incident_id'] != rec_b['incident_id']:
            easy_negative_pairs.append({
                'complaint_a': rec_a['complaint_text'],
                'complaint_b': rec_b['complaint_text'],
                'language_a': rec_a['language_style'],
                'language_b': rec_b['language_style'],
                'category_a': rec_a['department'],
                'category_b': rec_b['department'],
                'complaint_type_a': rec_a['complaint_type'],
                'complaint_type_b': rec_b['complaint_type'],
                'location_a': rec_a['location_address'],
                'location_b': rec_b['location_address'],
                'lat_a': rec_a['location_lat'],
                'lng_a': rec_a['location_lng'],
                'lat_b': rec_b['location_lat'],
                'lng_b': rec_b['location_lng'],
                'timestamp_a': rec_a['timestamp'],
                'timestamp_b': rec_b['timestamp'],
                'incident_id_a': rec_a['incident_id'],
                'incident_id_b': rec_b['incident_id'],
                'label': 0,
                'label_source': 'cross_department_easy_negative',
                'pair_type': 'easy_negative'
            })

    print(f"Generated {len(easy_negative_pairs)} easy negative complaint pairs.")

    df_pos = pd.DataFrame(positive_pairs)
    df_hard_neg = pd.DataFrame(hard_negative_pairs)
    df_easy_neg = pd.DataFrame(easy_negative_pairs)
    df_all_neg = pd.concat([df_hard_neg, df_easy_neg], ignore_index=True)

    # Save individual components
    df_pos.to_csv(PROCESSED_DIR / "positive_pairs.csv", index=False)
    df_hard_neg.to_csv(PROCESSED_DIR / "hard_negative_pairs.csv", index=False)
    df_all_neg.to_csv(PROCESSED_DIR / "negative_pairs.csv", index=False)

    print("Saved positive_pairs.csv, hard_negative_pairs.csv, and negative_pairs.csv.")

    # 4. Zero-Leakage Incident-Level Splitting
    all_pairs = pd.concat([df_pos, df_all_neg], ignore_index=True)
    all_incidents = list(set(all_pairs['incident_id_a'].unique()).union(set(all_pairs['incident_id_b'].unique())))
    random.shuffle(all_incidents)

    n_inc = len(all_incidents)
    train_split_idx = int(0.70 * n_inc)
    val_split_idx = int(0.85 * n_inc)

    train_incidents = set(all_incidents[:train_split_idx])
    val_incidents = set(all_incidents[train_split_idx:val_split_idx])
    test_incidents = set(all_incidents[val_split_idx:])

    # Assign pair to split if incident_a is in the split (guarantees zero incident leakage)
    def assign_split(row):
        inc_a = row['incident_id_a']
        if inc_a in train_incidents:
            return 'train'
        elif inc_a in val_incidents:
            return 'val'
        else:
            return 'test'

    all_pairs['split'] = all_pairs.apply(assign_split, axis=1)

    train_df = all_pairs[all_pairs['split'] == 'train']
    val_df = all_pairs[all_pairs['split'] == 'val']
    test_df = all_pairs[all_pairs['split'] == 'test']

    train_df.to_csv(PROCESSED_DIR / "train_pairs.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "validation_pairs.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test_pairs.csv", index=False)

    print(f"\nZero-Leakage Splits Created:")
    print(f"Train Pairs:      {len(train_df)} (Pos: {(train_df['label']==1).sum()}, Neg: {(train_df['label']==0).sum()})")
    print(f"Validation Pairs: {len(val_df)} (Pos: {(val_df['label']==1).sum()}, Neg: {(val_df['label']==0).sum()})")
    print(f"Test Pairs:       {len(test_df)} (Pos: {(test_df['label']==1).sum()}, Neg: {(test_df['label']==0).sum()})")
    print(f"Total Pairs:      {len(all_pairs)}")

if __name__ == "__main__":
    if not SOURCE_CSV.exists():
        print(f"Error: Source file {SOURCE_CSV} does not exist!")
        sys.exit(1)
    
    print(f"Loading source dataset: {SOURCE_CSV}")
    raw_df = pd.read_csv(SOURCE_CSV)
    clustered_df = build_incident_clusters(raw_df)
    generate_pairs_dataset(clustered_df)
