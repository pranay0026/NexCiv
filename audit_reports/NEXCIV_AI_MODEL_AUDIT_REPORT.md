# NEXCIV AI Model Audit & Forensic Investigation Report

**Author:** Senior Machine Learning Engineer, NLP Researcher & AI Evaluation Specialist  
**System:** NexCiv Multilingual Civic Grievance Management System  
**Audit Date:** November 2026  
**Status:** Audit Completed — Baseline Defects Identified  

---

## Executive Summary

A comprehensive forensic audit of the AI/NLP models, training pipelines, datasets, and inference routing in the NexCiv civic grievance management system was conducted. The investigation revealed critical systemic issues:

1. **Target and Label Leakage in Classifier Data**: English municipal records synthesized from BBMP metadata injected the target label string directly into the complaint text (e.g., `"Citizen Grievance #21233532: Street Light Not Working issue reported on..."`), enabling trivial memorization rather than natural language understanding.
2. **Template Duplication & Split Contamination**: Telugu (`te`) and Romanized Telugu (`te_latn`) datasets consisted of only 7 and 2 template phrases per category respectively, duplicated hundreds of times across training, validation, and test splits (529 exact identical complaint texts shared between train and test sets, >35% contamination).
3. **Target Leakage in Priority Regression ($R^2 = 0.99998$)**: The reported near-perfect fit was an artifact of data leakage. The target `priority_score` was generated via a fixed linear formula and an emergency override ($95.0$ constant). The input features directly included `is_emergency` ($r = 0.959$) and the exact constituent formula terms (`safety_risk`, `infra_risk`, `sla_days`), reducing LightGBM to fitting a linear equation rather than genuine predictive triage.
4. **Hardcoded Rule-Based Inference Preemption**: In `backend/classifier.py`, regex keyword matching was executed before model invocation. Any match bypassed the machine learning model entirely with a hardcoded $0.98$ confidence score.
5. **Pair Leakage in Duplicate Detection**: In `test_pairs.csv`, over $71.5\%$ of the complaints appeared in `train_pairs.csv` due to random pair splitting rather than group/cluster splitting.
6. **Artifact Cross-Contamination**: Text classification pipeline bundles were saved under `nexciv_multimodal_priority_model.pkl` in `ai/src/train.py`, and scikit-learn version mismatches ($1.6.1$ pickled vs $1.9.1$ runtime) generated widespread deserialization warnings.

---

## 1. Forensic Inventory of Models and Pipelines

| Subsystem | Model Artifact / Script | Stated Algorithm | Actual Implementation & Defects |
| :--- | :--- | :--- | :--- |
| **Department Classifier** | `ai/models/nexciv_classifier/nexciv_multitask_baseline.pkl`<br>`models/complaint_classifier/complaint_classifier.pkl` | Sublinear TF-IDF + Logistic Regression / Linear SVM | Fitted on contaminated data; bypassed at runtime by regex; overwrites multimodal priority artifact |
| **Priority Engine** | `priority_engine/models/nexciv_lightgbm_priority_model.pkl`<br>`priority_engine/saved_models/nexciv_multimodal_unified_model.pkl` | LightGBM Regressor ($R^2 = 0.99998$, $\text{MAE} = 0.010$) | Trained on linear formula components + `is_emergency` target leak ($95.0$ constant); not genuine prediction |
| **Duplicate Detection** | `duplicate_detection/saved_models/incident_matching_lgbm.pkl`<br>`duplicate_detection/decision_engine/hybrid_engine.py` | 3-Layer Hybrid (BGE-M3 / MiniLM + Geospatial/Temporal + Cross-Encoder + GBDT) | $71.5\%$ text overlap between train and test pairs; zero false positive claim based on narrow synthetic slice |
| **Backend Inference** | `backend/classifier.py` | Multimodal singleton predictor | Regex `_analyze_multilingual_intent` fires first, assigns $0.98$ confidence and preempts ML pipeline |

---

## 2. Detailed Vulnerability Analysis

### 2.1. Complaint Classifier: Data Leakage & Contamination

1. **BBMP English Label Leakage**:
   In `scripts/build_10k_real_dataset.py` (lines 304–308):
   ```python
   complaint_text = f"Citizen Grievance #{cid}: {subcat} issue reported on {dt} at {ward}, {zone}."
   ```
   The `subcat` field contains strings like `"Street Light Not Working"`, `"water stagnation"`, `"Potholes"`. The model learns to match the literal department/category name embedded in the prompt.
2. **Template Duplication Across Splits**:
   The entire Romanized Telugu corpus was derived from 40 templates, and native Telugu from 140 templates. When randomly shuffled into 7,000 train / 1,500 val / 1,500 test:
   - Train unique texts: 3,486 out of 7,000.
   - Train & Test exact text overlap: 529 records.
   - Test set accuracy was evaluated on complaints already present in the training set.
