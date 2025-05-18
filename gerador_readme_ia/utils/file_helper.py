# gerador_readme_ia/utils/file_helper.py
import os
import logging
from ..constants import APP_NAME, APP_AUTHOR # Importar APP_AUTHOR também se usado pelo logger
# from ..logger_setup import setup_logging # Módulos não devem chamar setup_logging diretamente, exceto o principal

# Obter o logger configurado para este módulo
logger = logging.getLogger(f"{APP_NAME}.file_helper")

def get_readme_output_filename(zip_file_basename: str, output_dir: str) -> str:
    """
    Gera um nome de arquivo de saída para o README.md no diretório especificado,
    evitando sobrescrever arquivos existentes.
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"Diretório de saída criado: {output_dir}")
        except OSError as e:
            logger.error(f"Não foi possível criar o diretório de saída '{output_dir}': {e}. Usando diretório atual como fallback.", exc_info=True)
            output_dir = "." # Fallback para o diretório atual

    # Remove a extensão .zip se presente para o nome base
    base_name_for_readme = zip_file_basename.replace(".zip", "")
    
    output_filename = os.path.join(output_dir, f"{base_name_for_readme}_README.md")
    
    counter = 1
    temp_filename = output_filename
    while os.path.exists(temp_filename):
        temp_filename = os.path.join(output_dir, f"{base_name_for_readme}_README_{counter}.md")
        counter += 1
    
    logger.debug(f"Nome do arquivo de saída do README definido como: {temp_filename}")
    return temp_filename

def get_file_extension(file_path: str) -> str:
    """Retorna a extensão do arquivo em minúsculas."""
    return os.path.splitext(file_path)[1].lower()

# Função antiga get_output_filename removida ou renomeada para get_readme_output_filename
# Se você ainda precisar da antiga para PDFs (o que não parece ser o caso), mantenha-a com outro nome.