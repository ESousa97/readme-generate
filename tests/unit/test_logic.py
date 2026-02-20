from gerador_readme_ia.gui.logic import build_prompt, clean_readme_content


def test_clean_readme_content_removes_fence_wrapper() -> None:
  raw = "```markdown\n# Titulo\n```"
  cleaned = clean_readme_content(raw)
  assert cleaned == "# Titulo"


def test_build_prompt_with_custom_prompt_appends_project_data() -> None:
  prompt = build_prompt(
    "dados do projeto",
    {
      "custom_prompt_enabled": True,
      "custom_prompt": "PROMPT CUSTOM",
      "readme_style": "profissional",
    },
  )

  assert "PROMPT CUSTOM" in prompt
  assert "dados do projeto" in prompt


def test_build_prompt_with_flags_adds_expected_sections() -> None:
  prompt = build_prompt(
    "dados do projeto",
    {
      "readme_style": "profissional",
      "include_badges": True,
      "include_toc": True,
      "include_examples": False,
    },
  )

  assert "Inclua badges informativos." in prompt
  assert "Inclua índice" in prompt