3. **Inference Pipeline Bypass**:
   In `backend/classifier.py`:
   ```python
   intent = self._analyze_multilingual_intent(clean_text)
   if intent:
       wing = intent['wing']
       wing_confidence = 0.98
       ...
   elif self._bundle is not None:
       ...
   ```
   The machine learning model is never executed for any grievance matching common keywords.

### 2.2. Priority Prediction: Forensic Analysis of $R^2 = 0.99998$

1. **Formula Reproduction rather than Prediction**:
   In `scripts/generate_expert_dataset.py`, the target variable `priority_score` is computed as:
   $$\text{Score} = 0.25 \cdot \text{sev} + 0.20 \cdot \text{safety} + 0.15 \cdot \text{impact} + 0.20 \cdot \text{sla} + 0.10 \cdot \text{infra} + 0.10 \cdot \text{recurrence}$$
   with an emergency clamp:
   $$\text{if } \text{is\_emergency}: \text{Score} = 95.0$$
2. **Input Feature Leakage**:
   In `priority_engine/train_lightgbm_priority.py`, the feature matrix passed into LightGBM directly included:
   - `safety_risk`
   - `public_health_risk`
   - `infrastructure_criticality`
   - `statutory_sla_days`
   - `is_emergency` (Correlation with target: $r = 0.9592$)
   
   Every emergency record had `priority_score == 95.0` with standard deviation $0.000$. LightGBM isolated this branch at the first split, yielding an artificial $\text{RMSE} = 0.090$ and $R^2 = 0.99998$.
3. **Correct Architectural Separation**:
   - **Rule-Based Priority Calculation**: Transparent, deterministic municipal policy engine for administrative compliance (Section 3 Act No. 6 of 2018).
   - **Machine-Learning Priority Prediction**: Predicts expected triage level based on citizen grievance text, reported physical defect, and geographic metadata without leaking the target formula or emergency flags.
   - **Emergency Override**: Deterministic post-processing rule layer based on public safety statutory mandates.

### 2.3. Duplicate Detection: Pair Contamination & Zero False Positive Fallacy

1. **Complaint Overlap Across Splits**:
   In `test_pairs.csv` (1,737 pairs, 1,280 unique complaints), 915 complaints were also present in `train_pairs.csv`. A true evaluation requires **incident-cluster splitting** where entire geographic/temporal incidents are held out.
2. **False Positive Rate Realism**:
   Civic grievances in dense urban wards frequently describe similar issues (e.g. potholes on the same road 1 km apart, or water issues on adjacent streets). Claiming zero false positives on a synthetic 200-pair slice is misleading. Calibrated multi-tier decision boundaries ($>0.85$ auto-link, $0.65-0.85$ human review, $<0.65$ new incident) are required.

---

## 3. Retraining & Remediation Roadmap

1. **Curate Genuine Uncontaminated Multilingual Corpus**:
   - Build a comprehensive, diverse dataset of authentic civic complaints in English, Romanized Telugu, and Native Telugu script.
   - Strip synthetic label indicators (no category names in prompts).
   - Ensure diverse phrasing, informal dialects, typos, and boundary/compound complaints.
2. **Strict Group-Based Partitioning**:
   - Split 70% Train / 15% Validation / 15% Test strictly by source/incident/template cluster.
   - **Zero text or near-duplicate overlap** between splits.
   - Vectorizers and scalers fitted strictly on training data.
3. **Multi-Model Benchmark**:
   - Baseline A: Word/Char TF-IDF + Logistic Regression (C-tuned, balanced class weights).
   - Baseline B: Word/Char TF-IDF + Linear SVM (Calibrated SGD/Modified Huber).
   - Baseline C: Multilingual Pretrained Transformer / Indic Embeddings comparison.
   - Evaluate against the engineering target of $\approx 85\%$ generalization accuracy on unseen test data.
4. **Reformulate Priority Model**:
   - Train LightGBM priority predictor using strictly legitimate pre-incident features (NLP text embeddings, department, zone type, image proof presence) without target components or `is_emergency` flags.
   - Evaluate against a baseline regressor on genuinely unseen incidents.
5. **Benchmark Duplicate Engine**:
   - Re-evaluate on independent held-out incidents across genuine duplicates, cross-lingual duplicates, same-category different-location, and same-location different-issue cases.
6. **Backend Integration**:
   - Remove hardcoded preemption in `classifier.py`; use ML model predictions with proper confidence calibration.
   - Ensure graceful fallbacks and verify all existing FastAPI endpoints and pytest suites pass.
