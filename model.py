from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os

# Use environment variables for model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-cnn")  # More powerful model
CACHE_DIR = "./model_cache"  # Local model caching

# Create cache directory if not exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Load with explicit caching and error handling
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
except Exception as e:
    print(f"Model loading failed: {str(e)}")
    # Fallback to smaller model
    tokenizer = AutoTokenizer.from_pretrained("t5-small", cache_dir=CACHE_DIR)
    model = AutoModelForSeq2SeqLM.from_pretrained("t5-small", cache_dir=CACHE_DIR)