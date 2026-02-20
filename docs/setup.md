# Setup Guide

## Requirements
- Python 3.11+
- pip

## Local setup
```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Environment variables
Create `.env` from `.env.example` and set at least:
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional, default `gemini-1.5-flash`)
- `APP_DEBUG` (optional)

## Validation commands
```bash
make lint
make test
make build
make audit
```
