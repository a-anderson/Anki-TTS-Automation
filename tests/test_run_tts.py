import pytest
from anki_tts.gcloud_tts import synthesize_audio
from scripts.run_tts import process_deck


# =========================
# Fixtures
# =========================
@pytest.fixture
def fake_notes():
    return [
        {
            "noteId": 1,
            "fields": {
                "Sentence": {"value": "こんにちは"},
                "Audio": {"value": ""},
            },
        },
        {
            "noteId": 2,
            "fields": {
                "Sentence": {"value": ""},
                "Audio": {"value": ""},
            },
        },
        {
            "noteId": 3,
            "fields": {
                "Sentence": {"value": "Hello"},
                "Audio": {"value": "[sound:old.mp3]"},
            },
        },
    ]


# =========================
# Tests
# =========================

def test_audio_added_to_audio_field_only(mocker, fake_notes):
    """Ensure audio is added only to the audio field, text remains unchanged."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[0]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"fakebytes")

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note", return_value=True)

    process_deck("MyDeck", "Sentence", "Audio")

    mock_add_audio.assert_called_once_with(1, "Audio", "1.mp3", b"fakebytes")


def test_skips_empty_text_field(mocker, fake_notes):
    """Ensure notes with empty text_field are skipped."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[2])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[1]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio")

    mock_add_audio.assert_not_called()


def test_skips_existing_audio_when_not_overwriting(mocker, fake_notes):
    """Ensure notes with existing audio are skipped unless overwrite=True."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[3])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[2]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    # Default overwrite = False → skip
    process_deck("MyDeck", "Sentence", "Audio", overwrite=False)
    mock_add_audio.assert_not_called()

    # Overwrite = True → should add audio
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"newbytes")
    process_deck("MyDeck", "Sentence", "Audio", overwrite=True)
    mock_add_audio.assert_called_once_with(3, "Audio", "3.mp3", b"newbytes")


def test_missing_required_fields(mocker):
    """Ensure notes missing text or audio fields are skipped."""
    bad_note = {
        "noteId": 99,
        "fields": {"Sentence": {"value": "こんにちは"}}  # Missing Audio field
    }

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[99])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[bad_note])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio")

    mock_add_audio.assert_not_called()


# =========================
# Label: main.py - process_deck
# =========================
def test_process_deck_skips_empty_notes(mocker):
    # Mock TTS and Anki functions
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[{
        "noteId": 1,
        "fields": {
            "Sentence": {"value": ""},   # Empty text field
            "Audio": {"value": ""},      # Audio field exists
        }
    }])
    mock_tts = mocker.patch("scripts.run_tts.synthesize_audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("Test Deck", "Sentence", "Audio", language_code="ja-JP")

    # synthesize_audio and add_audio_to_note should not be called
    mock_tts.assert_not_called()
    mock_add_audio.assert_not_called()


def test_process_deck_calls_tts_and_add_audio(mocker):
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[{
        "noteId": 1,
        "fields": {
            "Sentence": {"value": "Hello"},  # Text field populated
            "Audio": {"value": ""},          # Audio field initially empty
        }
    }])
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"fake_audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note", return_value=True)

    process_deck("Test Deck", "Sentence", "Audio", language_code="ja-JP")

    # Audio should be added to the Audio field, not Sentence
    mock_add_audio.assert_called_once_with(1, "Audio", "1.mp3", b"fake_audio")


def test_process_deck_basic_flow(mocker):
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[{
        "noteId": 1,
        "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": ""}}
    }])
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("Test Deck", "Sentence", "Audio")

    mock_add_audio.assert_called_once_with(1, "Audio", "1.mp3", b"audio")
