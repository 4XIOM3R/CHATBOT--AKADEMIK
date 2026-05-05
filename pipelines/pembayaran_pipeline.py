import logging
import re
from sqlalchemy.orm import Session
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

def run_pembayaran_pipeline(db: Session, user_id, pembayaran_json):
    try:
        db.query(Pembayaran).filter(Pembayaran.user_id == user_id).delete()

        for item in pembayaran_json:
            # Semester sudah di-convert ke integer oleh parser_pembayaran
            semester_val = item.get("semester", 0)
            if not isinstance(semester_val, int):
                try:
                    semester_val = int(semester_val)
                except (ValueError, TypeError):
                    semester_val = 0
            
            db.add(Pembayaran(
                user_id=user_id,
                jenis=item.get("jenis"),
                tahun_ajaran=item.get("tahun_ajaran"),
                semester=semester_val,
                tagihan=clean_tagihan(item.get("tagihan", 0)),
            ))

        logger.info(f"Pembayaran Pipeline success for user {user_id}")

    except Exception as e:
        logger.error(f"ERROR Pembayaran Pipeline: {str(e)}")
        raise
