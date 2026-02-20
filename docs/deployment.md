# Deployment Notes

## Distribution model
This project is a desktop app. The usual deployment path is packaging for end users.

## Packaging baseline
- Use PyInstaller with existing project conventions.
- Validate startup, generation flow, and file save behavior after build.

## Security checks before release
- Run `python -m pip_audit`.
- Ensure no `.env` or secrets are present in repository or build artifacts.
- Review dependencies and changelog before publishing.

## Release checklist
1. `make validate`
2. `make audit`
3. Update `CHANGELOG.md`
4. Tag release using SemVer
