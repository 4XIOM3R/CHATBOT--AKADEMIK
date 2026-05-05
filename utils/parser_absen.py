import re


def extract_semester_from_page(driver):
    """Extract semester aktif dari halaman absen SIA.
    
    Mencari teks seperti 'Semester Ganjil 2024/2025' atau 'Semester Genap 2024/2025'
    di halaman, lalu menghitung semester ke-berapa mahasiswa saat ini.
    
    Returns:
        int or None: Nomor semester (misal: 1, 2, 3, dst.) atau None jika gagal.
    """
    try:
        page_text = driver.page_source
        
        # Cari pola "Semester Ganjil/Genap YYYY/YYYY"
        match = re.search(r'Semester\s+(Ganjil|Genap)\s+(\d{4})/(\d{4})', page_text, re.IGNORECASE)
        if match:
            jenis = match.group(1).lower()  # "ganjil" atau "genap"
            return jenis
    except Exception:
        pass
    
    return None


def parse_absen(rows, semester_info=None):
    """Parse baris tabel absensi dari SIA.
    
    Args:
        rows: Selenium WebElement rows dari tabel absen.
        semester_info: String jenis semester ('ganjil'/'genap') dari halaman SIA.
    
    Returns:
        list[dict]: Data absensi per mata kuliah.
    """
    data = []

    for row in rows:
        cols = row.find_elements("tag name", "td")
        cols = [c.text.strip() for c in cols]

        if len(cols) < 6:
            continue

        pertemuan = {}

        for i in range(4, len(cols)):
            pertemuan[str(i - 3)] = cols[i]

        item = {
            "mata_kuliah": cols[1],
            "sks": cols[2],
            "jadwal": cols[3],
            "pertemuan": pertemuan,
        }
        
        if semester_info:
            item["semester_info"] = semester_info
        
        data.append(item)

    return data