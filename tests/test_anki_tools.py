import pytest
from anki_tts.anki_tools import invoke, get_notes_from_deck, get_note_info, add_audio_to_note

# =========================
# AnkiConnect - invoke
# =========================
def test_invoke_success(mocker) -> None:
    """Test that invoke() returns the correct result when AnkiConnect responds successfully."""
    class MockResponse:
        def json(self) -> dict:
            return {"result": 123, "error": None}

        def raise_for_status(self) -> None:
            return None  # no-op for success

    mocker.patch("requests.post", return_value=MockResponse())
    result = invoke("someAction", param=1)
    assert result == 123


def test_invoke_error(mocker) -> None:
    """Test that invoke() raises RuntimeError when AnkiConnect returns an error."""
    class MockResponse:
        def json(self) -> dict:
            return {"result": None, "error": "Error message"}

        def raise_for_status(self) -> None:
            return None  # no-op

    mocker.patch("requests.post", return_value=MockResponse())
    with pytest.raises(RuntimeError):
        invoke("someAction", param=1)


# =========================
# AnkiConnect - get_notes_from_deck
# =========================
def test_get_notes_from_deck(mocker) -> None:
    """Test that get_notes_from_deck() returns note IDs when invoke() is patched."""
    # Patch the invoke function from the package path
    mocker.patch("anki_tts.anki_tools.invoke", return_value=[1, 2, 3])
    notes = get_notes_from_deck("My Deck")
    assert notes == [1, 2, 3]


# =========================
# AnkiConnect - get_note_info
# =========================
def test_get_note_info(mocker) -> None:
    """Test that get_note_info() returns note information."""
    fake_notes = [{"noteId": 1, "fields": {"Front": {"value": "Hello"}}}]
    mocker.patch("anki_tts.anki_tools.invoke", return_value=fake_notes)
    notes = get_note_info([1])
    assert notes[0]["noteId"] == 1


# =========================
# AnkiConnect - add_audio_to_note
# =========================
def test_add_audio_to_note(mocker) -> None:
    """Test that add_audio_to_note() calls invoke() with the correct parameters."""
    mocker.patch("anki_tts.anki_tools.invoke", return_value=True)
    result = add_audio_to_note(1, "Front", "test.mp3", b"fakebytes")
    assert result is True
