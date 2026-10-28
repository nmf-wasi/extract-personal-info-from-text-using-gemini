import os
from fastapi import FastAPI, HTTPException
from app.router import person

app = FastAPI()

app.include_router(person.router, prefix="/person", tags=["llm"])


@app.get("/")
def home():
    return {"author": "nmf_wasi"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not set")
    return {"status": "ready"}
