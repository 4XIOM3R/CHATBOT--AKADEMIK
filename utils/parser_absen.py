def parse_absen(rows):
    data = []

    for row in rows:
        cols = row.find_elements("tag name", "td")
        cols = [c.text.strip() for c in cols]

        if len(cols) < 6:
            continue

        pertemuan = {}

        for i in range(4, len(cols)):
            pertemuan[str(i - 3)] = cols[i]

        data.append({
            "mata_kuliah": cols[1],
            "sks": cols[2],
            "jadwal": cols[3],
            "pertemuan": pertemuan
        })

    return data