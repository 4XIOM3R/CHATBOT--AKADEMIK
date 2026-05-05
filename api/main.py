import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from db.session import engine, Base
from api.routes.sync import router as sync_router
from api.routes.academic import router as academic_router
from api.routes.auth import router as auth_router
from api.routes.ai import router as ai_router

# Inisialisasi database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot Akademik UTY API")

# Daftarkan Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(sync_router, prefix="/sync", tags=["Sync"])
app.include_router(academic_router, prefix="/academic", tags=["Academic"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# Melayani Frontend
if not os.path.exists("frontend"):
    os.makedirs("frontend")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")

