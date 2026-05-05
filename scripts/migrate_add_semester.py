"""
Migration script: Tambah kolom semester ke tabel yang ada (PostgreSQL).

Jalankan script ini SATU KALI untuk mengupdate schema database yang sudah ada.
Script ini aman dijalankan berulang karena mengecek apakah kolom sudah ada.

Usage:
    python -m scripts.migrate_add_semester
"""
import logging
from sqlalchemy import text, inspect
from db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(inspector, table_name, column_name):
    """Cek apakah kolom sudah ada di tabel."""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def get_column_type(inspector, table_name, column_name):
    """Ambil tipe data kolom."""
    columns = inspector.get_columns(table_name)
    col = next((c for c in columns if c['name'] == column_name), None)
    return str(col['type']).upper() if col else None


def run_migration():
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Add User.current_semester (Integer, nullable)
        if not column_exists(inspector, "users", "current_semester"):
            conn.execute(text("ALTER TABLE users ADD COLUMN current_semester INTEGER"))
            logger.info("Added 'current_semester' column to 'users' table")
        else:
            logger.info("Column 'current_semester' already exists in 'users' table")
        
        # 2. Add Absen.semester (Integer, nullable)
        if not column_exists(inspector, "absensi", "semester"):
            conn.execute(text("ALTER TABLE absensi ADD COLUMN semester INTEGER"))
            logger.info("Added 'semester' column to 'absensi' table")
        else:
            logger.info("Column 'semester' already exists in 'absensi' table")
        
        # 3. Convert Pembayaran.semester dari String ke Integer (PostgreSQL)
        if column_exists(inspector, "pembayaran", "semester"):
            col_type = get_column_type(inspector, "pembayaran", "semester")
            
            if col_type and ('VARCHAR' in col_type or 'TEXT' in col_type or 'CHARACTER' in col_type):
                logger.info(f"Converting 'semester' column in 'pembayaran' from {col_type} to INTEGER...")
                
                # PostgreSQL: ALTER COLUMN TYPE dengan USING untuk konversi data
                conn.execute(text("""
                    ALTER TABLE pembayaran 
                    ALTER COLUMN semester TYPE INTEGER 
                    USING CASE 
                        WHEN LOWER(semester) = 'ganjil' THEN 1
                        WHEN LOWER(semester) = 'genap' THEN 2
                        WHEN semester ~ '^[0-9]+$' THEN semester::INTEGER
                        ELSE 0
                    END
                """))
                
                logger.info("Converted 'semester' column in 'pembayaran' to INTEGER")
            else:
                logger.info(f"Column 'semester' in 'pembayaran' is already {col_type}")
        
        conn.commit()
    
    logger.info("Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
