
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_current_user, get_db
from services.gemini_service import ask_gemini
from services.academic_service import (
    get_khs_by_user,
    get_absen_by_user,
    get_pembayaran_by_user,
    get_pembayaran_all_by_user,
    get_ipk,
    get_ips_per_semester,
    get_user_current_semester,
)
from services.vector_service import search_multiple_collections
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def get_user_context_string(db: Session, user_id: str):
    current_semester = get_user_current_semester(db, user_id)
    khs = get_khs_by_user(db, user_id)
    absen = get_absen_by_user(db, user_id)
    pembayaran = get_pembayaran_by_user(db, user_id)
    ipk = get_ipk(db, user_id)
    ips_data = get_ips_per_semester(db, user_id)
    
    if not khs and not absen:
        return "Mahasiswa belum melakukan sinkronisasi data. Sarankan mahasiswa untuk menekan tombol 'Sinkronisasi Data' terlebih dahulu agar saya bisa melihat nilai dan absennya."

    context = "DATA AKADEMIK PRIBADI MAHASISWA\n"
    context += f"- Semester Saat Ini: {current_semester}\n"
    context += f"- IPK Saat Ini: {ipk}\n"
    
    # IPS (Indeks Prestasi Semester)
    context += "\nRiwayat IPS per Semester:\n"
    for item in ips_data:
        context += f"- Semester {item['semester']}: IPS {item['ips']}\n"
    
    # KHS - Ambil 40 data terbaru
    context += "\nDetail Nilai Mata Kuliah (KHS):\n"
    recent_khs = sorted(khs, key=lambda x: (x['semester'], x['mata_kuliah']), reverse=True)[:40]
    for item in recent_khs:
        context += f"- Smt {item['semester']}: {item['mata_kuliah']} ({item['kode']}) -> Nilai: {item['nilai']} (Bobot: {item['bobot']})\n"
    
    if len(khs) > 40:
        context += f"(Terdapat {len(khs) - 40} data lama lainnya yang tidak ditampilkan)\n"
    
    # Presensi (filtered by current semester)
    context += f"\nKehadiran (Semester {current_semester} - Berjalan):\n"
    for item in absen:
        context += f"- {item['mata_kuliah']}: Hadir {item['hadir']}, Izin {item['izin']}, Alpha {item['alpha']}\n"
    
    # Pembayaran (filtered by current semester)
    semester_type = "Ganjil" if current_semester % 2 == 1 else "Genap"
    context += f"\nStatus Keuangan/Tagihan (Semester {semester_type}):\n"
    unpaid_pembayaran = [p for p in pembayaran if p['tagihan'] > 0]
    if not unpaid_pembayaran:
        context += "- Semua tagihan sudah lunas (LANCAR).\n"
    else:
        total_tagihan = sum(p['tagihan'] for p in unpaid_pembayaran)
        for p in unpaid_pembayaran:
            context += f"- {p['jenis']} ({p['tahun_ajaran']}): Rp {p['tagihan']:,}\n"
        context += f"Total Tunggakan: Rp {total_tagihan:,}\n"
    
    return context


