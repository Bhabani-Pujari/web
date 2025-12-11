# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

# Import database setup
from db import Base, engine
import models

# Import routers
from auth.router import router as auth_router
from doctors.router import router as doctor_router
from appointments.router import router as appointment_router

# ------------------------------
# Create all database tables
# ------------------------------
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database setup warning: {e}")

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="HealthTrack Clinic System")

# ------------------------------
# Validation Error Handler
# ------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"❌ Validation Error on {request.method} {request.url}")
    logging.error(f"❌ Errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        }
    )

# ------------------------------
# Enable CORS
# ------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Include Routers
# ------------------------------
app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(appointment_router)

# ------------------------------
# Root endpoint
# ------------------------------
@app.get("/")
def home():
    return {
        "message": "HealthTrack API Working!",
        "status": "live",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# ------------------------------
# For local development only
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)