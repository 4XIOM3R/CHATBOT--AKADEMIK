from services.vector_service import ingest_pdf
import os

if __name__ == "__main__":
    pdf_path = "data/Pedoman_Akademik.pdf"
    if os.path.exists(pdf_path):
        print(f"Menginisialisasi ingatan bot dari {pdf_path}...")
        ingest_pdf(pdf_path)
    else:
        print(f"File {pdf_path} tidak ditemukan. Silakan buat PDF-nya dulu.")
