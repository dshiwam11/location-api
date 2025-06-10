import os
import json
import re
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
    content = response.text.strip()

    # 1) Find the first '[' and last ']' so we only grab the JSON array
    start = content.find('[')
    end = content.rfind(']')
    if start != -1 and end != -1 and end > start:
        json_part = content[start:end+1]
    else:
        json_part = content

    # 2) Remove any trailing commas before the closing bracket
    json_part = re.sub(r",\s*]", "]", json_part, flags=re.S)

    # 3) Try to parse clean JSON
    try:
        locations = json.loads(json_part)
    except json.JSONDecodeError:
        # Fallback: strip brackets/quotes and comma-split
        cleaned = json_part.strip("[] \n")
        locations = [loc.strip(" \"'") for loc in cleaned.split(",") if loc.strip()]

    # 4) Return a real list[str], not a print()
    return [loc for loc in locations if isinstance(loc, str) and loc.strip()]
