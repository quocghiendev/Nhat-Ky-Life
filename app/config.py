from pathlib import Path
import os
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
IMAGES_DIR = UPLOADS_DIR / "images"
AUDIO_DIR = UPLOADS_DIR / "audio"
DB_PATH = DATA_DIR / "database.sqlite3"
ENV_PATH = BASE_DIR / ".env"

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables if .env exists
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Supported AI configurations
DEFAULT_AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_AI_TONE = os.getenv("AI_TONE", "chan_that")  # chan_that, sau_sac, tho_mong, vui_ve, toi_gian
