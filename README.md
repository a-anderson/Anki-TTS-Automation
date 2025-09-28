# Anki TTS Automation

This tool automates the process of generating natural-sounding text-to-speech (TTS) audio for your Anki decks and attaches it directly to your cards via the [AnkiConnect add-on](https://ankiweb.net/shared/info/2055492159).

---

## Features

-   High-quality TTS (Google Wavenet)
-   Only adds missing audio by default (safe mode)
-   `--overwrite` option to regenerate all audio
-   Configurable voice

---

## Setup

### 1. Requirements

-   Anki with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) running
-   Python 3.9+
-   Google Cloud account with Text-to-Speech enabled

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Credentials

Download your service account JSON key and save it locally.
Set the environment variable (in `~/.zshrc` or `~/.bashrc`):

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/anki-tts-sa-key.json"
```

### 4. Run

#### 1. Default (Japanese deck, only missing audio)

```bash
python -m scripts.run_tts "My Deck" --text-field "Sentence" --audio-field "Audio"
```

-   Replace `My Japanese Deck` with your deck name
-   Replace `Sentence` with the field containing your Japanese text
-   Uses language: `ja-JP`
-   Voice: `ja-JP-Wavenet-B` (default)
-   Adds audio only if missing

#### 2. Overwrite existing audio

```bash
python -m scripts.run_tts "My Deck" --text-field "Sentence" --audio-field "Audio" --overwrite
```

-   Forces regeneration of audio for **all cards**, even if audio already exists

#### 3. Specify language

```bash
python -m scripts.run_tts "My English Deck" "Front" --language en-GB
```

-   Language: `en-GB`
-   Voice: `en-GB-Wavenet-F` (default for English)

```bash
python -m scripts.run_tts "French Phrases" "Phrase" --language fr-FR
```

-   Language: `fr-FR`
-   Voice: `fr-FR-Wavenet-F` (default for French)

#### 4. Specify custom voice

```bash
python -m scripts.run_tts "My English Deck" "Front" --language en-GB --voice en-GB-Wavenet-F
```

-   Language: `en-GB`
-   Voice: `en-GB-Wavenet-F`

#### 5. Adjust logging verbosity

```bash
python -m scripts.run_tts "My Deck" --text-field "Sentence" --audio-field "Audio" --log-level DEBUG
```

-   Shows detailed logs (each skipped note, API calls, etc.)

```bash
python -m scripts.run_tts "My Deck" --text-field "Sentence" --audio-field "Audio" --log-level ERROR
```

-   Only shows errors

Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default = `INFO`)

### Notes

-   Logs are shown in console for debugging
-   Default voice is `ja-JP-Wavenet-B`, override with `--voice`
