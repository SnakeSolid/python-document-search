import os

STORAGE_ROOT = ".storage"
DOCUMENT_ROOT = ".documents"

MODEL_EMBEDDING = "nomic-embed-text"
MODEL_TEXT = "gemma2"
MODEL_TRANSLATE = "gemma2"
MODEL_IMAGE = "llava:13b"

LANGUAGES = [
    "English",
    "Russian",
    "German",
    "French",
    "Spanish",
    "Polish",
    "Greek",
    "Hebrew",
    "Arabic",
    "Hindi",
    "Chinese",
    "Japanese",
]

# Create storage and documents directories if they do not exist.
os.makedirs(STORAGE_ROOT, exist_ok=True)
os.makedirs(DOCUMENT_ROOT, exist_ok=True)
