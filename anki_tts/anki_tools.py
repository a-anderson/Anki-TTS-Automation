import requests
import base64
import logging
from typing import List, Dict
from anki_tts.config import ANKI_CONNECT_URL


def invoke(action: str, **params):
    """Send a request to AnkiConnect API and return the result."""
    request_json = {"action": action, "version": 6, "params": params}
    try:
        response = requests.post(ANKI_CONNECT_URL, json=request_json, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("error") is not None:
            raise RuntimeError(f"AnkiConnect error: {result['error']}")
        return result["result"]
    except Exception as e:
        logging.error(f"Failed to call AnkiConnect action {action}: {e}")
        raise


def get_notes_from_deck(deck_name: str) -> List[int]:
    """Return note IDs from the given deck."""
    return invoke("findNotes", query=f'deck:"{deck_name}"')


def get_note_info(note_ids: List[int]) -> List[Dict]:
    """Return full note info for a batch of note IDs."""
    if not note_ids:
        return []
    return invoke("notesInfo", notes=note_ids)


def add_audio_to_note(note_id: int, field_name: str, filename: str, audio_data: bytes):
    """Attach audio to a note field in Anki."""
    b64_audio = base64.b64encode(audio_data).decode("utf-8")
    return invoke(
        "updateNote",
        note={
            "id": note_id,
            "fields": {field_name: ""},
            "audio": [
                {
                    "filename": filename,
                    "data": b64_audio,
                    "fields": [field_name],
                }
            ],
        },
    )
