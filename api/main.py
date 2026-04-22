from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import json

from sqlalchemy import text

from db.session import SessionLocal, engine, Base
import db.models # ensure models are registered

Base.metadata.create_all(bind=engine)

app = FastAPI()

#sync
from api.routes.sync import router as sync_router
from api.routes.academic import router as academic_router


app.include_router(sync_router, prefix="/sync", tags=["Sync"])

# ✅ REGISTER ROUTER DI SINI
app.include_router(academic_router, prefix="/academic", tags=["Academic"])

from api.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

from api.routes.ai import router as ai_router
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# Serving Frontend
import os
if not os.path.exists("frontend"):
    os.makedirs("frontend")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

from fastapi.responses import FileResponse
@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints are now handled by routers in api/routes/