# gerador_readme_ia/ia_client/gemini_client.py
import logging
from typing import Any, Optional

import google.generativeai as genai

from ..constants import APP_NAME

logger = logging.getLogger(f"{APP_NAME}.gemini_client")

class QuotaExceededException(Exception):
    """Exceção específica para quota excedida"""
    def __init__(self, message, model_name=None):
        self.model_name = model_name
        super().__init__(message)

class GeminiClient:
    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        if model_name.startswith("models/"):
            return model_name
        return f"models/{model_name}"

    @staticmethod
    def _is_quota_error(error: Exception) -> bool:
        error_msg = str(error).lower()
        return "quota" in error_msg or "429" in error_msg

    @staticmethod
    def _build_safety_settings() -> list[dict[str, str]]:
        return [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

    @staticmethod
    def _extract_text_from_parts(parts: Any) -> Optional[str]:
        if not parts:
            return None

        combined_text = ""
        for part in parts:
            if hasattr(part, "text") and part.text:
                combined_text += part.text

        return combined_text or None

    @classmethod
    def _extract_text_from_candidates(cls, candidates: Any) -> Optional[str]:
        if not candidates:
            return None

        for candidate in candidates:
            if not hasattr(candidate, "content") or not candidate.content:
                continue
            if not hasattr(candidate.content, "parts"):
                continue

            candidate_text = cls._extract_text_from_parts(candidate.content.parts)
            if candidate_text:
                return candidate_text

        return None

    @staticmethod
    def _extract_response_text(response: Any) -> Optional[str]:
        if hasattr(response, "text") and response.text:
            return response.text

        direct_parts_text = GeminiClient._extract_text_from_parts(getattr(response, "parts", None))
        if direct_parts_text:
            return direct_parts_text

        return GeminiClient._extract_text_from_candidates(getattr(response, "candidates", None))

    def _raise_quota_exception(self, model_name: str, original_error: Exception) -> None:
        display_name = model_name.replace("models/", "")
        raise QuotaExceededException(
            f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
            display_name,
        ) from original_error

    @staticmethod
    def _model_supports_generation(model: Any, expected_name: str) -> bool:
        if not hasattr(model, "name") or model.name != expected_name:
            return False
        if not hasattr(model, "supported_generation_methods"):
            return True
        return "generateContent" in model.supported_generation_methods

    def _validate_model_availability(self, model_name: str) -> None:
        try:
            available_models = list(genai.list_models())
            if any(self._model_supports_generation(model, model_name) for model in available_models):
                return
            raise ValueError(f"Modelo '{model_name}' não encontrado ou não suporta generateContent")
        except Exception as error:
            if self._is_quota_error(error):
                self._raise_quota_exception(model_name, error)
            logger.warning(f"Não foi possível verificar disponibilidade do modelo: {error}")

    @staticmethod
    def _raise_if_blocked(response: Any, context: str) -> None:
        if not hasattr(response, "prompt_feedback") or not response.prompt_feedback:
            return
        if not hasattr(response.prompt_feedback, "block_reason") or not response.prompt_feedback.block_reason:
            return

        block_reason_str = str(response.prompt_feedback.block_reason)
        logger.error(f"{context} bloqueado pelo Gemini. Razão: {block_reason_str}")
        if hasattr(response.prompt_feedback, "safety_ratings") and response.prompt_feedback.safety_ratings:
            for rating in response.prompt_feedback.safety_ratings:
                logger.error(f"  Safety Rating: Category={rating.category}, Probability={rating.probability}")
        raise ValueError(f"PROMPT BLOQUEADO PELA IA. Razão: {block_reason_str}")

    def _map_init_exception(self, model_name: str, error: Exception) -> Exception:
        error_msg = str(error)
        if self._is_quota_error(error):
            display_name = model_name.replace("models/", "")
            return QuotaExceededException(
                f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                display_name,
            )
        if "404" in error_msg or "not found" in error_msg.lower():
            return ConnectionError(
                f"Modelo '{model_name}' não encontrado. Verifique se você tem acesso a este modelo com sua API Key."
            )
        if "403" in error_msg or "permission" in error_msg.lower():
            return ConnectionError(
                f"Sem permissão para usar o modelo '{model_name}'. Verifique sua API Key e quota."
            )
        if "401" in error_msg:
            return ConnectionError("API Key inválida ou expirada.")
        return ConnectionError(f"Não foi possível inicializar o modelo Gemini '{model_name}'. Erro: {error_msg}")

    def _map_test_connection_exception(self, error: Exception) -> Exception:
        error_msg = str(error)
        if self._is_quota_error(error):
            display_name = self.model_name.replace("models/", "")
            return QuotaExceededException(
                f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                display_name,
            )
        if "404" in error_msg:
            return ConnectionError(f"Modelo '{self.model_name}' não encontrado ou não acessível")
        if "403" in error_msg:
            return ConnectionError(f"Sem permissão para acessar modelo '{self.model_name}'")
        if "401" in error_msg:
            return ConnectionError("API Key inválida ou expirada")
        return error

    @staticmethod
    def _validate_init_inputs(api_key: str, model_name: str) -> None:
        if not api_key:
            logger.error("API Key não fornecida para o GeminiClient.")
            raise ValueError("API Key é obrigatória para inicializar o GeminiClient.")
        if not model_name:
            logger.error("Nome do modelo não fornecido para o GeminiClient.")
            raise ValueError("Nome do modelo é obrigatório para inicializar o GeminiClient.")

    def _create_model(self, normalized_model_name: str) -> Any:
        self._validate_model_availability(normalized_model_name)
        logger.debug(f">>> GeminiClient __init__: Inicializando GenerativeModel ('{normalized_model_name}')...")
        return genai.GenerativeModel(
            model_name=normalized_model_name,
            safety_settings=self._build_safety_settings(),
        )

    @staticmethod
    def _build_generation_config() -> Any:
        return genai.types.GenerationConfig(
            temperature=0.5,
            max_output_tokens=8192,
            top_p=0.8,
            top_k=40,
        )

    @staticmethod
    def _build_test_generation_config() -> Any:
        return genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=10,
            top_p=0.8,
        )

    def _generate_content(self, contents: str, generation_config: Any) -> Any:
        logger.debug(">>> GeminiClient: Chamando model.generate_content...")
        response = self.model.generate_content(contents=contents, generation_config=generation_config)
        logger.debug(f">>> GeminiClient: Resposta bruta do Gemini: {type(response)}")
        return response

    def _handle_runtime_exception(self, error: Exception, operation: str) -> None:
        if self._is_quota_error(error):
            self._raise_quota_exception(self.model_name, error)
        logger.error(
            f"Erro durante {operation} (modelo {self.model_name}): {type(error).__name__} - {error}",
            exc_info=True,
        )
        raise

    def __init__(self, api_key: str, model_name: str):
        logger.info(f">>> GeminiClient __init__: Iniciando com modelo '{model_name}' e API Key fornecida.")
        self._validate_init_inputs(api_key, model_name)

        normalized_model_name = self._normalize_model_name(model_name)
        self.api_key = api_key
        self.model_name = normalized_model_name

        try:
            logger.debug(">>> GeminiClient __init__: Configurando genai...")
            genai.configure(api_key=api_key)
            logger.debug(">>> GeminiClient __init__: genai configurado.")

            self.model = self._create_model(normalized_model_name)
            logger.info(f">>> GeminiClient __init__: GenerativeModel INICIALIZADO para '{normalized_model_name}'.")

        except QuotaExceededException:
            raise
        except Exception as error:
            logger.error(
                f">>> GeminiClient __init__: EXCEÇÃO CRÍTICA durante a inicialização do modelo '{normalized_model_name}': "
                f"{type(error).__name__} - {error}",
                exc_info=True,
            )
            mapped_error = self._map_init_exception(normalized_model_name, error)
            raise mapped_error from error

    def send_conversational_prompt(self, prompt_text: str) -> Optional[str]:
        logger.info(f"Enviando prompt para o modelo: {self.model_name}. Tamanho (aprox): {len(prompt_text):,} chars.")
        try:
            response = self._generate_content(
                contents=prompt_text,
                generation_config=self._build_generation_config(),
            )

            self._raise_if_blocked(response, "Solicitação")
            response_text = self._extract_response_text(response)
            if response_text:
                logger.info("Resposta textual recebida do Gemini.")
                return response_text

            logger.warning("Resposta do Gemini não continha conteúdo textual esperado.")
            return None

        except Exception as error:
            self._handle_runtime_exception(error, "chamada à API Gemini")

    def test_connection(self) -> bool:
        logger.info(f">>> GeminiClient test_connection: Testando com modelo '{self.model_name}'...")
        try:
            response = self._generate_content(
                contents="Test connection. Please respond with just 'OK'",
                generation_config=self._build_test_generation_config(),
            )

            self._raise_if_blocked(response, "Prompt de teste")
            if self._extract_response_text(response):
                logger.info(f">>> GeminiClient test_connection: Resposta recebida de '{self.model_name}'. Conexão OK.")
                return True
            logger.warning(">>> GeminiClient test_connection: Resposta vazia, mas sem erro de API. Considerando conexão OK.")
            return True
                
        except Exception as error:
            logger.error(
                f">>> GeminiClient test_connection: EXCEÇÃO CRÍTICA no teste: {type(error).__name__} - {error}",
                exc_info=True,
            )
            mapped_error = self._map_test_connection_exception(error)
            if mapped_error is error:
                raise
            raise mapped_error from error

    def close(self):
        logger.info(f"Cliente Gemini ({self.model_name}) 'fechado'.")

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Valida uma API Key sem criar uma instância completa"""
        try:
            genai.configure(api_key=api_key)
            # Tenta listar modelos como teste básico
            models = list(genai.list_models())
            return len(models) > 0
        except Exception:
            return False

    @staticmethod
    def get_available_models(api_key: str) -> list[str]:
        """Obtém lista de modelos disponíveis"""
        try:
            genai.configure(api_key=api_key)
            models_data = list(genai.list_models())
            available_models = []
            
            # Modelos conhecidos que funcionam bem (fallback)
            known_working_models = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-1.0-pro',
                'gemini-2.0-flash-exp'
            ]
            
            for model in models_data:
                if hasattr(model, 'name'):
                    model_name = model.name
                    
                    # Filtrar apenas modelos que suportam generateContent
                    if hasattr(model, 'supported_generation_methods'):
                        if 'generateContent' in model.supported_generation_methods:
                            # Remover prefixo models/ para exibição
                            display_name = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                            available_models.append(display_name)
                    else:
                        # Se não tem info sobre métodos, incluir mesmo assim
                        display_name = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                        available_models.append(display_name)
            
            # Se não encontrou modelos, usar lista conhecida
            if not available_models:
                logger.warning("Nenhum modelo encontrado via API, usando lista conhecida")
                available_models = known_working_models.copy()
            else:
                # Garantir que pelo menos um modelo conhecido esteja na lista
                for known_model in known_working_models:
                    if known_model not in available_models:
                        # Verificar se existe um modelo similar
                        for available in available_models:
                            if known_model.replace('-', '').replace('.', '') in available.replace('-', '').replace('.', ''):
                                break
                        else:
                            # Se não encontrou similar, adicionar o conhecido
                            available_models.append(known_model)
                            break
            
            logger.info(f"Modelos disponíveis encontrados: {available_models}")
            return sorted(available_models)
            
        except Exception as e:
            logger.error(f"Erro ao obter modelos disponíveis: {e}")
            # Retornar lista de modelos conhecidos como fallback
            return [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-1.0-pro'
            ]