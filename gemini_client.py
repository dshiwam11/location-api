import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment or .env")

genai.configure(api_key=GOOGLE_API_KEY)

def extract_locations_from_text(text: str) -> list[str]:
    prompt = f"Extract all cities or location names mentioned in the following sentence:\n\n{text}\n\nGive output as a comma-separated list."

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    locations = response.text.strip().split(",")
    return [loc.strip() for loc in locations if loc.strip()]

