from pydantic import BaseModel, Field
from typing import Optional


class TranslationRequest(BaseModel):
    """
    Schema for translation request
    """
    text: str = Field(..., title="Text to translate", description="Content that needs to be translated")
    target_language: str = Field(..., title="Target language", description="Language code to translate to (ISO 639-1 format)")
    source_language: Optional[str] = Field(None, title="Source language", description="Language code of the source text (ISO 639-1 format). If not provided, auto-detection will be used.")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "target_language": "fr",
                "source_language": None
            }
        }


class TranslationResponse(BaseModel):
    """
    Schema for translation response
    """
    translated_text: str = Field(..., title="Translated text", description="The translated content")
    source_language: str = Field(..., title="Source language", description="Detected or provided source language code")
    target_language: str = Field(..., title="Target language", description="Target language code")
    
    class Config:
        schema_extra = {
            "example": {
                "translated_text": "Bonjour, comment allez-vous?",
                "source_language": "en",
                "target_language": "fr"
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error response
    """
    error: str = Field(..., title="Error", description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Failed to translate text"
            }
        } 