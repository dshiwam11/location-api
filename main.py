from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from models import LocationRequest, LocationResponse, Coordinates
from gemini_client import extract_locations_from_text
from geocoder import get_coordinates
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

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
    locations = extract_locations_from_text(request.text)
    results = []

    for location in locations:
        coords = await get_coordinates(location)
        if coords:
            results.append(Coordinates(location_name=location, latitude=coords[0], longitude=coords[1]))

    return LocationResponse(coordinates=results)
