import sys
from pathlib import Path

# Ensure backend directory is in sys.path so modules and routers import seamlessly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import complaints, classify, employees, auth
from classifier import get_classifier

app = FastAPI(title="NEXCIV API", version="2.0.0")

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

@app.on_event("startup")
async def startup_event():
    # Preload classifier model on startup
    get_classifier()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "NEXCIV API", "phase": "1 & 2 Live"}
