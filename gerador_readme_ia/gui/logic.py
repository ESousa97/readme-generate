# gerador_readme_ia/gui/logic.py
"""Funções de domínio separadas – mantêm app_gui enxuto."""
from __future__ import annotations

import os
import zipfile
from typing import Dict, List, Callable, Optional

from ..constants import PROMPTS

PROMPT_README_GENERATION = PROMPTS["profissional"]  # fallback

# ------------------------------------------------------------------
# BUILD PROMPT ------------------------------------------------------
# ------------------------------------------------------------------

def build_prompt(project_data: str, config: Dict[str, object]) -> str:
    """Constrói um prompt customizado a partir da configuração avançada."""
    style_key = config.get("readme_style", "profissional").lower()
    base = PROMPTS.get(style_key, PROMPT_README_GENERATION)

    if config.get("custom_prompt_enabled") and (custom := config.get("custom_prompt", "").strip()):
        return f"{custom}\n\n=== Dados do Projeto Extraídos ===\n{project_data}"

    # acrescenta flags simples
    extras: List[str] = []
    if config.get("include_badges"):   extras.append("Inclua badges informativos.")
    if config.get("include_toc"):      extras.append("Inclua índice (Table of Contents).")
    if config.get("include_examples"): extras.append("Inclua exemplos de uso.")
    extras_txt = " " + " ".join(extras) if extras else ""

    return base.format(project_data=project_data) + extras_txt

# ------------------------------------------------------------------
# EXTRACT DATA ------------------------------------------------------
# ------------------------------------------------------------------

def extract_project_data_from_zip(
    zip_path: str,
    config: Dict[str, object],
    progress_cb: Optional[Callable[[str,int], None]] = None,
    step_cb: Optional[Callable[[str,str,str], None]] = None,
) -> str:
    """Extrai nomes de arquivos e primeiros bytes de cada arquivo relevante.
    Mantém implementação simples para evitar travar interface.
    
    CORRIGIDO: Progress callbacks agora funcionam corretamente
    """
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(zip_path)

    def emit_progress(msg: str, val: int):
        if progress_cb: 
            progress_cb(msg, val)
            print(f"[DEBUG] Progress: {msg} - {val}%")  # Debug temporário

    def emit_step(name: str, status: str, details: str = ""):
        if step_cb: 
            step_cb(name, status, details)
            print(f"[DEBUG] Step: {name} - {status} - {details}")  # Debug temporário

    emit_step("ZIP", "progress", "Abrindo arquivo…")
    emit_progress("Iniciando análise do arquivo ZIP", 5)

    data_parts: List[str] = []
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.infolist()
            total = len(members)
            max_files = config.get("max_files", 30)
            max_size = int(config.get("max_file_size_kb", 5)) * 1024

            emit_progress(f"Encontrados {total} arquivos no ZIP", 10)
            emit_step("Análise", "progress", f"{total} arquivos encontrados")

            # Processar arquivos
            files_to_process = min(total, max_files)
            for idx, info in enumerate(members[:max_files]):
                
                # Calcular progresso (10% a 80% da operação)
                progress_percent = int(10 + (70 * (idx + 1) / files_to_process))
                emit_progress(f"Processando {info.filename}", progress_percent)
                
                if info.is_dir():
                    continue
                    
                try:
                    with zf.open(info) as fp:
                        raw = fp.read(max_size)
                        try:
                            text = raw.decode("utf-8")
                        except UnicodeDecodeError:
                            text = raw.decode("latin-1", errors="ignore")
                        
                        if len(raw) == max_size:
                            text += "\n…[TRUNCADO]"
                            
                        data_parts.append(f"\n--- {info.filename} ---\n{text}")
                        
                        # Progresso incremental para arquivos grandes
                        if idx % 5 == 0:  # Atualizar a cada 5 arquivos
                            emit_step("Arquivo", "info", f"Processado: {info.filename}")
                            
                except Exception as e:
                    data_parts.append(f"\n--- {info.filename} (erro ao ler: {e}) ---\n")
                    emit_step("Erro", "warning", f"Erro em {info.filename}: {e}")

            emit_progress("Finalizando extração de dados", 85)
            emit_step("ZIP", "success", f"{min(total, max_files)} arquivos analisados")
            
    except Exception as e:
        emit_step("ZIP", "error", f"Erro ao processar ZIP: {e}")
        raise

    emit_progress("Dados extraídos com sucesso", 90)
    result = "\n".join(data_parts)
    
    # Log do tamanho final dos dados
    data_size_kb = len(result) // 1024
    emit_step("Dados", "success", f"Extraídos {data_size_kb}KB de dados")
    
    return result


# ------------------------------------------------------------------
# CLEAN README ------------------------------------------------------
# ------------------------------------------------------------------

def clean_readme_content(raw: str) -> str:
    """Limpa o conteúdo do README removendo delimitadores de código desnecessários"""
    if not raw: 
        return ""
    
    out = raw.strip()
    
    # Remove delimitadores de código markdown se envolvem todo o conteúdo
    if out.startswith("```"): 
        out = out.split("\n", 1)[-1]
    if out.endswith("```"):
        out = out.rsplit("```", 1)[0]
        
    return out.strip()
