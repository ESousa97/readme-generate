from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QTextEdit,
    QSpinBox, QLabel, QScrollArea, QComboBox
)

def create_settings_tab():
    # --- Widget raiz da aba (para o QTabWidget) ------------------------
    settings_widget = QWidget()
    scroll_area = QScrollArea()          # será adicionado à aba
    scroll_area.setWidget(settings_widget)
    scroll_area.setWidgetResizable(True)

    layout = QVBoxLayout(settings_widget)

    # -------- 1) PROMPT PERSONALIZADO ---------------------------------
    prompt_group = QGroupBox("Personalização do Prompt")
    prompt_layout = QVBoxLayout(prompt_group)
    custom_prompt_enabled = QCheckBox("Usar prompt personalizado")
    custom_prompt_text = QTextEdit()
    custom_prompt_text.setPlaceholderText("Digite aqui instruções específicas para a IA…")
    custom_prompt_text.setMaximumHeight(150)
    custom_prompt_text.setEnabled(False)
    custom_prompt_enabled.toggled.connect(custom_prompt_text.setEnabled)
    prompt_layout.addWidget(custom_prompt_enabled)
    prompt_layout.addWidget(custom_prompt_text)

    # -------- 2) FILTROS DE ARQUIVO -----------------------------------
    filter_group = QGroupBox("Filtros de Arquivo")
    filter_layout = QVBoxLayout(filter_group)

    include_tests   = QCheckBox("Incluir arquivos de teste");          include_tests.setChecked(True)
    include_docs    = QCheckBox("Incluir documentação existente");     include_docs.setChecked(True)
    include_config  = QCheckBox("Incluir arquivos de configuração");   include_config.setChecked(True)

    max_file_size_label = QLabel("Tamanho máximo por arquivo (KB):")
    max_file_size_spin  = QSpinBox(); max_file_size_spin.setRange(1, 100); max_file_size_spin.setValue(5); max_file_size_spin.setSuffix(" KB")

    max_files_label = QLabel("Máximo de arquivos para análise:")
    max_files_spin  = QSpinBox(); max_files_spin.setRange(5, 100); max_files_spin.setValue(30)

    for w in (include_tests, include_docs, include_config,
              max_file_size_label, max_file_size_spin,
              max_files_label, max_files_spin):
        filter_layout.addWidget(w)

    # -------- 3) ESTILO DO README -------------------------------------
    style_group = QGroupBox("Estilo do README")
    style_layout = QVBoxLayout(style_group)
    readme_style_label = QLabel("Estilo:")

    readme_style_combo = QComboBox()
    readme_style_combo.addItems([
        "Profissional", "Detalhado", "Minimalista", "Tutorial", "Open Source"
    ])

    include_badges   = QCheckBox("Incluir badges");   include_badges.setChecked(True)
    include_toc      = QCheckBox("Incluir índice (TOC)"); include_toc.setChecked(True)
    include_examples = QCheckBox("Incluir exemplos de uso"); include_examples.setChecked(True)

    for w in (readme_style_label, readme_style_combo,
              include_badges, include_toc, include_examples):
        style_layout.addWidget(w)

    # ---- adiciona aos layouts principais -----------------------------
    for grp in (prompt_group, filter_group, style_group):
        layout.addWidget(grp)
    layout.addStretch()

    # ---------- Dicionário de CONTROLES para acesso externo -----------
    controls = {
        "custom_prompt_enabled": custom_prompt_enabled,
        "custom_prompt_text":    custom_prompt_text,
        "include_tests":         include_tests,
        "include_docs":          include_docs,
        "include_config":        include_config,
        "max_file_size_spin":    max_file_size_spin,
        "max_files_spin":        max_files_spin,
        "readme_style_combo":    readme_style_combo,
        "include_badges":        include_badges,
        "include_toc":           include_toc,
        "include_examples":      include_examples,
    }

    # ------------------------------------------------------------------
    #  ➜ Retorne (widget_da_aba, dicionario_com_controles)
    return scroll_area, controls
