import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:2005@localhost:5432/chatbot"
)

BASE_URL = os.getenv("BASE_URL", "https://sia.uty.ac.id")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 12))

if not SECRET_KEY:
    # Warning: Using a fallback key is not recommended for production
    SECRET_KEY = "temporary_secret_key_for_development_only"