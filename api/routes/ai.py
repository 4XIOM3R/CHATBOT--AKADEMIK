from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from api.deps import get_current_user, get_db
from services.gemini_service import ask_gemini
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def get_user_context(db: Session, user_id: str):
    # Ambil KHS
    khs = db.execute(text("""
        SELECT c.name, k.semester, k.grade, k.total
        FROM khs k JOIN courses c ON k.course_id = c.id
        WHERE k.user_id = :user_id
    """), {"user_id": user_id}).fetchall()
    
    # Ambil Absen
    absen = db.execute(text("""
        SELECT c.name, a.hadir, a.izin, a.alpha
        FROM absensi a JOIN courses c ON a.course_id = c.id
        WHERE a.user_id = :user_id
    """), {"user_id": user_id}).fetchall()
    
    # Ambil Pembayaran
    pembayaran = db.execute(text("""
        SELECT jenis, semester, tagihan
        FROM pembayaran
        WHERE user_id = :user_id
    """), {"user_id": user_id}).fetchall()
    
    context = "Data Akademik Mahasiswa:\n"
    context += "- KHS: " + str([dict(row._mapping) for row in khs]) + "\n"
    context += "- Absen: " + str([dict(row._mapping) for row in absen]) + "\n"
    context += "- Pembayaran: " + str([dict(row._mapping) for row in pembayaran]) + "\n"
    
    return context

@router.post("/chat")
def chat_with_ai(data: ChatRequest, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    context = get_user_context(db, user_id)
    
    system_prompt = f"""
    Anda adalah Asisten Akademik AI untuk mahasiswa UTY (Universitas Teknologi Yogyakarta).
    Gunakan data akademik berikut untuk menjawab pertanyaan mahasiswa dengan ramah, informatif, dan profesional.
    Jika data tidak tersedia, informasikan dengan sopan.
    
    DATA AKADEMIK:
    {context}
    
    PERTANYAAN MAHASISWA: {data.message}
    """
    
    answer = ask_gemini(system_prompt)
    return {"answer": answer}

