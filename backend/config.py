import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory first, then fallback to current working directory
_backend_dir = Path(__file__).resolve().parent
_env_file = _backend_dir / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file)
load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../models/complaint_classifier/complaint_classifier.pkl")

settings = Settings()
