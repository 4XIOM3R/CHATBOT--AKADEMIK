from fastapi import APIRouter, Depends
from api.deps import get_current_user
from services.gemini_service import ask_gemini
from services.academic_service import (
    get_khs_by_user,
    get_absen_by_user,
    get_pembayaran_by_user,
    get_ipk
)
from services.vector_service import search_vector_db
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def get_user_context_string(user_id: str):
    khs = get_khs_by_user(user_id)
    absen = get_absen_by_user(user_id)
    pembayaran = get_pembayaran_by_user(user_id)
    ipk = get_ipk(user_id)
    
    if not khs and not absen:
        return "Mahasiswa belum melakukan sinkronisasi data. Sarankan mahasiswa untuk menekan tombol 'Sinkronisasi Data' terlebih dahulu."

    context = "### DATA AKADEMIK PRIBADI MAHASISWA\n"
    context += f"- **IPK Terakhir:** {ipk}\n\n"
    
    context += "#### Kartu Hasil Studi (KHS):\n"
    for item in khs:
        context += f"- Smt {item['semester']}: {item['mata_kuliah']} ({item['kode']}) - SKS: {item['sks']}, Nilai: {item['nilai']}\n"
    
    context += "\n#### Presensi Kuliah:\n"
    for item in absen:
        context += f"- {item['mata_kuliah']}: Hadir {item['hadir']}, Izin {item['izin']}, Alpha {item['alpha']}\n"
    
    context += "\n#### Status Pembayaran:\n"
    total_tagihan = sum(p['tagihan'] for p in pembayaran)
    for p in pembayaran:
        context += f"- {p['jenis']} ({p['semester']}): Rp {p['tagihan']:,}\n"
    context += f"**Total Tagihan Belum Dibayar: Rp {total_tagihan:,}**\n"
    
    return context

@router.post("/chat")
def chat_with_ai(data: ChatRequest, user_id: str = Depends(get_current_user)):
    # 1. Ambil data personal dari SQL
    personal_context = get_user_context_string(user_id)
    
    # 2. Cari aturan akademik yang relevan dari Vector DB (PDF)
    rules_context_list = search_vector_db(data.message)
    rules_context = "\n".join(rules_context_list) if rules_context_list else "Tidak ada aturan spesifik yang ditemukan."
    
    system_prompt = f"""
    Anda adalah Asisten Akademik AI untuk mahasiswa UTY (Universitas Teknologi Yogyakarta).
    
    TUGAS ANDA:
    - Jawab pertanyaan mahasiswa dengan ramah dan profesional.
    - Gunakan DATA AKADEMIK PRIBADI jika pertanyaan terkait nilai/absen mahasiswa.
    - Gunakan PEDOMAN AKADEMIK KAMPUS jika pertanyaan terkait aturan, biaya, atau prosedur.
    - Jika jawaban tidak ada di data mana pun, sarankan mahasiswa untuk menghubungi bagian akademik.

    DATA AKADEMIK PRIBADI MAHASISWA:
    {personal_context}

    POTONGAN PEDOMAN AKADEMIK KAMPUS:
    {rules_context}

    PERTANYAAN MAHASISWA: {data.message}
    """
    
    answer = ask_gemini(system_prompt)
    return {"answer": answer}
