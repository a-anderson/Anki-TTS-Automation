import logging
import os
from google.cloud import texttospeech
# from pathlib import Path
from anki_tts.config import DEFAULT_VOICES, DEFAULT_LANGUAGE

def init_tts_client():
    """
    Initialize Google TTS client.

    Raises:
        EnvironmentError: If GOOGLE_APPLICATION_CREDENTIALS is not set.
        Exception: If the client fails to initialize.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_path:
        raise EnvironmentError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. "
            "Please set it to the path of your service account JSON key."
        )

    if not os.path.isfile(credentials_path):
        raise EnvironmentError(
            f"GOOGLE_APPLICATION_CREDENTIALS path does not exist: {credentials_path}"
        )

    try:
        client = texttospeech.TextToSpeechClient()
        logging.info(f"Initialized Google TTS client using credentials at: {credentials_path}")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Google TTS client: {e}")
        raise

def synthesize_audio(
    text: str,
    client,
    language_code: str = "ja-JP",
    voice_name: str | None = None,
) -> bytes:
    """Generate speech for a given text."""
    if not voice_name:
        voice_name = DEFAULT_VOICES.get(language_code, DEFAULT_VOICES[DEFAULT_LANGUAGE])

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
    except Exception as e:
        logging.error(f"TTS synthesis failed for text '{text[:30]}...': {e}")
        raise

    return response.audio_content
