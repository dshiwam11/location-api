# main.py

import os
import logging
import httpx

from fastapi import FastAPI, Security, HTTPException, Depends, Body, status, Request # Import Request
from fastapi.security.api_key import APIKeyHeader
from models import LocationResponse, Place # Ensure Place and LocationResponse are correctly imported
# You had `from models import LocationRequest` in your previous code. If LocationRequest is needed for other
# purposes but not directly as the `Body` param type, keep it. If you're only using `text: str = Body(...)`,
# then LocationRequest isn't strictly necessary for *this* endpoint's signature, but keep it if used elsewhere.
from gemini_client import extract_locations_from_text, setup_genai
from geocoder import get_coordinates
from dotenv import load_dotenv
from typing import Optional, List

from fastapi.middleware.cors import CORSMiddleware

# Load .env variables early
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini API
setup_genai()

# API Key Security
API_KEY_NAME = "X-API-Key"
# FIX: Set auto_error=False. This tells FastAPI NOT to automatically raise an error if the header is missing.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# FIX: Add Request as a dependency and make api_key_header Optional.
# This allows us to check the HTTP method before validating the key.
async def get_api_key(request: Request, api_key_value: Optional[str] = Security(api_key_header)):
    # If it's an OPTIONS request (preflight), just return None.
    # The browser does not send the API key for preflight requests.
    if request.method == "OPTIONS":
        return None

    # If it's not an OPTIONS request, the API key is now required.
    if not api_key_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header required for this method."
        )

    # Validate the API key against the environment variable
    if api_key_value == os.getenv("API_KEY"): # Ensure "API_KEY" env var is set on Cloud Run
        return api_key_value
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API key.")

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Configuration ---
# Define origins that are allowed to access your API.
# It's crucial to include the specific domain(s) where your Bolt frontend is hosted.
origins = [
    "http://localhost:3000",                                                # For local development of your frontend
    "https://*.webcontainer-api.io",                                        # For Bolt's webcontainer preview URLs (wildcard)
    "https://zp1v56uxy8rdx5ypatb0ockcb9tr6a-oci3--5173--cb7c0bca.local-credentialless.webcontainer-api.io", # Exact URL from your error
    "https://*.stackblitz.io",                                              # StackBlitz domains
    "https://eclectic-griffin-eb897c.netlify.app",
    "https://*.netlify.app",
    # Add your specific Bolt application's URL if it's deployed to a fixed domain
    # Example: "https://your-bolt-app-id.firebaseapp.com",
    # If your Bolt app eventually deploys to a custom domain, add it:
    # "https://your-custom-bolt-domain.com",
    "https://travelguideintelligence-61701835609.asia-southeast1.run.app", # Your Gemini Cloud Function's URL (if it's also a client to THIS API)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,             # Allow cookies to be sent with requests
    allow_methods=["*"],                # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],                # Allows all headers, including 'Content-Type', 'X-API-Key', etc.
)
# --- END CORS Configuration ---


# --- Your Endpoint ---
@app.post("/get-coordinates", response_model=LocationResponse)
async def get_location_coordinates(
    text_content: str = Body(..., media_type="text/plain"), # Based on your frontend description
    api_key: str = Depends(get_api_key) # This dependency will now handle OPTIONS correctly
):
    logger.info(f"Received request for get_coordinates. Method: POST. Body media type: text/plain.")
    
    try:
        # Use the `text_content` directly from the Body parameter
        locations = extract_locations_from_text(text_content)
        results = []
        missing = []
        for loc in locations:
            coords = await get_coordinates(loc["name"]) # Assuming get_coordinates is async
            if coords:
                # Ensure Place model matches data types from geocoder
                results.append(Place(
                    name=loc["name"],
                    type=loc["type"],
                    latitude=coords[0],
                    longitude=coords[1]
                ))
            else:
                missing.append(loc["name"])

        if missing:
            logger.info(f"Could not find coordinates for: {', '.join(missing)}")
        
        return LocationResponse(places=results)

    except Exception:
        logger.exception("Error in get_location_coordinates processing.")
        raise HTTPException(status_code=500, detail="Internal server error during location processing.")

@app.get("/")
def read_root():
    return {"message": "FastAPI Location API is running. Use POST /get-coordinates with text/plain body."}

if __name__ == "__main__":
    import uvicorn
    # When deployed to Cloud Run, the PORT environment variable is automatically set by GCP.
    # For local testing, it defaults to 8080.
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))