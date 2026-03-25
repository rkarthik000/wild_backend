"""
WildGuard AI — FastAPI Backend
Real-time wildlife threat detection & ranger alert system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from routers import detect, incidents, cameras, rangers, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛡  WildGuard AI Backend starting...")
    print(f"   Model: {settings.YOLO_MODEL}")
    print(f"   DB:    {settings.SUPABASE_URL or 'SQLite (local mode)'}")
    yield
    print("WildGuard shutting down.")


app = FastAPI(
    title="WildGuard AI",
    description="Real-time wildlife threat detection & ranger alert system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router,    prefix="/api/detect",    tags=["Detection"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(cameras.router,   prefix="/api/cameras",   tags=["Cameras"])
app.include_router(rangers.router,   prefix="/api/rangers",   tags=["Rangers"])
app.include_router(alerts.router,    prefix="/api/alerts",    tags=["Alerts"])


@app.get("/")
async def root():
    return {
        "service": "WildGuard AI",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
