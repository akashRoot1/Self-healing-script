# Self-healing-script

`Self-healing-script` is a Python demo project that shows how UI test automation can recover from broken selectors.

## What this project does

- Serves a small Flask app with a primary action button whose label changes often.
- Uses a `SelfHealer` helper to:
  - try the original Playwright locator,
  - fall back to cached healed locators,
  - ask Ollama for a better locator,
  - and finally use fuzzy matching as a fallback.
- Demonstrates locator healing with a Playwright-based test script.

## Project structure

- `/home/runner/work/Self-healing-script/Self-healing-script/app.py` – demo web app with changing button text.
- `/home/runner/work/Self-healing-script/Self-healing-script/healer.py` – core self-healing locator logic.
- `/home/runner/work/Self-healing-script/Self-healing-script/simple_test.py` – demo Playwright script that uses `SelfHealer`.
- `/home/runner/work/Self-healing-script/Self-healing-script/requirements.txt` – Python dependencies.

## Requirements

- Python 3.10+ (recommended)
- Playwright browser binaries installed
- Optional: local Ollama runtime (for LLM-based healing step)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browser binaries:

   ```bash
   python -m playwright install
   ```

## Run the demo app

```bash
python app.py
```

The app starts at `http://localhost:5000`.

## Run the self-healing test

In a second terminal (while the app is running):

```bash
python simple_test.py
```

The script opens a browser, attempts to click the primary action using a fragile locator, and then heals it when needed.

## Notes

- If Ollama is not installed or available, healing still works via fuzzy matching fallback.
- `SelfHealer` keeps an in-memory cache of successful healed locators during runtime.
