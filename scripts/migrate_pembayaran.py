import json
from sqlalchemy import create_engine, text
import os
os.environ["PGCLIENTENCODING"] = "utf8"

from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://postgres:2005@127.0.0.1:5432/academic_ai"
engine = create_engine(DATABASE_URL, echo=True)

USER_ID = "11111111-1111-1111-1111-111111111111"

def clean_rupiah(rp):
    return int(rp.replace("Rp.", "").replace(",", "").strip())

def migrate():
    print("START MIGRATION")

    with open("data/pembayaran.json") as f:
        data = json.load(f)

    with engine.connect() as conn:
        # pastikan user ada
        conn.execute(text("""
            INSERT INTO users (id, email)
            VALUES (:id, :email)
            ON CONFLICT DO NOTHING
        """), {
            "id": USER_ID,
            "email": "user@test.com"
        })

        for item in data["data"]:
            print("INSERT:", item)

            conn.execute(text("""
                INSERT INTO pembayaran (user_id, jenis, semester, amount, status)
                VALUES (:user_id, :jenis, :semester, :amount, :status)
            """), {
                "user_id": USER_ID,
                "jenis": item["jenis"],
                "semester": item["semester"],
                "amount": clean_rupiah(item["tagihan"]),
                "status": "unpaid"
            })

        conn.commit()

    print("DONE")

if __name__ == "__main__":
    migrate()