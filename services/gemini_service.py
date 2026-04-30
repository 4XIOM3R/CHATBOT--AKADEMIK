import google.generativeai as genai
from config import GOOGLE_API_KEY

def ask_gemini(prompt: str):
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Gemini API Key is not configured. Please add it to your .env file."
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    response = model.generate_content(prompt)
    return response.text
