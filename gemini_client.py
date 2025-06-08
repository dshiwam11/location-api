import os
import json
import google.generativeai as genai
# from dotenv import load_dotenv

# Load environment variables from .env
# load_dotenv()

def setup_genai():
    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment or .env")
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        raise ValueError(f"Error setting up Gemini API: {e}")

def extract_locations_from_text(text: str) -> list[str]:
    prompt = f"""
You are a precise geographic‐entity extractor. 
From the following text, identify *all* place names—including cities, towns, villages, states/provinces, countries, regions, landmarks, neighborhoods, etc.—and return them as a JSON array of strings. Do *not* include any extra words, explanations, or formatting.

Text:
\"\"\"
{text}
\"\"\"
"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # parse the JSON array the model returns
    try:
        locations = json.loads(response.text)
    except ValueError:
        # fallback to comma-split if it didn't come back as valid JSON
        locations = response.text.strip().split(",")

    return [loc.strip() for loc in locations if loc.strip()]


