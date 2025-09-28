import pytest
from anki_tts.anki_tools import invoke, get_notes_from_deck, get_note_info, add_audio_to_note

# =========================
# Label: AnkiConnect - invoke
# =========================
def test_invoke_success(mocker):
    class MockResponse:
        def json(self):
            return {"result": 123, "error": None}

        def raise_for_status(self):
            return None  # no-op for success

    mocker.patch("requests.post", return_value=MockResponse())
    result = invoke("someAction", param=1)
    assert result == 123


def test_invoke_error(mocker):
    class MockResponse:
        def json(self):
            return {"result": None, "error": "Error message"}

        def raise_for_status(self):
            return None  # no-op

    mocker.patch("requests.post", return_value=MockResponse())
    with pytest.raises(RuntimeError):
        invoke("someAction", param=1)


# =========================
# Label: AnkiConnect - get_notes_from_deck
# =========================
def test_get_notes_from_deck(mocker):
    # Patch the invoke function from the package path
    mocker.patch("anki_tts.anki_tools.invoke", return_value=[1, 2, 3])
    notes = get_notes_from_deck("My Deck")
    assert notes == [1, 2, 3]


# =========================
# Label: AnkiConnect - get_note_info
# =========================
def test_get_note_info(mocker):
    fake_notes = [{"noteId": 1, "fields": {"Front": {"value": "Hello"}}}]
    mocker.patch("anki_tts.anki_tools.invoke", return_value=fake_notes)
    notes = get_note_info([1])
    assert notes[0]["noteId"] == 1


# =========================
# Label: AnkiConnect - add_audio_to_note
# =========================
def test_add_audio_to_note(mocker):
    mocker.patch("anki_tts.anki_tools.invoke", return_value=True)
    result = add_audio_to_note(1, "Front", "test.mp3", b"fakebytes")
    assert result is True
