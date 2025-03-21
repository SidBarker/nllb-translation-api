from fastapi import APIRouter, HTTPException, Depends
from ..models.nllb_model import get_translator
from ..utils.exceptions import TranslationError, UnsupportedLanguageError
from .schemas import TranslationRequest, TranslationResponse
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

@router.post("/translate", response_model=TranslationResponse, status_code=200)
async def translate(request: TranslationRequest):
    """
    Translate text from source language to target language.
    If source language is not provided, it will be auto-detected.
    """
    try:
        # Get translator instance (singleton)
        translator = get_translator()
        
        # Log request info
        logger.info(f"Translation request: target={request.target_language}, source={request.source_language or 'auto'}")
        
        # Get source language code (either provided or detected)
        source_language = request.source_language
        if source_language is None:
            # Detect language first to include in response
            source_language_code = translator.detect_language(request.text)
            # Extract ISO code (first part before '_')
            source_language = source_language_code.split('_')[0]
        
        # Translate text
        translated_text = translator.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=source_language
        )
        
        # Build and return response
        return TranslationResponse(
            translated_text=translated_text,
            source_language=source_language,
            target_language=request.target_language
        )
        
    except UnsupportedLanguageError as e:
        logger.error(f"Unsupported language: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except TranslationError as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/health", status_code=200)
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok"} 