# gerador_readme_ia/config_manager.py
import configparser
import os
from appdirs import user_config_dir
import logging
from typing import Optional # <--- IMPORTAÇÃO ADICIONADA

from .constants import (
    APP_NAME, APP_AUTHOR, CONFIG_FILE_NAME,
    CONFIG_SECTION_API, CONFIG_KEY_API_KEY, CONFIG_KEY_MODEL, DEFAULT_GEMINI_MODEL
)

# Logger será configurado pelo módulo que o importa ou pelo entry point.
# Se este arquivo for executado como __main__, o logger pode não estar totalmente configurado.
logger = logging.getLogger(f"{APP_NAME}.config_manager")

class ConfigManager:
    def __init__(self):
        # Usar constantes para garantir consistência
        self.app_name_const = APP_NAME
        self.app_author_const = APP_AUTHOR
        self.config_file_name_const = CONFIG_FILE_NAME

        self.config_dir = user_config_dir(self.app_name_const, self.app_author_const)
        self.config_file_path = os.path.join(self.config_dir, self.config_file_name_const)
        self.config = configparser.ConfigParser()
        
        self._ensure_config_dir_exists()
        self._load_config()
        logger.debug(f"ConfigManager inicializado. Arquivo de config: {self.config_file_path}")

    def _ensure_config_dir_exists(self):
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir, exist_ok=True) # exist_ok=True para segurança
                logger.info(f"Diretório de configuração criado ou já existente: {self.config_dir}")
            except OSError as e:
                logger.error(f"Não foi possível criar o diretório de configuração {self.config_dir}: {e}", exc_info=True)
                raise # Re-levantar a exceção para sinalizar falha crítica

    def _load_config(self):
        if os.path.exists(self.config_file_path):
            self.config.read(self.config_file_path, encoding='utf-8')
            logger.info(f"Configuração carregada de: {self.config_file_path}")
        else:
            logger.info(f"Arquivo de configuração não encontrado em '{self.config_file_path}'. Será criado na primeira gravação ou quando uma seção for adicionada.")
        
        # Sempre garantir que a seção API exista
        if not self.config.has_section(CONFIG_SECTION_API):
            self.config.add_section(CONFIG_SECTION_API)
            logger.debug(f"Seção de configuração '{CONFIG_SECTION_API}' adicionada pois não existia.")


    def _save_config(self):
        try:
            # Garante que o diretório de configuração ainda exista antes de salvar
            self._ensure_config_dir_exists()
            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            logger.info(f"Configuração salva em: {self.config_file_path}")
        except IOError as e:
            logger.error(f"Não foi possível salvar o arquivo de configuração {self.config_file_path}: {e}", exc_info=True)
            # Considerar se deve re-levantar a exceção dependendo da criticidade
            # raise

    def get_api_key(self) -> Optional[str]:
        return self.config.get(CONFIG_SECTION_API, CONFIG_KEY_API_KEY, fallback=None)

    def set_api_key(self, api_key: str):
        # A seção já deve existir devido ao _load_config
        self.config.set(CONFIG_SECTION_API, CONFIG_KEY_API_KEY, api_key)
        self._save_config()
        logger.info("API Key salva na configuração.")

    def get_gemini_model(self) -> str:
        return self.config.get(CONFIG_SECTION_API, CONFIG_KEY_MODEL, fallback=DEFAULT_GEMINI_MODEL)

    def set_gemini_model(self, model_name: str):
        self.config.set(CONFIG_SECTION_API, CONFIG_KEY_MODEL, model_name)
        self._save_config()
        logger.info(f"Modelo Gemini '{model_name}' salvo na configuração.")

    # Os métodos ensure_* são mais para CLI. Para GUI, essa lógica é tratada nos diálogos.
    # Se for manter uma CLI funcional, eles precisariam ser adaptados ou chamados de um contexto CLI.

# Bloco if __name__ == "__main__": removido para evitar dependência de logger_setup
# se este arquivo for executado diretamente sem o contexto da aplicação.
# Testes unitários são uma forma melhor de testar esta classe isoladamente.