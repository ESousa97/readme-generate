from pathlib import Path

from gerador_readme_ia.utils.file_helper import get_file_extension, get_readme_output_filename


def test_get_file_extension_returns_lowercase() -> None:
  assert get_file_extension("arquivo.MD") == ".md"


def test_get_readme_output_filename_appends_counter_when_file_exists(tmp_path: Path) -> None:
  first = tmp_path / "repo_README.md"
  first.write_text("x", encoding="utf-8")

  output = get_readme_output_filename("repo.zip", str(tmp_path))

  assert output.endswith("repo_README_1.md")
