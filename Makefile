PYTHON=.venv/Scripts/python.exe

.PHONY: install install-dev lint lint-fix format test test-coverage build audit start validate

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check .

lint-fix:
	$(PYTHON) -m ruff check . --fix

format:
	$(PYTHON) -m ruff format .

test:
	$(PYTHON) -m pytest

test-coverage:
	$(PYTHON) -m pytest --cov=gerador_readme_ia --cov-report=term-missing

build:
	$(PYTHON) -m compileall gerador_readme_ia run_app.py

audit:
	$(PYTHON) -m pip_audit

start:
	$(PYTHON) run_app.py

validate: lint test build
