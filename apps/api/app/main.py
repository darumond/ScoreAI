from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import transcriptions

app = FastAPI(
    title="ScoreAI API",
    description="Convert YouTube links into piano sheet music.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcriptions.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
