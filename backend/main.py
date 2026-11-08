import sys
from pathlib import Path

# Ensure backend directory is in sys.path so modules and routers import seamlessly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from dotenv import load_dotenv
    env_file = backend_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    load_dotenv()
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import complaints, classify, employees, auth, ai, compliance, investigations, sla
from classifier import get_classifier

# Priority Engine & AI Task Router
try:
    from priority_engine.api.priority_api import router as priority_api_router
except Exception as e:
    print(f"Notice: Failed to import priority API router: {e}")
    priority_api_router = None

# Duplicate Detection & Master Incident Engine Integration
try:
    from duplicate_detection.api.routes import router as duplicate_router
except Exception as e:
    print(f"Notice: Failed to import duplicate detection router: {e}")
    duplicate_router = None

app = FastAPI(title="NEXCIV API", version="3.1.0")

@app.middleware("http")
async def normalize_path_middleware(request, call_next):
    if "//" in request.scope.get("path", ""):
        import re
        request.scope["path"] = re.sub(r"/+", "/", request.scope["path"])
        if "raw_path" in request.scope:
            request.scope["raw_path"] = request.scope["path"].encode("ascii")
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(classify.router)
app.include_router(employees.router)
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(compliance.router)
app.include_router(investigations.router)
app.include_router(sla.router)
if priority_api_router:
    app.include_router(priority_api_router)
if duplicate_router:
    app.include_router(duplicate_router)

@app.on_event("startup")
async def startup_event():
    # Preload classifier model on startup
    get_classifier()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "NEXCIV API", "phase": "Phase 1, 2 & 3 Active (AI Dispatch & CV Verification Live)"}

