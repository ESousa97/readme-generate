# gerador_readme_ia/config_manager.py
import configparser
import os
from appdirs import user_config_dir
import logging
from typing import Optional

from .constants import (
    APP_NAME, APP_AUTHOR, CONFIG_FILE_NAME,
    CONFIG_SECTION_API, CONFIG_KEY_API_KEY, CONFIG_KEY_MODEL, DEFAULT_GEMINI_MODEL
)

logger = logging.getLogger(f"{APP_NAME}.config_manager")

class ConfigManager:
    def __init__(self):
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
                os.makedirs(self.config_dir, exist_ok=True)
                logger.info(f"Diretório de configuração criado: {self.config_dir}")
            except OSError as e:
                logger.error(f"Não foi possível criar o diretório de configuração {self.config_dir}: {e}", exc_info=True)
                raise

    def _load_config(self):
        if os.path.exists(self.config_file_path):
            try:
                self.config.read(self.config_file_path, encoding='utf-8')
                logger.info(f"Configuração carregada de: {self.config_file_path}")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração de {self.config_file_path}: {e}", exc_info=True)
                # Criar configuração vazia em caso de erro
                self.config = configparser.ConfigParser()
        else:
            logger.info(f"Arquivo de configuração não encontrado em '{self.config_file_path}'. Será criado na primeira gravação.")
        
        # Sempre garantir que a seção API exista
        if not self.config.has_section(CONFIG_SECTION_API):
            self.config.add_section(CONFIG_SECTION_API)
            logger.debug(f"Seção de configuração '{CONFIG_SECTION_API}' adicionada.")

    def _save_config(self):
        try:
            self._ensure_config_dir_exists()
            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            logger.info(f"Configuração salva em: {self.config_file_path}")
        except IOError as e:
            logger.error(f"Não foi possível salvar o arquivo de configuração {self.config_file_path}: {e}", exc_info=True)
            raise

    def get_api_key(self) -> Optional[str]:
        """Obtém a API Key salva"""
        try:
            api_key = self.config.get(CONFIG_SECTION_API, CONFIG_KEY_API_KEY, fallback=None)
            if api_key and api_key.strip():
                return api_key.strip()
            return None
        except Exception as e:
            logger.error(f"Erro ao obter API Key: {e}")
            return None

    def set_api_key(self, api_key: str):
        """Salva a API Key"""
        if not api_key or not api_key.strip():
            logger.warning("Tentativa de salvar API Key vazia")
            return
            
        try:
            self.config.set(CONFIG_SECTION_API, CONFIG_KEY_API_KEY, api_key.strip())
            self._save_config()
            logger.info("API Key salva na configuração.")
        except Exception as e:
            logger.error(f"Erro ao salvar API Key: {e}", exc_info=True)
            raise

    def get_gemini_model(self) -> str:
        """Obtém o modelo Gemini configurado"""
        try:
            model = self.config.get(CONFIG_SECTION_API, CONFIG_KEY_MODEL, fallback=DEFAULT_GEMINI_MODEL)
            return model if model and model.strip() else DEFAULT_GEMINI_MODEL
        except Exception as e:
            logger.error(f"Erro ao obter modelo Gemini: {e}")
            return DEFAULT_GEMINI_MODEL

    def set_gemini_model(self, model_name: str):
        """Salva o modelo Gemini"""
        if not model_name or not model_name.strip():
            logger.warning("Tentativa de salvar modelo vazio")
            return
            
        try:
            self.config.set(CONFIG_SECTION_API, CONFIG_KEY_MODEL, model_name.strip())
            self._save_config()
            logger.info(f"Modelo Gemini '{model_name}' salvo na configuração.")
        except Exception as e:
            logger.error(f"Erro ao salvar modelo Gemini: {e}", exc_info=True)
            raise

    def clear_api_key(self):
        """Remove a API Key da configuração"""
        try:
            if self.config.has_option(CONFIG_SECTION_API, CONFIG_KEY_API_KEY):
                self.config.remove_option(CONFIG_SECTION_API, CONFIG_KEY_API_KEY)
                self._save_config()
                logger.info("API Key removida da configuração.")
        except Exception as e:
            logger.error(f"Erro ao remover API Key: {e}", exc_info=True)

    def has_valid_config(self) -> bool:
        """Verifica se há uma configuração válida"""
        api_key = self.get_api_key()
        model = self.get_gemini_model()
        return bool(api_key and model)

    def get_config_file_path(self) -> str:
        """Retorna o caminho do arquivo de configuração"""
        return self.config_file_path