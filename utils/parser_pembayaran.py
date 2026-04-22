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
            data.append({
                "jenis": cols[0],
                "tahun_ajaran": cols[1],
                "semester": cols[2],
                "tagihan": cols[3]
            })
        except:
            continue

    return data, total_tagihan