import pytest
import os
from anki_tts.gcloud_tts import synthesize_audio, init_tts_client

# =========================
# Label: Google TTS - init_tts_client
# =========================
def test_init_tts_client_success(mocker, tmp_path):
    # Create a fake credentials file
    cred_file = tmp_path / "fake_key.json"
    cred_file.write_text("{}")

    # Patch the env var
    mocker.patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": str(cred_file)})

    # Patch the actual client to avoid real API calls
    mock_client = object()
    mocker.patch("anki_tts.gcloud_tts.texttospeech.TextToSpeechClient", return_value=mock_client)

    client = init_tts_client()
    assert client == mock_client


def test_init_tts_client_missing_env(mocker):
    # Ensure env var is not set
    mocker.patch.dict(os.environ, {}, clear=True)

    with pytest.raises(EnvironmentError, match="GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"):
        init_tts_client()


def test_init_tts_client_invalid_path(mocker, tmp_path):
    # Point to a non-existent file
    fake_path = tmp_path / "does_not_exist.json"
    mocker.patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": str(fake_path)})

    with pytest.raises(EnvironmentError, match="GOOGLE_APPLICATION_CREDENTIALS path does not exist"):
        init_tts_client()


def test_init_tts_client_failure(mocker):
    mocker.patch(
        "anki_tts.gcloud_tts.texttospeech.TextToSpeechClient",
        side_effect=Exception("Failed to init")
    )
    with pytest.raises(Exception):
        init_tts_client()


# =========================
# Label: Google TTS - synthesize_audio
# =========================
def test_synthesize_audio_returns_bytes(mocker):
    # Create a mock client instance
    mock_client = mocker.MagicMock()

    # Mock the synthesize_speech method to return a fake response
    class MockResponse:
        audio_content = b"fake_audio_data"

    mock_client.synthesize_speech.return_value = MockResponse()

    # Call synthesize_audio with the mock client
    result = synthesize_audio("こんにちは", mock_client)

    # Assert the returned bytes are as expected
    assert result == b"fake_audio_data"

def test_synthesize_audio_with_custom_voice(mocker):
    mock_client = mocker.MagicMock()

    class MockResponse:
        audio_content = b"voice_audio_data"

    mock_client.synthesize_speech.return_value = MockResponse()

    result = synthesize_audio("Hello", mock_client, language_code="en-GB", voice_name="en-GB-Wavenet-F")
    assert result == b"voice_audio_data"
    # Ensure synthesize_speech was called exactly once
    mock_client.synthesize_speech.assert_called_once()