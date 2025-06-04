from pydantic import BaseModel
from typing import List, Optional

class LocationRequest(BaseModel):
    text: str

class Coordinates(BaseModel):
    location_name: str
    latitude: float
    longitude: float

class LocationResponse(BaseModel):
    coordinates: List[Coordinates]
