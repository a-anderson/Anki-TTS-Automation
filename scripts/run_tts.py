import argparse
import logging
from anki_tts.anki_tools import get_notes_from_deck, get_note_info, add_audio_to_note
from anki_tts.gcloud_tts import init_tts_client, synthesize_audio
from anki_tts.config import DEFAULT_LANGUAGE

def process_deck(deck_name, text_field, audio_field, language_code="ja-JP", overwrite=False, voice=None):
    client = init_tts_client()
    note_ids = get_notes_from_deck(deck_name)
    if not note_ids:
        logging.info(f"No notes found in deck '{deck_name}'.")
        return

    notes = get_note_info(note_ids)

    for note in notes:
        note_id = note["noteId"]
        fields = note["fields"]

        # Validate required fields
        if text_field not in fields or audio_field not in fields:
            logging.warning(f"Note {note_id} missing required fields: {text_field}, {audio_field}")
            continue

        text_value = fields[text_field]["value"]
        audio_value = fields[audio_field]["value"]

        # Skip empty text fields
        if not text_value.strip():
            logging.debug(f"Skipping empty field for note {note_id}.")
            continue
        
        # Skip if audio already exists and overwrite is False
        if "[sound:" in audio_value and not overwrite:
            logging.debug(f"Skipping note {note_id} (already has audio).")
            continue

        logging.info(f"Generating audio for note {note_id}: {text_value}")
        try:
            audio_data = synthesize_audio(text_value, client, language_code=language_code, voice_name=voice)
            filename = f"{note_id}.mp3"
            add_audio_to_note(note_id, audio_field, filename, audio_data)
        except Exception as e:
            logging.error(f"Failed to process note {note_id}: {e}")

    logging.info("✅ Finished processing deck.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Add Google TTS audio to Anki deck.")
    parser.add_argument("deck", help="Name of the Anki deck to process")
    parser.add_argument("--text-field", required=True, help="Anki deck field name containing the input text")
    parser.add_argument("--audio-field", required=True, help="Anki deck field name where audio will be added")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help=f"Language code (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing audio")
    parser.add_argument("--voice", default=None, help="Google TTS voice name")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(levelname)s: %(message)s",
    )
    process_deck(
        args.deck,
        args.text_field,
        args.audio_field,
        language_code=args.language,
        overwrite=args.overwrite,
        voice=args.voice,
    )
