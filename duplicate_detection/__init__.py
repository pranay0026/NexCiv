"""
NEX-CIV Multilingual & Multimodal Duplicate Complaint Detection Package.
Consists of:
- Layer 1: Dense Multilingual Semantic Retrieval (BGE-M3 / mE5)
- Layer 2: Cross-Encoder Incident Verification (BGE-Reranker-v2-m3)
- Layer 3: Structured Incident Matching & Decision Engine (Haversine + GBDT)
"""

__version__ = "1.0.0"
