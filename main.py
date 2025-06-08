from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from models import LocationRequest, LocationResponse, Coordinates
from gemini_client import extract_locations_from_text, setup_genai
from geocoder import get_coordinates
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup Gemini API before app initialization
setup_genai()

app = FastAPI()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.getenv("API_KEY"):
        return api_key_header
    raise HTTPException(
        status_code=403, detail="Could not validate API key"
    )

@app.post("/get-coordinates", response_model=LocationResponse)
async def get_location_coordinates(
    request: LocationRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        locations = extract_locations_from_text(request.text)
        results = []
        missing_locations = []

        for location in locations:
            coords = await get_coordinates(location)
            if coords:
                results.append(Coordinates(location_name=location, latitude=coords[0], longitude=coords[1]))
            else:
                missing_locations.append(location)

        if missing_locations:
            logger.info(f"Coordinates not found for locations: {missing_locations}")
        logger.info(f"Returning coordinates for {len(results)} locations.")
        return LocationResponse(coordinates=results)
    except Exception as e:
        logger.exception(f"Error in get_location_coordinates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
def read_root():
    return {
        "message": "API is up and running! Visit /docs for Swagger UI or use /get-coordinates endpoint."
    }
