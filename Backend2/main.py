# main.py - Minimal version for testing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HealthTrack API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "HealthTrack API is working!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}