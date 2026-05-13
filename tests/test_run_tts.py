import logging
import pytest
from scripts.run_tts import process_deck


# =========================
# Fixtures
# =========================
@pytest.fixture
def fake_notes() -> list[dict]:
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

@pytest.fixture(autouse=True)
def mock_tqdm(mocker):
    # Patches the progress-bar wrapper rather than tqdm itself; tqdm uses a
    # context manager internally which a simple lambda cannot satisfy.
    mocker.patch("scripts.run_tts.iter_notes_with_progress", side_effect=lambda notes, desc: iter(notes))

# =========================
# Tests
# =========================

def test_audio_added_to_audio_field_only(mocker, fake_notes) -> None:
    """Ensure audio is added only to the audio field, text remains unchanged."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[0]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"fakebytes")

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note", return_value=True)

    process_deck("MyDeck", "Sentence", "Audio")

    mock_add_audio.assert_called_once_with(1, "Audio", "1.mp3", b"fakebytes")


def test_skips_empty_text_field(mocker, fake_notes) -> None:
    """Ensure notes with empty text_field are skipped."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[2])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[1]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio")

    mock_add_audio.assert_not_called()


def test_skips_existing_audio_when_not_overwriting(mocker, fake_notes) -> None:
    """Ensure notes with existing audio are skipped unless overwrite=True."""

    mock_client = object()
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[3])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[fake_notes[2]])
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)

    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    # Default overwrite = False -> skip
    process_deck("MyDeck", "Sentence", "Audio", overwrite=False)
    mock_add_audio.assert_not_called()

    # Overwrite = True -> should add audio
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"newbytes")
    process_deck("MyDeck", "Sentence", "Audio", overwrite=True)
    mock_add_audio.assert_called_once_with(3, "Audio", "3.mp3", b"newbytes")


def test_missing_required_fields(mocker) -> None:
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
# run_tts.py - process_deck
# =========================
def test_process_deck_skips_empty_notes(mocker) -> None:
    """Ensure process_deck() skips notes with empty text fields."""

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


def test_process_deck_calls_tts_and_add_audio(mocker) -> None:
    """Ensure process_deck() calls TTS and adds audio when text is present."""

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


def test_process_deck_basic_flow(mocker) -> None:
    """Basic test of process_deck() end-to-end flow."""

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


# =========================
# max_cards tests
# =========================

def test_max_cards_limits_processing(mocker) -> None:
    """Ensure max_cards caps the number of audio additions, not cards visited."""

    three_eligible_notes = [
        {"noteId": i, "fields": {"Sentence": {"value": f"text{i}"}, "Audio": {"value": ""}}}
        for i in range(1, 4)
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2, 3])
    mocker.patch("scripts.run_tts.get_note_info", return_value=three_eligible_notes)
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio", max_cards=2)

    assert mock_add_audio.call_count == 2


def test_max_cards_counts_only_additions_not_skips(mocker) -> None:
    """Ensure skipped notes (existing audio, empty text) don't count toward max_cards."""

    notes = [
        {"noteId": 1, "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": "[sound:old.mp3]"}}},
        {"noteId": 2, "fields": {"Sentence": {"value": ""}, "Audio": {"value": ""}}},
        {"noteId": 3, "fields": {"Sentence": {"value": "text3"}, "Audio": {"value": ""}}},
        {"noteId": 4, "fields": {"Sentence": {"value": "text4"}, "Audio": {"value": ""}}},
        {"noteId": 5, "fields": {"Sentence": {"value": "text5"}, "Audio": {"value": ""}}},
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2, 3, 4, 5])
    mocker.patch("scripts.run_tts.get_note_info", return_value=notes)
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio", max_cards=2)

    assert mock_add_audio.call_count == 2
    mock_add_audio.assert_any_call(3, "Audio", "3.mp3", b"audio")
    mock_add_audio.assert_any_call(4, "Audio", "4.mp3", b"audio")


def test_max_cards_zero_raises() -> None:
    """Ensure max_cards=0 raises ValueError — processing zero cards is not meaningful."""

    with pytest.raises(ValueError, match="max_cards must be >= 1"):
        process_deck("MyDeck", "Sentence", "Audio", max_cards=0)


def test_max_cards_negative_raises() -> None:
    """Ensure a negative max_cards raises ValueError immediately."""

    with pytest.raises(ValueError, match="max_cards must be >= 1"):
        process_deck("MyDeck", "Sentence", "Audio", max_cards=-1)


def test_max_cards_larger_than_deck(mocker) -> None:
    """Ensure max_cards larger than deck size processes all available notes without error."""

    two_notes = [
        {"noteId": 1, "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": ""}}},
        {"noteId": 2, "fields": {"Sentence": {"value": "World"}, "Audio": {"value": ""}}},
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2])
    mocker.patch("scripts.run_tts.get_note_info", return_value=two_notes)
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    process_deck("MyDeck", "Sentence", "Audio", max_cards=100)

    assert mock_add_audio.call_count == 2


# =========================
# consecutive failure abort
# =========================

