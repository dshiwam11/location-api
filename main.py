from fastapi import FastAPI
from models import LocationRequest, LocationResponse, Coordinates
from gemini_client import extract_locations_from_text
from geocoder import get_coordinates

app = FastAPI()

@app.post("/get-coordinates", response_model=LocationResponse)
async def get_location_coordinates(request: LocationRequest):
    locations = extract_locations_from_text(request.text)
    results = []

    for location in locations:
        coords = await get_coordinates(location)
        if coords:
            results.append(Coordinates(location_name=location, latitude=coords[0], longitude=coords[1]))

    return LocationResponse(coordinates=results)