@router.post("/ask")
def ask_knowledge_base(data: ChatRequest):
    """Public endpoint - akses knowledge base tanpa login (hanya knowledge umum, bukan data personal)."""
    try:
        rules_context_list = search_multiple_collections(data.message, collections=["pedoman_akademik"], n_results=6)
        rules_context = "\n".join(rules_context_list) if rules_context_list else "Tidak ada informasi spesifik yang ditemukan dalam knowledge base."
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"⚠️ Vector DB Search Error: {str(e)}")
        rules_context = "Maaf, saat ini saya tidak dapat mengakses knowledge base kampus."

    system_prompt = f"""
    Anda adalah Asisten Akademik AI untuk mahasiswa UTY (Universitas Teknologi Yogyakarta).
    Nama Anda adalah "SIA Assistant".

    GAYA BICARA:
    - Ramah, bersahabat, namun tetap sopan dan profesional.
    - Gunakan bahasa Indonesia yang natural (tidak terlalu kaku/robot).
    - Jawab secara JELAS dan INFORMATIF. Jika ada beberapa informasi relevan, sebutkan semuanya secara poin-poin.

    ATURAN JAWABAN:
    1. Gunakan POTONGAN PEDOMAN AKADEMIK KAMPUS untuk menjawab pertanyaan tentang aturan, prosedur, prestasi, atau biaya umum.
    2. JANGAN berikan informasi data pribadi mahasiswa (karena ini adalah akses public tanpa login).
    3. Jika pengguna bertanya tentang data pribadi (nilai, absen, tagihan), sarankan mereka login ke aplikasi dan gunakan fitur "Chat Pribadi".
    4. JANGAN mengarang data. Jika tidak tahu, katakan sejujurnya dengan cara yang sopan.
    5. JANGAN PERNAH MENGGUNAKAN SIMBOL BINTANG (**) ATAU FORMAT MARKDOWN BOLD/ITALIC dalam jawaban Anda. Gunakan teks polos saja.

    KNOWLEDGE BASE KAMPUS:
    {rules_context}

    PERTANYAAN: {data.message}
    """

    answer = ask_gemini(system_prompt)
    return {"answer": answer}


@router.post("/chat")
def chat_with_ai(data: ChatRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """Private endpoint - akses knowledge base + personal data (perlu login)."""
    # 1. Ambil data personal dari SQL
    personal_context = get_user_context_string(db, user_id)

    # 2. Cari aturan akademik yang relevan dari Vector DB (multiple collections)
    try:
        # Menambah n_results menjadi 6 agar mendapatkan konteks yang lebih luas
        rules_context_list = search_multiple_collections(data.message, n_results=6)
        rules_context = "\n".join(rules_context_list) if rules_context_list else "Tidak ada aturan spesifik yang ditemukan."
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"⚠️ Vector DB Search Error: {str(e)}")
        rules_context = "Maaf, saat ini saya tidak dapat mengakses knowledge base kampus."


    system_prompt = f"""
    Anda adalah Asisten Akademik AI cerdas untuk mahasiswa UTY (Universitas Teknologi Yogyakarta).
    Nama Anda adalah "SIA Assistant".

    GAYA BICARA:
    - Ramah, bersahabat, namun tetap sopan dan profesional.
    - Gunakan bahasa Indonesia yang natural (tidak terlalu kaku/robot).
    - Jawab secara JELAS dan INFORMATIF. Jika ada beberapa informasi relevan, sebutkan semuanya secara poin-poin.
    - Anda bisa memanggil mahasiswa dengan "Sobat" atau "Kak".

    ATURAN JAWABAN:
    1. Jawab pertanyaan berdasarkan DATA AKADEMIK PRIBADI yang disediakan jika ditanya soal nilai, absen, atau tagihan.
    2. Gunakan POTONGAN PEDOMAN AKADEMIK KAMPUS jika ditanya soal aturan, prosedur, prestasi, atau biaya umum.
    3. Jika mahasiswa bertanya tentang daftar prestasi, sebutkan semua prestasi yang ditemukan dalam data konteks.
    4. Jika data tidak lengkap atau tidak ditemukan, sarankan mahasiswa untuk melakukan 'Sinkronisasi Data' atau hubungi bagian akademik kampus.
    5. JANGAN mengarang data. Jika tidak tahu, katakan sejujurnya dengan cara yang sopan.
    6. JANGAN PERNAH MENGGUNAKAN SIMBOL BINTANG (**) ATAU FORMAT MARKDOWN BOLD/ITALIC dalam jawaban Anda. Gunakan teks polos saja.

    DATA AKADEMIK PRIBADI MAHASISWA:
    {personal_context}

    POTONGAN PEDOMAN AKADEMIK KAMPUS:
    {rules_context}

    PERTANYAAN MAHASISWA: {data.message}
    """

    answer = ask_gemini(system_prompt)
    return {"answer": answer}
