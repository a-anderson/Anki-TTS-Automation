import requests
import base64
import logging
from typing import List, Dict, Any
from anki_tts.config import ANKI_CONNECT_URL


def invoke(action: str, **params: Any) -> Any:
    """
    Send a request to the AnkiConnect API.

    Args:
        action: The AnkiConnect action name.
        **params: Additional parameters for the action.

    Returns:
        The 'result' field from the AnkiConnect response.

    Raises:
        RuntimeError: If AnkiConnect returns an error.
        requests.RequestException: If the HTTP request fails.
    """
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
    """
    Get note IDs from a given deck.

    Args:
        deck_name: Name of the Anki deck.

    Returns:
        A list of note IDs belonging to the deck.
    """
    return invoke("findNotes", query=f'deck:"{deck_name}"')


def get_note_info(note_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Get detailed information for a batch of notes.

    Args:
        note_ids: List of Anki note IDs.

    Returns:
        A list of dictionaries containing note information.
    """
    if not note_ids:
        return []
    return invoke("notesInfo", notes=note_ids)


def add_audio_to_note(note_id: int, field_name: str, filename: str, audio_data: bytes) -> Any:
    """
    Attach audio to a note field in Anki.

    Args:
        note_id: The ID of the Anki note.
        field_name: The field in the note to associate the audio with.
        filename: The filename to assign to the audio in Anki.
        audio_data: Raw audio data as bytes.

    Returns:
        The response from AnkiConnect after updating the note.
    """
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
