# Architecture Overview

## Context
`readme-generate` is a desktop application that processes a ZIP project and uses Gemini to generate a README draft.

## High-level modules
- `run_app.py`: startup entry point and dependency checks.
- `gerador_readme_ia/gui/app_gui.py`: UI orchestration and user flows.
- `gerador_readme_ia/gui/logic.py`: domain logic for prompt building and ZIP analysis.
- `gerador_readme_ia/config_manager.py`: persistent configuration and environment overrides.
- `gerador_readme_ia/ia_client/gemini_client.py`: Gemini API integration.
- `gerador_readme_ia/utils/file_helper.py`: output naming and path utilities.

## Runtime flow
1. User starts the app (`run_app.py`).
2. GUI loads config and validates API key/model.
3. User selects ZIP and generation options.
4. `logic.py` extracts safe textual data from ZIP.
5. Prompt is composed and sent to Gemini client.
6. Generated README is rendered and can be saved.

## Design decisions
- Security-first ZIP processing: suspicious paths and binary files are ignored.
- API key can be provided by environment variables (`GEMINI_API_KEY`) to avoid local file persistence when desired.
- Legacy PyQt modules were removed to reduce maintenance surface.
