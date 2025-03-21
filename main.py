import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.endpoints import router
from models.nllb_model import get_translator

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RQG Translation API",
    description="API for translating text using NLLB-200 model",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in this example
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "RQG Translation API is running",
        "documentation": "/docs",
    }

# Startup event to preload the model
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing translation model...")
        # Initialize the translator (will be cached as singleton)
        get_translator()
        logger.info("Translation model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize translation model: {str(e)}")
        # We don't want to prevent the API from starting, but log the error
        # The error will be raised when the first translation request is made

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="debug" if debug_mode else "info",
        reload=debug_mode,
    ) 