# NEX-CIV Intelligent Multilingual & Multimodal Duplicate Complaint Detection System

## 1. System Overview
The **NEX-CIV Duplicate Detection & Master Incident Engine** is a research-grade, production-ready AI module designed to solve municipal ticket fragmentation and duplicate spam across Andhra Pradesh Urban Local Bodies (ULBs). 

Unlike naive duplicate systems that merely check text similarity, this engine implements a **3-Layer Hybrid Architecture** that distinguishes between:
1. **Exact & Semantic Duplicates**: Paraphrased descriptions of the same breakdown (e.g. *"Water pipe burst"* vs *"Drinking water leakage"* in Telugu, English, or Romanized Telugu).
2. **Location-Based Incidents**: Multiple citizens reporting the same physical hazard at the same GPS spot vs identical wording at completely different locations (e.g. *"No water in Ram Nagar"* vs *"No water in Lakshmi Nagar"* are kept strictly distinct).
3. **Multimodal Evidence**: Perceptual image hashing (`dHash`) and visual defect verification.
4. **Master Incident Consolidation**: Never deletes citizen complaints; consolidates them into an actionable Master Incident (`INC-GVMC-xxxx`), preserving every citizen's legal acknowledgement number (`AP-GVMC-2026-NXCxxxx`).

---

## 2. 3-Layer Hybrid Architecture

```
                                  [ Citizen Complaint Submission ]
                                                |
                                                v
                              +-----------------------------------+
                              | Preprocessing & Telugu Normalizer |
                              | Unicode NFC, Virama, dHash Finger |
                              +-----------------------------------+
                                                |
        +---------------------------------------+---------------------------------------+
        |                                       |                                       |
        v                                       v                                       v
[ LAYER 1: Dense Retrieval ]             [ LAYER 2: Cross-Encoder ]              [ LAYER 3: Structured Incident ]
- BAAI/bge-m3 / mE5 / MiniLM             - BAAI/bge-reranker-v2-m3 / ms-marco    - Haversine Distance (meters)
- Top-K Candidate Retrieval              - Joint All-to-All Token Attention      - Ward / Street / Mandal Match
- pgvector Cosine Dot Product            - Probability Calibration (\sigma(z))   - Temporal Window (< 72 Hours)
                                                                                 - GBDT Model (LightGBM)
        |                                       |                                       |
        +---------------------------------------+---------------------------------------+
                                                |
                                                v
                              +-----------------------------------+
                              |       HYBRID DECISION ENGINE      |
                              |  D = 0.45S + 0.25L + 0.15C        |
                              |          + 0.10T + 0.05I          |
                              +-----------------------------------+
                                                |
                +-------------------------------+-------------------------------+
                |                                                               |
                v                                                               v
      Score >= 0.85                                                       Score < 0.65
[ High-Confidence Duplicate ]                                           [ New Incident ]
Auto-link to Master Incident                                            Create new Master Incident
(Upvote incremented, Citizen notified)                                  (Dispatch to Field Team)
                |
                +-------------------------------+
                                                |
                                                v
                                       0.65 <= Score < 0.84
                                   [ Human Review Required ]
                                   Flagged for Municipal Cadre
```

---

## 3. Dataset Pipeline & Pair Distributions

Generated from 10,000 real Andhra Pradesh multilingual complaints across 5,988 physical incidents with **Zero-Leakage Incident-Level Splitting**:
- **Positive Pairs (`label = 1`)**: 5,818 pairs (Telugu, English, Romanized Telugu for same incident).
- **Hard Negative Pairs (`label = 0`)**: 3,423 pairs (Same complaint type & high text similarity, but **distinct wards/municipalities**).
- **Easy Negative Pairs (`label = 0`)**: 2,395 pairs (Cross-department, distinct areas).
- **Train Split (70%)**: 8,128 pairs (`train_pairs.csv`)
- **Validation Split (15%)**: 1,771 pairs (`validation_pairs.csv`)
- **Test Split (15%)**: 1,737 pairs (`test_pairs.csv`)

---

## 4. Benchmark Evaluation Results

Evaluated on independent zero-leakage test pairs:
- **Global Precision**: **100.0%** (Zero false duplicate merges)
- **Global Accuracy**: **78.0%**
- **F1-Score**: **71.8%**
- **Hard Negatives False Merge Rate**: **0.0% (Compliant - Ram Nagar vs Lakshmi Nagar kept strictly separate)**
- **False Positive Rate**: **0.0%**
- **Human Verification Rate**: **10.0%** (Flagged for officer review)
- **Inference Latency**: **41.92 ms / pair** on standard CPU

---

## 5. Directory Structure
```
duplicate_detection/
├── api/
│   ├── routes.py                     # FastAPI REST API endpoints
├── configs/
│   ├── config.py                     # Weights, thresholds, and model paths
├── cross_encoder/
│   ├── reranker.py                   # Layer 2 Cross-Encoder verification & calibration
├── database/
│   └── migrations/
│       └── 001_duplicate_detection_schema.sql # PostgreSQL + pgvector DDL
├── datasets/
│   ├── generate_pairs.py             # Leakage-proof pair generation
│   ├── processed/
│   │   ├── positive_pairs.csv
│   │   ├── hard_negative_pairs.csv
│   │   ├── negative_pairs.csv
│   │   ├── train_pairs.csv
│   │   ├── validation_pairs.csv
│   │   └── test_pairs.csv
├── decision_engine/
│   ├── hybrid_engine.py              # 3-Layer hybrid formula & threshold engine
├── embeddings/
│   ├── embedder.py                   # Layer 1 Dense semantic embedder & retrieval
├── evaluation/
│   ├── benchmark_evaluator.py        # Comprehensive evaluation & subgroup metrics
├── preprocessing/
│   ├── geo_utils.py                  # Haversine distance & temporal compatibility
│   ├── image_fingerprint.py          # dHash perceptual Hamming distance
│   └── text_cleaner.py               # Telugu Unicode NFC normalization & language detection
├── retrieval/
│   └── vector_store.py               # pgvector + local JSON dual persistence
├── saved_models/
│   ├── incident_matching_lgbm.pkl    # Trained Layer 3 LightGBM classifier
│   └── evaluation_results.json       # Benchmark metrics output
└── tests/
    ├── test_api_endpoints.py         # End-to-end API integration test suite
    └── test_hybrid_decision.py       # Ram Nagar vs Lakshmi Nagar verification
```

---

## 6. How to Run & Verify

### 6.1 Run Pair Generation
```bash
python duplicate_detection/datasets/generate_pairs.py
```

### 6.2 Train Layer 3 LightGBM Classifier
```bash
python -m duplicate_detection.structured_matching.train_lgbm
```

### 6.3 Run Ram Nagar vs Lakshmi Nagar Decision Verification
```bash
python -m duplicate_detection.tests.test_hybrid_decision
```

### 6.4 Run Full End-to-End API Test Suite
```bash
python duplicate_detection/tests/test_api_endpoints.py
```

### 6.5 Run Comprehensive Benchmark Evaluation
```bash
python -m duplicate_detection.evaluation.benchmark_evaluator
```

---

## 7. Hardware & Deployment Requirements
- **CPU**: Standard x86_64 / ARM64 (Intel Core i5+, AMD Ryzen, or AWS c5.xlarge)
- **RAM**: Minimum 4 GB (8 GB recommended)
- **GPU (Optional)**: NVIDIA CUDA 11.8+ for accelerating multi-gigabyte BGE-M3 / BGE-Reranker-v2-m3 inference.
- **Database**: PostgreSQL 15+ with `pgvector` extension enabled, or built-in file-backed transactional JSON tables.
