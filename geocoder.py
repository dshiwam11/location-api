import httpx

async def get_coordinates(location_name: str) -> tuple[float, float] | None:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json", "limit": 1}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    return None
