import google.generativeai as genai
import logging
from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# Inisialisasi Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Menggunakan gemini-2.5-flash
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None
    logger.warning("GOOGLE_API_KEY is not configured in .env file.")

def ask_gemini(prompt: str):
    if not model:
        return "Gemini API Key is not configured. Please add it to your .env file."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f" Gemini API Error: {str(e)}")
        return "Maaf, terjadi kesalahan saat menghubungi asisten AI. Silakan coba lagi nanti."

