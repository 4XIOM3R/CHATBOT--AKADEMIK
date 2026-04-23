import logging
import re
from db.session import SessionLocal
from db.models import Pembayaran

logger = logging.getLogger(__name__)

def clean_tagihan(tagihan_str):
    if isinstance(tagihan_str, (int, float)):
        return float(tagihan_str)
    if not tagihan_str:
        return 0.0
    # Remove 'Rp.', '.', and whitespace
    cleaned = re.sub(r'[^\d]', '', str(tagihan_str))
    return float(cleaned) if cleaned else 0.0

def run_pembayaran_pipeline(user_id, pembayaran_json):
    db = SessionLocal()

    try:
        db.query(Pembayaran).filter(Pembayaran.user_id == user_id).delete()

        for item in pembayaran_json:
            db.add(Pembayaran(
                user_id=user_id,
                jenis=item.get("jenis"),
                tahun_ajaran=item.get("tahun_ajaran"),
                semester=item.get("semester"),
                tagihan=clean_tagihan(item.get("tagihan", 0)),
            ))

        db.commit()
        logger.info(f"✅ Pembayaran Pipeline success for user {user_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ ERROR Pembayaran Pipeline: {str(e)}")
        raise

    finally:
        db.close()