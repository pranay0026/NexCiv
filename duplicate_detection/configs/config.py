import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

class DuplicateDetectionConfig:
    # 1. Embedding Models (Layer 1)
    # Primary: BAAI/bge-m3 (Multilingual Dense + Sparse)
    PRIMARY_EMBEDDING_MODEL = os.getenv("PRIMARY_EMBEDDING_MODEL", "BAAI/bge-m3")
    BENCHMARK_EMBEDDING_MODEL = os.getenv("BENCHMARK_EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    LIGHTWEIGHT_EMBEDDING_MODEL = os.getenv("LIGHTWEIGHT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    FALLBACK_EMBEDDING_MODEL = os.getenv("FALLBACK_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    EMBEDDING_DIM = 1024  # bge-m3 / multilingual-e5 dimension (all-MiniLM is 384)
    TOP_K_CANDIDATES = int(os.getenv("TOP_K_CANDIDATES", "15"))

    # 2. Cross-Encoder Models (Layer 2)
    PRIMARY_CROSS_ENCODER = os.getenv("PRIMARY_CROSS_ENCODER", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    BENCHMARK_CROSS_ENCODER = os.getenv("BENCHMARK_CROSS_ENCODER", "BAAI/bge-reranker-v2-m3")
    FALLBACK_CROSS_ENCODER = os.getenv("FALLBACK_CROSS_ENCODER", "cross-encoder/ms-marco-MiniLM-L-6-v2")

    # 3. Decision Engine Weights (Layer 3 Fusion)
    # D = 0.45*S + 0.25*L + 0.15*C + 0.10*T + 0.05*I
    WEIGHT_SEMANTIC = float(os.getenv("WEIGHT_SEMANTIC", "0.45"))
    WEIGHT_LOCATION = float(os.getenv("WEIGHT_LOCATION", "0.25"))
    WEIGHT_CROSS_ENCODER = float(os.getenv("WEIGHT_CROSS_ENCODER", "0.15"))
    WEIGHT_TEMPORAL = float(os.getenv("WEIGHT_TEMPORAL", "0.10"))
    WEIGHT_IMAGE = float(os.getenv("WEIGHT_IMAGE", "0.05"))

    # 4. Calibration & Decision Thresholds
    THRESHOLD_HIGH_CONFIDENCE_DUPLICATE = float(os.getenv("THRESHOLD_HIGH_CONFIDENCE", "0.85"))
    THRESHOLD_HUMAN_REVIEW = float(os.getenv("THRESHOLD_HUMAN_REVIEW", "0.65"))

    # 5. Incident Spatio-Temporal Bounds
    MAX_DUPLICATE_DISTANCE_METERS = float(os.getenv("MAX_DUPLICATE_DISTANCE_METERS", "150.0"))
    IMMEDIATE_PROXIMITY_METERS = float(os.getenv("IMMEDIATE_PROXIMITY_METERS", "25.0"))
    MAX_TEMPORAL_WINDOW_HOURS = float(os.getenv("MAX_TEMPORAL_WINDOW_HOURS", "72.0")) # 3 days

    # 6. Storage & Paths
    DATASET_DIR = BASE_DIR / "datasets"
    SAVED_MODELS_DIR = BASE_DIR / "saved_models"
    PROCESSED_DATA_DIR = DATASET_DIR / "processed"
    RAW_DATA_DIR = DATASET_DIR / "raw"

    # Database Configuration (Supabase PostgreSQL / pgvector)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")

cfg = DuplicateDetectionConfig()
