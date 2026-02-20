# gerador_readme_ia/utils/file_helper.py
import logging
from pathlib import Path

from ..constants import APP_NAME

# Obter o logger configurado para este módulo
logger = logging.getLogger(f"{APP_NAME}.file_helper")

def get_readme_output_filename(zip_file_basename: str, output_dir: str) -> str:
    """
    Gera um nome de arquivo de saída para o README.md no diretório especificado,
    evitando sobrescrever arquivos existentes.
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de saída criado: {output_path}")
        except OSError as e:
            logger.error(f"Não foi possível criar o diretório de saída '{output_dir}': {e}. Usando diretório atual como fallback.", exc_info=True)
            output_path = Path(".")

    base_name_for_readme = Path(zip_file_basename).stem

    output_filename = output_path / f"{base_name_for_readme}_README.md"
    
    counter = 1
    temp_filename = output_filename
    while temp_filename.exists():
        temp_filename = output_path / f"{base_name_for_readme}_README_{counter}.md"
        counter += 1
    
    logger.debug(f"Nome do arquivo de saída do README definido como: {temp_filename}")
    return str(temp_filename)

def get_file_extension(file_path: str) -> str:
    """Retorna a extensão do arquivo em minúsculas."""
    return Path(file_path).suffix.lower()