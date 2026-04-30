from fpdf import FPDF
import os

def create_pedoman_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "PEDOMAN AKADEMIK UTY", ln=True, align="C")
    pdf.ln(10)
    
    text_content = """BAB II - KETENTUAN AKADEMIK
A. Biaya Kuliah
Mahasiswa wajib membayar:
- SPA (Sumbangan Pengembangan Akademik)
- SPP Tetap
- SPP Variabel (berdasarkan SKS)
- Biaya lain (praktikum, tugas akhir, dll)
Pembayaran:
- Dilakukan tiap semester
- Harus sesuai jadwal
- Bukti pembayaran wajib disimpan

B. Sistem Kredit Semester (SKS)
Sistem pembelajaran menggunakan SKS dengan ciri:
- Mahasiswa bebas memilih mata kuliah
- Beban studi diukur dalam SKS
- Ada batas maksimal SKS per semester
Ketentuan SKS berdasarkan IP:
- IP < 1.00 -> 15 SKS
- 1.00-1.49 -> 18 SKS
- 1.50-2.49 -> 20 SKS
- 2.50-3.49 -> 22 SKS
- 3.50-4.00 -> 24 SKS

C. Registrasi Mahasiswa
Mahasiswa wajib registrasi setiap semester
Termasuk pembayaran + KRS
Jika tidak registrasi -> dianggap cuti/tidak aktif

D. Kartu Rencana Studi (KRS)
Diisi setiap semester
Harus disetujui dosen pembimbing akademik
Mahasiswa yang tidak isi KRS -> tidak bisa ikut kuliah/ujian

E. Semester Antara
Untuk memperbaiki nilai / percepat studi
Maksimal:
- IP <= 2.50 -> 3 SKS
- 2.51-3.50 -> 6 SKS
- >= 3.51 -> 9 SKS

F. Tugas Akhir
Wajib untuk kelulusan
Dibimbing dosen
Harus mengikuti aturan ilmiah

G. Penilaian
Komponen nilai: Tugas, UTS, UAS
Syarat: Kehadiran minimal 75%
Skala nilai:
- A (81-100) -> Sangat Baik
- B (61-80) -> Baik
- C (41-60) -> Cukup
- D (21-40) -> Kurang
- E (<20) -> Gagal

H. Indeks Prestasi (IP & IPK)
IP = rata-rata nilai semester
IPK = rata-rata keseluruhan
Predikat:
- 2.00-2.75 -> Memuaskan
- 2.76-3.00 -> Memuaskan
- 3.01-3.50 -> Sangat Memuaskan
- 3.51-4.00 -> Pujian

I. Masa Studi
Maksimal studi: 7 tahun

J. Cuti Akademik
Harus izin resmi
Maksimal 1 semester (bisa diperpanjang)
Total cuti maksimal 3 semester

K. Tidak Registrasi
Tidak registrasi = dianggap tidak aktif
Bisa drop out jika terlalu lama

L. Wisuda
Dilakukan setelah semua syarat terpenuhi

BAB III - KEMAHASISWAAN
A. Status Mahasiswa
Aktif jika registrasi + KRS
Tidak aktif jika tidak melakukan registrasi

B. Perilaku Mahasiswa
Mahasiswa wajib:
- Menjaga etika
- Menjaga nama baik kampus
- Tidak melakukan pelanggaran

C. Kejujuran Akademik
Dilarang:
- Mencontek
- Plagiarisme
- Pemalsuan data
- Titip absen / joki

D. Tata Tertib
Berpakaian sopan
Hadir tepat waktu
Tidak merokok di kelas

E. Penampilan
Harus rapi dan sopan
Mengikuti aturan kampus

F. Poster / Informasi
Harus izin sebelum menyebarkan

G. Larangan
Termasuk: Kekerasan, Vandalisme, Pelanggaran hukum, Penyalahgunaan fasilitas

H. Kegiatan Mahasiswa
Harus izin kampus
Ada jadwal resmi

I. Organisasi
Bukan organisasi politik
Untuk pengembangan mahasiswa

J. Himbauan Berkendara
Gunakan helm
Patuhi aturan lalu lalu lintas

BAB IV - PROGRAM STUDI
Visi & Misi
Fokus pada: Teknologi, Pengembangan SDM, Penelitian & pengabdian

Program Studi Informatika
Fokus: Intelligent System, Software Engineering

Syarat Kelulusan
Mahasiswa dinyatakan lulus jika:
- TOEFL >= 450
- Minimal 144 SKS
- Lulus mata kuliah wajib
- Memiliki sertifikat kompetensi
- Lulus sidang akhir
"""
    
    pdf.set_font("Arial", "", 12)
    # Gunakan multi_cell untuk teks panjang
    pdf.multi_cell(0, 10, text_content)
    
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "Pedoman_Akademik.pdf")
    pdf.output(output_path)
    print(f"PDF created at: {output_path}")

if __name__ == "__main__":
    create_pedoman_pdf()
