"""
Configuration file for Anki TTS Automation.
Loads environment variables and sets defaults for AnkiConnect and Google TTS.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load values from .env if present

# =========================
# AnkiConnect settings
# =========================
ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")

# =========================
# TTS defaults
# =========================
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ja-JP")

DEFAULT_VOICES = {
    "ja-JP": os.getenv("VOICE_JA", "ja-JP-Wavenet-B"),
    "en-GB": os.getenv("VOICE_EN", "en-GB-Wavenet-F"),
    "fr-FR": os.getenv("VOICE_FR", "fr-FR-Wavenet-F"),
}
