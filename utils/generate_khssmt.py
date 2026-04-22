def generate_khssmt(khs_data):
    semester_map = {}

    for item in khs_data:
        smt = item["semester"]
        sks = item["sks"]
        total = item["total"]

        if smt not in semester_map:
            semester_map[smt] = {
                "sks": 0,
                "total": 0
            }

        semester_map[smt]["sks"] += sks
        semester_map[smt]["total"] += total

    result = []

    for smt, val in semester_map.items():
        ips = val["total"] / val["sks"] if val["sks"] > 0 else 0

        result.append({
            "semester": smt,
            "sks": val["sks"],
            "ips": round(ips, 2)
        })

    return sorted(result, key=lambda x: int(x["semester"]))