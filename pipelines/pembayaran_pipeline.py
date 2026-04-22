from db.session import SessionLocal
from db.models import Pembayaran


def run_pembayaran_pipeline(user_id: str, pembayaran_json: list[dict]):
    db = SessionLocal()

    try:
        # 🔥 hapus data lama
        db.query(Pembayaran).filter(Pembayaran.user_id == user_id).delete()

        for item in pembayaran_json:
            pembayaran = Pembayaran(
                user_id=user_id,
                jenis=item.get("jenis"),
                tahun_ajaran=item.get("tahun_ajaran"),
                semester=item.get("semester"),
                tagihan=item.get("tagihan")
            )


            db.add(pembayaran)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()