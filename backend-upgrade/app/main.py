from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.api.integration_hub import router as integration_router

app = FastAPI(title="AVENOR-AI Intelligence Cloud")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(integration_router, prefix="/api/v1/intelligence")

from app.api.main import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "Enterprise Ready"}

