import os
import logging

from fastapi import FastAPI, Security, HTTPException, Depends, Body
from fastapi.security.api_key import APIKeyHeader
from models import LocationResponse, Coordinates
from gemini_client import extract_locations_from_text, setup_genai
from geocoder import get_coordinates
from dotenv import load_dotenv

# Load .env variables early
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Init app
app = FastAPI()

# Initialize Gemini API
setup_genai()

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.getenv("API_KEY"):
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate API key")

# --- RAW TEXT ENDPOINT ---
@app.post("/get-coordinates", response_model=LocationResponse)
async def get_location_coordinates(
    text: str = Body(..., media_type="text/plain"),
    api_key: str = Depends(get_api_key)
):
    logger.info("Received raw text body")
    try:
        locations = extract_locations_from_text(text)
        results = []
        missing = []
        for loc in locations:
            coords = await get_coordinates(loc)
            if coords:
                results.append(Coordinates(location_name=loc, latitude=coords[0], longitude=coords[1]))
            else:
                missing.append(loc)

        if missing:
            logger.info(f"Could not find coords for: {missing}")
        return LocationResponse(coordinates=results)

    except Exception:
        logger.exception("Error in get_location_coordinates")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
def read_root():
    return {"message": "API is up. Use POST /get-coordinates as text/plain."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
