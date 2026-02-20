# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em Keep a Changelog e este projeto segue Semantic Versioning.

## [Unreleased]

## [1.1.0] - 2026-02-19
### Added
- Toolchain de qualidade com `ruff`, `pytest`, `pytest-cov` e `pip-audit`.
- `Makefile` com comandos padronizados para lint, testes, build, audit e validação.
- Testes unitários para lógica de prompt e utilitário de nomes de saída.
- Infraestrutura GitHub completa: templates de issue, template de PR, `CODEOWNERS`, `FUNDING.yml`.
- Workflows CI e auditoria de segurança com GitHub Actions.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` e documentação em `docs/`.
- `.editorconfig`, `.gitattributes`, `.env.example`, `requirements-dev.txt`, `pyproject.toml`.

### Changed
- Fortalecimento de `ConfigManager` com suporte a variáveis de ambiente (`GEMINI_API_KEY`, `GEMINI_MODEL`).
- Refatoração do entrypoint `run_app.py` para reduzir code smells e melhorar validações de dependência.
- Refino de `app_gui.py` para imports explícitos e tratamento de exceções mais robusto.
- Extração de ZIP mais segura em `logic.py` (ignora paths suspeitos e arquivos binários).
- Normalização de ignore rules e artefatos internos (`BASELINE.md`, `FINAL.md`).

### Removed
- Remoção de módulos legados PyQt5 não utilizados, reduzindo dívida técnica e superfície de manutenção.

### Fixed
- Correções de lint até estado limpo (`ruff check .`).
- Ajustes de robustez em tratamento de erros com encadeamento explícito (`raise ... from e`).

### Security
- Auditoria de dependências (`pip-audit`) integrada ao fluxo local e CI.
- Política de reporte de vulnerabilidades com SLA publicada em `SECURITY.md`.

## [1.0.2] - 2025-08-01
### Added
- Empacotamento via PyInstaller.
- Tema escuro e tema claro com detecção automática.
- Suporte a modelos Gemini.
- Interface com logs em tempo real e preview Markdown.
