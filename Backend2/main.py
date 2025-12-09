# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine
import models
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import os   # ✅ ADD THIS
from fastapi.staticfiles import StaticFiles
from doctors.router import router as doctor_router


# Import routers
from auth.router import router as auth_router
from doctors.router import router as doctor_router
from appointments.router import router as appointment_router

# ------------------------------
# Create all database tables
# ------------------------------
Base.metadata.create_all(bind=engine)

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="HealthTrack Clinic System")

# ------------------------------
# Enable CORS for frontend integration
# ------------------------------
origins = [
    "http://localhost:5500",  # Live Server or HTML frontend
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://localhost:8080",      # ← ADD THIS
    "http://127.0.0.1:8080",# React/Vite dev server (optional)
    "*"                        # Allow all origins for testing (optional)
]



# In main.py, add this:
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import logging
    logging.error(f"❌ Validation Error on {request.method} {request.url}")
    logging.error(f"❌ Body: {await request.body()}")
    logging.error(f"❌ Errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(await request.body())
        }
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(appointment_router)

# Root endpoint
@app.get("/")
def home():
    return {"message": "HealthTrack API Working!"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "Frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# app.add_middleware(



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplify to just this
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
    return {"message": "HealthTrack API Working!"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "Frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    











# import os
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# from db import Base, engine
# import models

# # Routers
# from auth.router import router as auth_router
# from doctors.router import router as doctor_router
# from appointments.router import router as appointment_router

# # Database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="HealthTrack Clinic System")

# # CORS
# origins = [
#     "http://localhost:5500",
#     "http://127.0.0.1:5500",
#     "*"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Use Backend2 absolute path
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend"))

# print("Serving frontend from:", FRONTEND_DIR)

# # DO NOT OVERRIDE "/" — use "/static" instead
# app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# # Routers
# app.include_router(auth_router)
# app.include_router(doctor_router)
# app.include_router(appointment_router)

# @app.get("/")
# def home():
#     return {"message": "HealthTrack API Working!"}
