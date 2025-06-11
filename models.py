from pydantic import BaseModel
from typing import List, Optional

class LocationRequest(BaseModel):
    text: str

class Place(BaseModel):
    name: str
    type: str
    latitude: float
    longitude: float

class LocationResponse(BaseModel):
    places: List[Place]
