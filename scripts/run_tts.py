import argparse
import logging
import re
import sys
from tqdm import tqdm
from typing import Optional
from anki_tts.anki_tools import get_notes_from_deck, get_note_info, add_audio_to_note
from anki_tts.gcloud_tts import init_tts_client, synthesize_audio
from anki_tts.logging_utils import TqdmLoggingHandler
from anki_tts.config import DEFAULT_LANGUAGE

def build_audio_filename(note_id: int, audio_field: str) -> str:
    safe_field = re.sub(r"[^\w\-]", "_", audio_field)
    return f"{note_id}_{safe_field}.mp3"


def iter_notes_with_progress(notes, desc: str):
    """Generator to yield notes and update tqdm progress automatically."""
    with tqdm(total=len(notes), desc=desc, unit="card") as progress_bar:
        for note in notes:
            yield note
            progress_bar.update(1)

def process_deck(
    deck_name: str,
    text_field: str,
    audio_field: str,
    language_code: str = "ja-JP",
    overwrite: bool = False,
    voice: Optional[str] = None,
    max_cards: Optional[int] = None,
    max_consecutive_failures: int = 3,
) -> bool:
    """
    Process all notes in a given Anki deck: generate audio for a text field and
    attach it to an audio field.

    Args:
        deck_name: The name of the Anki deck to process.
        text_field: The field containing the source text.
        audio_field: The field where synthesized audio will be attached.
        language_code: Language code for synthesis (default: "ja-JP").
        overwrite: If True, replace existing audio files.
        voice: Optional voice name for TTS synthesis.
        max_cards: Maximum number of notes to add audio to. Notes skipped due
            to empty text, existing audio, or failed synthesis do not count
            toward this limit. Must be >= 1. Default None adds audio to all
            eligible notes.
        max_consecutive_failures: Abort after this many consecutive synthesis
            failures. A successful addition resets the counter. Must be >= 1.
            Default 3.

    Returns:
        True if the run completed normally, False if aborted due to consecutive
        failures.
    """
    if max_cards is not None and max_cards < 1:
        raise ValueError(f"max_cards must be >= 1, got {max_cards}")
    if max_consecutive_failures < 1:
        raise ValueError(f"max_consecutive_failures must be >= 1, got {max_consecutive_failures}")

    client = init_tts_client()
    note_ids = get_notes_from_deck(deck_name)
    if not note_ids:
        logging.info(f"No notes found in deck '{deck_name}'.")
        return True

    notes = get_note_info(note_ids)

    desc = f"Processing deck '{deck_name}'"
    if max_cards is not None:
        desc += f" (max {max_cards})"

    audio_added = 0
    consecutive_failures = 0
    aborted = False
    for note in iter_notes_with_progress(notes, desc):
        if max_cards is not None and audio_added >= max_cards:
            break

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
            filename = build_audio_filename(note_id, audio_field)
            add_audio_to_note(note_id, audio_field, filename, audio_data)
            audio_added += 1
            consecutive_failures = 0
        except Exception as e:
            logging.error(f"❌ Failed to process note {note_id}: {e}")
            consecutive_failures += 1
            if consecutive_failures >= max_consecutive_failures:
                aborted = True
                break

    logging.info(f"Added audio to {audio_added} card(s).")
    if aborted:
        logging.error(
            f"❌ Run aborted — {consecutive_failures} consecutive synthesis failures. "
            "Check your API credentials or quota."
        )
    else:
        logging.info("✅ Finished processing deck.")
    return not aborted


def _positive_int(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    if ivalue < 1:
        raise argparse.ArgumentTypeError(f"must be a positive integer, got {value}")
    return ivalue


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Add Google TTS audio to Anki deck.")
    parser.add_argument("deck", help="Name of the Anki deck to process")
    parser.add_argument("--text-field", required=True, help="Anki deck field name containing the input text")
    parser.add_argument("--audio-field", required=True, help="Anki deck field name where audio will be added")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help=f"Language code (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing audio")
    parser.add_argument("--voice", default=None, help="Google TTS voice name")
    parser.add_argument(
        "--max-cards",
        type=_positive_int,
        default=None,
        help="Maximum number of cards to add audio to. Cards skipped due to empty text or existing audio do not count toward this limit. Default: all eligible cards.",
    )
    parser.add_argument(
        "--max-consecutive-failures",
        type=_positive_int,
        default=3,
        help="Abort after this many consecutive synthesis failures. A successful addition resets the counter. Default: 3.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    args = parser.parse_args()
    
    handler = TqdmLoggingHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.root.handlers = [handler]
    logging.root.setLevel(getattr(logging, args.log_level.upper()))

    success = process_deck(
        args.deck,
        args.text_field,
        args.audio_field,
        language_code=args.language,
        overwrite=args.overwrite,
        voice=args.voice,
        max_cards=args.max_cards,
        max_consecutive_failures=args.max_consecutive_failures,
    )
    if not success:
        sys.exit(1)
