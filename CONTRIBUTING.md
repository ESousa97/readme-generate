# Contributing Guide

## Repository status
This repository is archived and no longer actively maintained.
It remains public for study purposes only.
There is no guarantee of response, review, merge, fix, or support.

## Development setup
1. Use Python 3.11+.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Code style and conventions
- Linting and formatting use `ruff` configured in `pyproject.toml`.
- Keep code cohesive, avoid dead code, and prefer small focused functions.
- Keep compatibility with existing GUI behavior.

## Branch and commit standards
- Branches: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`.
- Commits follow Conventional Commits:

```text
<type>(<scope>): <description>
```

Allowed types:
- `feat` new functionality
- `fix` bug fix
- `refactor` internal refactor with no behavior change
- `docs` documentation
- `style` formatting only
- `test` tests
- `chore` maintenance/dependencies/config
- `ci` CI/CD changes
- `perf` performance improvements
- `security` security fixes

## Pull request process
1. Keep PRs focused and small.
2. Run validation locally before opening PR:

```bash
make lint
make test
make build
```

3. Fill all fields in `PULL_REQUEST_TEMPLATE.md`.

## Community and contact
- Portfolio: https://enoquesousa.vercel.app
- GitHub: https://github.com/enoquesousa
