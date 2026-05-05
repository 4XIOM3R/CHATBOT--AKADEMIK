def convert_semester_to_int(semester_str, tahun_ajaran=None):
    """Convert semester string (Ganjil/Genap) ke integer.
    
    Logic:
    - Ganjil = semester ganjil (1, 3, 5, 7, ...)
    - Genap  = semester genap  (2, 4, 6, 8, ...)
    
    Jika tahun_ajaran tersedia (misal '2021/2022'), gunakan untuk menghitung
    semester relatif terhadap tahun masuk mahasiswa.
    Jika tidak, return 1 untuk Ganjil, 2 untuk Genap sebagai fallback.
    
    Args:
        semester_str: String semester ('Ganjil' atau 'Genap').
        tahun_ajaran: String tahun ajaran (misal '2024/2025').
    
    Returns:
        int: Semester sebagai integer. 0 jika tidak dikenali.
    """
    if isinstance(semester_str, int):
        return semester_str
    
    if not semester_str:
        return 0
    
    semester_lower = str(semester_str).strip().lower()
    
    if semester_lower == "ganjil":
        return 1
    elif semester_lower == "genap":
        return 2
    
    # Coba parse sebagai integer langsung
    try:
        return int(semester_str)
    except (ValueError, TypeError):
        return 0


def parse_pembayaran(rows):
    data = []
    total_tagihan = None

    for row in rows:
        cols = row.find_elements("tag name", "td")
        cols = [c.text.strip() for c in cols]

        if len(cols) < 4:
            continue

        # DETEKSI TOTAL (baris terakhir)
        if "Total Tagihan" in cols[2]:
            total_tagihan = cols[3]
            continue

        try:
            semester_int = convert_semester_to_int(cols[2], cols[1])
            
            data.append({
                "jenis": cols[0],
                "tahun_ajaran": cols[1],
                "semester": semester_int,
                "tagihan": cols[3]
            })
        except:
            continue

    return data, total_tagihan