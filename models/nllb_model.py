import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from langdetect import detect
import logging

# Configure logging based on DEBUG env var
debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NLLBTranslator:
    """
    Translator class using Meta's NLLB-200 model from Hugging Face
    """
    # Model size can be adjusted here - distilled-600M, 1.3B, 3.3B
    MODEL_NAME = "facebook/nllb-200-distilled-600M"
    
    # Language code mappings
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
    
    def __init__(self):
        """
        Initialize the translator by loading the NLLB model and tokenizer
        """
        # Check if GPU is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        logger.debug(f"Loading NLLB model: {self.MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.MODEL_NAME).to(self.device)
        logger.info("NLLB model loaded successfully")
    
    def detect_language(self, text):
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
            nllb_code = self.LANGUAGE_CODE_MAP.get(lang_code)
            
            if nllb_code:
                logger.info(f"Detected language: {lang_code} (NLLB code: {nllb_code})")
                return nllb_code
            else:
                logger.warning(f"Language {lang_code} not supported by NLLB, using English as fallback")
                return self.LANGUAGE_CODE_MAP['en']
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            logger.warning("Using English as fallback language")
            return self.LANGUAGE_CODE_MAP['en']
    
    def translate(self, text, target_language, source_language=None):
        """
        Translate text from source language to target language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (ISO 639-1)
            source_language (str, optional): Source language code (ISO 639-1). If None, auto-detection is used.
            
        Returns:
            str: Translated text
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for translation")
                return ""
            
            # Convert target_language to NLLB format
            if target_language not in self.LANGUAGE_CODE_MAP:
                logger.warning(f"Target language {target_language} not supported, using English as fallback")
                target_language_code = self.LANGUAGE_CODE_MAP['en']
            else:
                target_language_code = self.LANGUAGE_CODE_MAP[target_language]
            
            # Detect or use provided source language
            if source_language is None:
                source_language_code = self.detect_language(text)
            else:
                source_language_code = self.LANGUAGE_CODE_MAP.get(
                    source_language, self.detect_language(text)
                )
            
            logger.debug(f"Translating from {source_language_code} to {target_language_code}")
            
            # Set source language for tokenization
            self.tokenizer.src_lang = source_language_code
            
            # Tokenize text
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate translation
            forced_bos_token_id = self.tokenizer.lang_code_to_id[target_language_code]
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=1024,
                num_beams=5,
                length_penalty=1.0
            )
            
            # Decode output tokens
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            logger.debug(f"Translation result: {translation[:50]}...")
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return f"Translation error: {str(e)}"

# Singleton instance
translator = None

def get_translator():
    """
    Get or create the singleton translator instance
    
    Returns:
        NLLBTranslator: Translator instance
    """
    global translator
    if translator is None:
        logger.info("Creating new translator instance")
        translator = NLLBTranslator()
    return translator 