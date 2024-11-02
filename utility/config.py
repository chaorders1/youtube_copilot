"""Configuration settings for the persona analyzer."""
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROMPT_DIR = BASE_DIR / 'prompt'
DATA_DIR = BASE_DIR / 'data'

# API settings
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 1000
TEMPERATURE = 0

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ('.jpg', '.jpeg', '.png') 