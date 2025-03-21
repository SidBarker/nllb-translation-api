import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Model name (can be changed to use different sizes)
MODEL_NAME = "facebook/nllb-200-distilled-600M"

def download_and_save_model():
    """
    Download and save the NLLB-200 model and tokenizer locally
    """
    logger.info(f"Downloading and saving model: {MODEL_NAME}")
    
    try:
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Download and save tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        # Download and save model
        logger.info("Downloading model (this may take some time)...")
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        
        # Save models to local directory
        logger.info("Saving model and tokenizer locally...")
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_model")
        os.makedirs(model_dir, exist_ok=True)
        
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        
        logger.info(f"Model and tokenizer saved successfully to {model_dir}")
        
        # Test the model with a simple translation
        test_model(model, tokenizer, device)
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise

def test_model(model, tokenizer, device):
    """
    Test the model with a simple translation
    """
    try:
        logger.info("Testing model with a simple translation...")
        
        # Example text to translate (English to French)
        english_text = "Hello, how are you? This is a test of the translation model."
        
        # Set source language for tokenization
        tokenizer.src_lang = "eng_Latn"
        
        # Tokenize text
        inputs = tokenizer(english_text, return_tensors="pt").to(device)
        
        # Generate translation
        forced_bos_token_id = tokenizer.lang_code_to_id["fra_Latn"]
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=128,
            num_beams=5,
            length_penalty=1.0
        )
        
        # Decode output tokens
        french_translation = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        
        logger.info(f"Test translation completed.")
        logger.info(f"English: {english_text}")
        logger.info(f"French: {french_translation}")
        
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        raise

if __name__ == "__main__":
    download_and_save_model() 