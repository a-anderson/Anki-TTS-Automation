# Anki TTS Automation

This tool automates the process of generating natural-sounding text-to-speech (TTS) audio for your Anki decks and attaches it directly to your cards via the [AnkiConnect add-on](https://ankiweb.net/shared/info/2055492159).

---

## Table of Contents

-   [Features](#features)
-   [Project Structure](#project-structure)
-   [Setup](#setup)
    -   [Requirements](#1-requirements)
    -   [Install dependencies](#2-install-dependencies)
    -   [Configure Google Cloud Credentials](#3-configure-google-cloud-credentials)
    -   [Configure Anki + AnkiConnect](#4-configure-anki--ankiconnect)
-   [Usage](#usage)
    -   [Default Run](#1-default-japanese-deck-only-missing-audio)
    -   [Overwrite Existing Audio](#2-overwrite-existing-audio)
    -   [Specify Language](#3-specify-language)
    -   [Specify Custom Voice](#4-specify-custom-voice)
    -   [Adjust Logging Verbosity](#5-adjust-logging-verbosity)
-   [Development and Testing](#development-and-testing)
-   [Troubleshooting](#troubleshooting)
-   [Notes](#notes)
-   [Disclaimer](#disclaimer)
-   [License](#license)
-   [Author](#author)

---

## Features

-   High-quality speech synthesis with [**Google Cloud Text-to-Speech**](https://cloud.google.com/text-to-speech?hl=en)
-   Safely adds audio only where missing (default)
-   `--overwrite` option to regenerate audio for all cards
-   Multi-language support with configurable default voices
-   Flexible CLI: choose text field and audio field separately
-   Fully tested with `pytest` for maintainability
-   Modular project layout for clarity and extensibility

---

## Project Structure

```bash
anki-tts-automation/
├── anki_tts/            # Core Python package
│   ├── __init__.py
│   ├── anki_tools.py    # AnkiConnect API integration
│   ├── gcloud_tts.py    # Google TTS wrapper
│   ├── logging_utils.py # Tqdm logging handler
│   └── config.py        # Configuration & defaults
├── scripts/
│   └── run_tts.py       # CLI entry point
├── tests/               # Pytest suite
│   ├── test_anki_tools.py
│   ├── test_gcloud_tts.py
│   └── test_run_tts.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

This structure separates reusable library code (`anki_tts/`) from scripts (`scripts/`) and tests (`tests/`), following Python best practices.

---

## Setup

### 1. Requirements

-   Anki with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) running
-   Python 3.9+
-   Google Cloud account with **Text-to-Speech API** enabled

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

For development (with testing, etc)

```bash
pip install -r requirements-dev.txt
```

### 3. Configure Google Cloud Credentials

Download your service account JSON key and save it locally.
Set the environment variable (in `~/.zshrc` or `~/.bashrc`):

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/anki-tts-key.json"
```

This ensures the correct Google project credentials are used at runtime. If you work with multiple projects, switch by updating the environment variable before running `run_tts.py`.

> ⚠️ **Caution:** Google Cloud and the Text-to-Speech API are **NOT** free to use.  
> You are fully responsible for any costs incurred when using this tool.
>
> -   Please review the Text-to-Speech [API pricing information](https://cloud.google.com/text-to-speech/pricing?hl=en) before enabling or using the API.
> -   This project’s maintainers/authors accept **no responsibility** for charges that may occur as a result of your usage.
> -   To avoid unexpected costs, configure **budget alerts and quotas** in your Google Cloud account. See the [Google Cloud Billing documentation](https://cloud.google.com/billing/docs/how-to/budgets) for details.

### 4. Configure Anki + AnkiConnect

This tool requires Anki and the AnkiConnect add-on to be open and running.

1. Install and set up Anki

-   Download from the [Anki website](https://apps.ankiweb.net/)
-   Download a shared deck or create your own.

2. Install [AnkiConnect](https://ankiweb.net/shared/info/2055492159)

-   In Anki, go to `Tools → Add-ons → Get Add-ons`.
-   Enter the code: `2055492159`
-   Restart Anki.

3. Verify AnkiConnect is working

-   Open a browser and visit: http://localhost:8765
-   You should see
    ```json
    { "error": "missing action", "result": null }
    ```

> ℹ️ By default, AnkiConnect listens on http://localhost:8765. You can change this in its config if needed.

---

## Usage

Run the CLI via:

#### 1. Default (Japanese deck, only missing audio)

```bash
python -m scripts.run_tts "My Deck" \
    --text-field "Sentence" \
    --audio-field "Audio"
```

-   Replace `My Japanese Deck` with your deck name
-   Replace `Sentence` with the field containing your Japanese text
-   Uses language: `ja-JP`
-   Voice: `ja-JP-Wavenet-B` (default)
-   Adds audio only if missing

#### 2. Overwrite existing audio

```bash
python -m scripts.run_tts "My Deck" \
    --text-field "Sentence" \
    --audio-field "Audio" \
    --overwrite
```

-   Forces regeneration of audio for **all cards**, even if audio already exists

#### 3. Specify language

```bash
python -m scripts.run_tts "My English Deck" \
    --text-field "Front" \
    --audio-field "Audio" \
    --language en-GB
```

-   Language: `en-GB`
-   Voice: `en-GB-Wavenet-F` (default for English)

```bash
python -m scripts.run_tts "French Phrases" \
    --text-field "Phrase" \
    --audio-field "Audio" \
    --language fr-FR
```

-   Language: `fr-FR`
-   Voice: `fr-FR-Wavenet-F` (default for French)

#### 4. Specify custom voice

```bash
python -m scripts.run_tts "My English Deck" \
    --text-field "Front" \
    --audio-field "Audio" \
    --language en-GB \
    --voice en-GB-Wavenet-F
```

-   Language: `en-GB`
-   Voice: `en-GB-Wavenet-F`

#### 5. Adjust logging verbosity

```bash
python -m scripts.run_tts "My Deck" \
    --text-field "Sentence" \
    --audio-field "Audio" \
    --log-level DEBUG
```

-   Shows detailed logs (each skipped note, API calls, etc.)

```bash
python -m scripts.run_tts "My Deck" \
    --text-field "Sentence" \
    --audio-field "Audio" \
    --log-level ERROR
```

-   Only shows errors

Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default = `INFO`)

### Development and Testing

Run all tests:

```bash
pytest
```

Run tests with detailed output:

```bash
pytest -v
```

Collect tests (without running):

```bash
pytest --collect-only
```

---

## Troubleshooting

### AnkiConnect not responding

-   Make sure Anki is open and running while you use this tool.
-   Check that AnkiConnect is installed (`Tools → Add-ons`).
-   Test by visiting [http://localhost:8765](http://localhost:8765) in your browser.  
    You should see:
    ```json
    { "error": "missing action", "result": null }
    ```

### Port conflicts

-   By default, AnkiConnect listens on port `8765`.
-   If another service is using this port, update the port in AnkiConnect’s config (`Tools → Add-ons → AnkiConnect → Config`) and in this tool’s `ANKI_CONNECT_URL` (via your `.env` file).

### Google Cloud authentication errors

-   Check that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set.
-   Make sure the path points to the correct `.json` key file.
-   Verify that your Google Cloud project has the **Text-to-Speech API enabled**.

### Audio not being added

-   Confirm you specified both `--text-field` and `--audio-field` and that they are correct.
-   If `--overwrite` is not set, notes with existing audio will be skipped (use `--log-level DEBUG` to confirm).
-   Ensure the audio field exists in your Anki note type.

### Still stuck?

-   Run with `--log-level DEBUG` for detailed output.
-   Check the AnkiConnect documentation for advanced config.

---

## Notes

-   Logs are shown in console for debugging
-   No local caching of MP3 files is performed — audio is streamed directly to Anki
-   By design, this tool never mutates your text fields, only updates the audio field

---

## Disclaimer

This project is provided "as is" without warranty of any kind.  
By using this tool, you acknowledge and agree that:

-   You are solely responsible for configuring and using Google Cloud services.
-   All costs associated with Google Cloud, including but not limited to usage of the Text-to-Speech API, are your responsibility.
-   The project maintainers/authors are not liable for any financial charges, data loss, or other issues that may arise from using this software.

Before use, please carefully review the [Google Cloud pricing documentation](https://cloud.google.com/text-to-speech/pricing?hl=en) and configure [budget alerts and quotas](https://cloud.google.com/billing/docs/how-to/budgets) to prevent unexpected charges.

---

## License

[MIT](LICENSE) — free to use, modify, and share.

## Author

Developed by [Ashley Anderson](https://github.com/a-anderson)