def test_aborts_after_max_consecutive_failures(mocker) -> None:
    """Ensure process_deck stops and returns False after N consecutive failures."""

    four_notes = [
        {"noteId": i, "fields": {"Sentence": {"value": f"text{i}"}, "Audio": {"value": ""}}}
        for i in range(1, 5)
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2, 3, 4])
    mocker.patch("scripts.run_tts.get_note_info", return_value=four_notes)
    mock_tts = mocker.patch("scripts.run_tts.synthesize_audio", side_effect=Exception("API error"))
    mocker.patch("scripts.run_tts.add_audio_to_note")

    result = process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=2)

    assert result is False
    assert mock_tts.call_count == 2


def test_consecutive_failure_counter_resets_on_success(mocker) -> None:
    """Ensure a successful addition resets the consecutive failure counter."""

    five_notes = [
        {"noteId": i, "fields": {"Sentence": {"value": f"text{i}"}, "Audio": {"value": ""}}}
        for i in range(1, 6)
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=list(range(1, 6)))
    mocker.patch("scripts.run_tts.get_note_info", return_value=five_notes)
    # fail, fail, succeed, fail, fail — never 3 consecutive failures
    mocker.patch(
        "scripts.run_tts.synthesize_audio",
        side_effect=[Exception("err"), Exception("err"), b"audio", Exception("err"), Exception("err")],
    )
    mock_add_audio = mocker.patch("scripts.run_tts.add_audio_to_note")

    result = process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=3)

    assert result is True
    mock_add_audio.assert_called_once()


def test_max_consecutive_failures_zero_raises() -> None:
    """Ensure max_consecutive_failures=0 raises ValueError — a threshold of zero is meaningless."""

    with pytest.raises(ValueError, match="max_consecutive_failures must be >= 1"):
        process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=0)


def test_max_consecutive_failures_negative_raises() -> None:
    """Ensure a negative max_consecutive_failures raises ValueError immediately."""

    with pytest.raises(ValueError, match="max_consecutive_failures must be >= 1"):
        process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=-1)


def test_abort_logs_clear_error_and_summary(mocker, caplog) -> None:
    """Ensure abort logs ❌ closing line, summary fires, and ✅ does not appear."""

    two_notes = [
        {"noteId": i, "fields": {"Sentence": {"value": f"text{i}"}, "Audio": {"value": ""}}}
        for i in range(1, 3)
    ]
    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2])
    mocker.patch("scripts.run_tts.get_note_info", return_value=two_notes)
    mocker.patch("scripts.run_tts.synthesize_audio", side_effect=Exception("quota exceeded"))
    mocker.patch("scripts.run_tts.add_audio_to_note")

    with caplog.at_level(logging.INFO):
        process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=2)

    assert "consecutive" in caplog.text.lower()
    assert "Added audio to 0 card(s)." in caplog.text
    assert "❌" in caplog.text
    assert "✅" not in caplog.text


def test_failed_note_logs_error_with_icon(mocker, caplog) -> None:
    """Ensure individual synthesis failures are logged with ❌ icon."""

    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[
        {"noteId": 1, "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": ""}}}
    ])
    mocker.patch("scripts.run_tts.synthesize_audio", side_effect=Exception("network error"))
    mocker.patch("scripts.run_tts.add_audio_to_note")

    with caplog.at_level(logging.ERROR):
        process_deck("MyDeck", "Sentence", "Audio", max_consecutive_failures=5)

    assert "❌" in caplog.text
    assert "Failed to process note 1" in caplog.text


# =========================
# Logging and progress bar
# =========================

def test_summary_log_reports_cards_added(mocker, caplog) -> None:
    """Ensure the summary log states how many cards received audio."""

    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1, 2])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[
        {"noteId": 1, "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": ""}}},
        {"noteId": 2, "fields": {"Sentence": {"value": "World"}, "Audio": {"value": ""}}},
    ])
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mocker.patch("scripts.run_tts.add_audio_to_note")

    with caplog.at_level(logging.INFO):
        process_deck("MyDeck", "Sentence", "Audio")

    assert "Added audio to 2 card(s)." in caplog.text


def test_progress_bar_desc_includes_max_cards(mocker) -> None:
    """Ensure the progress bar description mentions the cap when max_cards is set."""

    mock_client = object()
    mocker.patch("scripts.run_tts.init_tts_client", return_value=mock_client)
    mocker.patch("scripts.run_tts.get_notes_from_deck", return_value=[1])
    mocker.patch("scripts.run_tts.get_note_info", return_value=[
        {"noteId": 1, "fields": {"Sentence": {"value": "Hello"}, "Audio": {"value": ""}}}
    ])
    mocker.patch("scripts.run_tts.synthesize_audio", return_value=b"audio")
    mocker.patch("scripts.run_tts.add_audio_to_note")
    mock_iter = mocker.patch(
        "scripts.run_tts.iter_notes_with_progress",
        side_effect=lambda notes, desc: iter(notes),
    )

    process_deck("MyDeck", "Sentence", "Audio", max_cards=5)

    assert "max 5" in mock_iter.call_args.args[1]
