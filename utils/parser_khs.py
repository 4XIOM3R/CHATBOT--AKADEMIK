def parse_khs(rows):
    data_khs = []
    total_sks = 0
    total_nilai = 0

    for row in rows:
        cols = row.find_elements("tag name", "td")
        cols = [c.text.strip() for c in cols]

        if len(cols) < 9:
            continue

        if not cols[3].isdigit():
            continue

        try:
            sks = int(cols[3])
            bobot = float(cols[7])
            total = float(cols[8])

            total_sks += sks
            total_nilai += total

            data_khs.append({
                "kode": cols[1],
                "mata_kuliah": cols[2],
                "sks": sks,
                "semester": cols[4],
                "nilai": cols[6],
                "bobot": bobot,
                "total": total
            })

        except:
            continue

    ipk = total_nilai / total_sks if total_sks > 0 else 0

    return data_khs, total_sks, round(ipk, 2)