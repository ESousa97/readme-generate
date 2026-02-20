# gerador_readme_ia/logger_setup.py
import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import Optional

from appdirs import user_log_dir

LOG_FILE_NAME_DEFAULT = "app.log"
DEFAULT_APP_AUTHOR = "Enoquesousa"  # Valor padrão direto para evitar importação circular


def setup_logging(logger_name: str,
                  debug: bool = False,
                  log_file_name: str = LOG_FILE_NAME_DEFAULT,
                  app_author: Optional[str] = None):
    """Configura o logging para a aplicação."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Evitar adicionar múltiplos handlers se já configurado e o logger já tem handlers.
    # Isso é importante se setup_logging for chamado múltiplas vezes para o mesmo logger_name.
    if logger.hasHandlers():
        # Se você quiser limpar e reconfigurar sempre, descomente:
        # logger.handlers.clear()
        # Ou, se quiser apenas retornar o logger já configurado:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if debug else logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler (logs persistentes)
    try:
        # Usa a parte principal de logger_name para o diretório de log.
        log_app_name_for_dir = logger_name.split('.')[0]
        current_app_author = app_author if app_author else DEFAULT_APP_AUTHOR

        log_dir = user_log_dir(log_app_name_for_dir, current_app_author)  # type: ignore
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file_path = os.path.join(log_dir, log_file_name)

        fh = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=3, encoding='utf-8')
        fh.setLevel(logging.DEBUG)  # Logar tudo (DEBUG e acima) no arquivo
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info(f"Logging para '{logger_name}' configurado. Arquivo de log: {log_file_path}")
    except Exception as e:
        # Usar print para stderr em caso de falha na configuração do logger,
        # pois o próprio logger pode não estar funcional.
        print(f"[CRITICAL_LOGGER_ERROR] Erro ao configurar o file handler do log para '{logger_name}': {e}\nTraceback: {traceback.format_exc()}", file=sys.stderr)
        print(f"[CRITICAL_LOGGER_ERROR] Logging de arquivo desabilitado para '{logger_name}'.", file=sys.stderr)

    return logger