import os
import runpod
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from langdetect import detect
import logging

# Configure logging
debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Language code mappings for NLLB
LANGUAGE_CODE_MAP = {
    'en': 'eng_Latn',
    'ar': 'arb_Arab',
    'fr': 'fra_Latn',
    'es': 'spa_Latn',
    'de': 'deu_Latn',
    'ru': 'rus_Cyrl',
    'zh': 'zho_Hans',
    'ja': 'jpn_Jpan',
    'pt': 'por_Latn',
    'it': 'ita_Latn',
    'nl': 'nld_Latn',
    'cs': 'ces_Latn',
    'pl': 'pol_Latn',
    'tr': 'tur_Latn',
    'ko': 'kor_Hang',
    'uk': 'ukr_Cyrl',
    'vi': 'vie_Latn',
    'id': 'ind_Latn',
    'fa': 'fas_Arab',
    'sv': 'swe_Latn',
    'hu': 'hun_Latn',
    'fi': 'fin_Latn',
    'da': 'dan_Latn',
    'no': 'nob_Latn',
    'he': 'heb_Hebr',
    'th': 'tha_Thai',
    'hi': 'hin_Deva',
    'bg': 'bul_Cyrl',
    'el': 'ell_Grek',
    'ro': 'ron_Latn',
    'sk': 'slk_Latn',
    'lt': 'lit_Latn',
    'lv': 'lvs_Latn',
    'et': 'est_Latn',
    'sr': 'srp_Cyrl',
    'hr': 'hrv_Latn',
    'sl': 'slv_Latn',
    'ca': 'cat_Latn',
    'ms': 'zsm_Latn',
    'ur': 'urd_Arab',
}

# Global variables for model and tokenizer
MODEL_NAME = "facebook/nllb-200-distilled-600M"
model = None
tokenizer = None

def load_model():
    """Load the NLLB model and tokenizer"""
    global model, tokenizer
    
    logger.info("Loading NLLB model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
    
    logger.info("Model loaded successfully")
    return model, tokenizer

def detect_language(text):
    """
    Detect the language of input text using langdetect
    
    Args:
        text (str): Text to detect language
        
    Returns:
        str: NLLB language code
    """
    try:
        logger.debug(f"Detecting language for text: {text[:50]}...")
        lang_code = detect(text)
        nllb_code = LANGUAGE_CODE_MAP.get(lang_code)
        
        if nllb_code:
            logger.info(f"Detected language: {lang_code} (NLLB code: {nllb_code})")
            return nllb_code, lang_code
        else:
            logger.warning(f"Language {lang_code} not supported by NLLB, using English as fallback")
            return LANGUAGE_CODE_MAP['en'], 'en'
    except Exception as e:
        logger.error(f"Error detecting language: {str(e)}")
        logger.warning("Using English as fallback language")
        return LANGUAGE_CODE_MAP['en'], 'en'

def translate(text, target_language, source_language=None):
    """
    Translate text from source language to target language
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (ISO 639-1)
        source_language (str, optional): Source language code (ISO 639-1). If None, auto-detection is used.
        
    Returns:
        dict: Dictionary with translated text and detected/provided source language
    """
    global model, tokenizer
    
    # Load model if not already loaded
    if model is None or tokenizer is None:
        model, tokenizer = load_model()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        if not text.strip():
            logger.warning("Empty text provided for translation")
            return {"translated_text": "", "source_language": source_language or "en"}
        
        # Convert target_language to NLLB format
        if target_language not in LANGUAGE_CODE_MAP:
            logger.warning(f"Target language {target_language} not supported, using English as fallback")
            target_language_code = LANGUAGE_CODE_MAP['en']
        else:
            target_language_code = LANGUAGE_CODE_MAP[target_language]
        
        # Detect or use provided source language
        if source_language is None:
            # Detect language
            source_language_code, detected_lang = detect_language(text)
            source_language = detected_lang
        else:
            source_language_code = LANGUAGE_CODE_MAP.get(source_language)
            if source_language_code is None:
                logger.warning(f"Source language {source_language} not supported, detecting language automatically")
                source_language_code, detected_lang = detect_language(text)
                source_language = detected_lang
        
        logger.debug(f"Translating from {source_language_code} to {target_language_code}")
        
        # Set source language for tokenization
        tokenizer.src_lang = source_language_code
        
        # Tokenize text
        inputs = tokenizer(text, return_tensors="pt").to(device)
        
        # Generate translation
        forced_bos_token_id = tokenizer.lang_code_to_id[target_language_code]
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=1024,
                num_beams=5,
                length_penalty=1.0
            )
        
        # Decode output tokens
        translation = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        logger.debug(f"Translation result: {translation[:50]}...")
        
        return {
            "translated_text": translation,
            "source_language": source_language,
            "target_language": target_language
        }
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return {
            "error": f"Translation error: {str(e)}",
            "source_language": source_language or "unknown",
            "target_language": target_language
        }

# RunPod handler function
def handler(event):
    """
    Handle RunPod serverless request
    
    Args:
        event (dict): RunPod event object with input data
        
    Returns:
        dict: Response with translated text
    """
    try:
        logger.info("Received translation request")
        
        # Extract request data
        input_data = event.get("input", {})
        text = input_data.get("text")
        target_language = input_data.get("target_language")
        source_language = input_data.get("source_language")
        
        # Validate required fields
        if not text:
            return {"error": "Missing required field: text"}
        if not target_language:
            return {"error": "Missing required field: target_language"}
        
        # Perform translation
        result = translate(text, target_language, source_language)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": f"Error processing request: {str(e)}"}

# Load model at startup
load_model()

# Start the RunPod serverless handler
runpod.serverless.start({"handler": handler}) 