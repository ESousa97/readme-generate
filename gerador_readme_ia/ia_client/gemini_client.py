# gerador_readme_ia/ia_client/gemini_client.py
import google.generativeai as genai
import logging
from typing import Optional

from ..constants import APP_NAME # APP_AUTHOR é usado pelo logger_setup, não diretamente aqui

logger = logging.getLogger(f"{APP_NAME}.gemini_client")

class GeminiClient:
    def __init__(self, api_key: str, model_name: str):
        logger.info(f">>> GeminiClient __init__: Iniciando com modelo '{model_name}' e API Key fornecida.")
        if not api_key:
            logger.error("API Key não fornecida para o GeminiClient.")
            raise ValueError("API Key é obrigatória para inicializar o GeminiClient.")
        if not model_name:
            logger.error("Nome do modelo não fornecido para o GeminiClient.")
            raise ValueError("Nome do modelo é obrigatório para inicializar o GeminiClient.")

        try:
            logger.debug(">>> GeminiClient __init__: Configurando genai...")
            genai.configure(api_key=api_key)
            logger.debug(">>> GeminiClient __init__: genai configurado.")
            
            default_safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            logger.debug(f">>> GeminiClient __init__: Inicializando GenerativeModel ('{model_name}')...")
            self.model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=default_safety_settings
            )
            logger.info(f">>> GeminiClient __init__: GenerativeModel INICIALIZADO para '{model_name}'.")
            self.model_name = model_name # Armazena o nome do modelo
        except Exception as e:
            logger.error(f">>> GeminiClient __init__: EXCEÇÃO CRÍTICA durante a inicialização do modelo '{model_name}': {type(e).__name__} - {e}", exc_info=True)
            raise ConnectionError(f"Não foi possível inicializar o modelo Gemini '{model_name}'. Verifique o nome do modelo, a API Key, as configurações de segurança e sua conexão com a internet.") from e

    def send_conversational_prompt(self, prompt_text: str) -> Optional[str]:
        logger.info(f"Enviando prompt para o modelo: {self.model_name}. Tamanho (aprox): {len(prompt_text):,} chars.")
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.5,
                # max_output_tokens=8192, # Ajuste conforme o modelo e necessidade
            )
            logger.debug(">>> GeminiClient send_conversational_prompt: Chamando model.generate_content...")
            response = self.model.generate_content(
                contents=prompt_text,
                generation_config=generation_config
            )
            logger.debug(f">>> GeminiClient send_conversational_prompt: Resposta bruta do Gemini: {response}")

            if response.text:
                logger.info("Resposta textual recebida do Gemini.")
                return response.text
            elif hasattr(response, 'parts') and response.parts:
                full_response_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                if full_response_text:
                    logger.info("Resposta textual (via response.parts) recebida do Gemini.")
                    return full_response_text
            
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                block_reason_str = str(response.prompt_feedback.block_reason)
                logger.error(f"Solicitação bloqueada pelo Gemini. Razão: {block_reason_str}")
                if response.prompt_feedback.safety_ratings:
                    for rating in response.prompt_feedback.safety_ratings:
                        logger.error(f"  Safety Rating: Category={rating.category}, Probability={rating.probability}")
                # Considerar levantar uma exceção específica para bloqueio se a GUI precisar tratar diferente
                raise ValueError(f"PROMPT BLOQUEADO PELA IA. Razão: {block_reason_str}")
            
            logger.warning("Resposta do Gemini não continha conteúdo textual esperado e não foi explicitamente bloqueada.")
            return None # Ou raise ValueError("Resposta inesperada da IA.")
        except Exception as e:
            logger.error(f"Erro durante chamada à API Gemini (modelo {self.model_name}): {type(e).__name__} - {e}", exc_info=True)
            raise # Re-levanta a exceção para ser tratada pelo chamador

    def test_connection(self) -> bool:
        logger.info(f">>> GeminiClient test_connection: Testando com modelo '{self.model_name}'...")
        try:
            response = self.model.generate_content(
                "Olá",
                generation_config=genai.types.GenerationConfig(temperature=0.9, candidate_count=1)
            )
            logger.debug(f">>> GeminiClient test_connection: Resposta do teste: {response}")
            if response.text:
                logger.info(f">>> GeminiClient test_connection: Resposta recebida de '{self.model_name}'. Conexão OK.")
                return True
            elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                logger.error(f">>> GeminiClient test_connection: Prompt de teste bloqueado. Razão: {response.prompt_feedback.block_reason}")
                raise ConnectionError(f"Teste de conexão falhou: prompt bloqueado pela IA (Razão: {response.prompt_feedback.block_reason})")
            else:
                logger.warning(f">>> GeminiClient test_connection: Resposta para 'Olá' foi vazia, mas sem erro de API. Considerando conexão OK.")
                return True
        except Exception as e:
            logger.error(f">>> GeminiClient test_connection: EXCEÇÃO CRÍTICA no teste: {type(e).__name__} - {e}", exc_info=True)
            raise # Re-levanta a exceção

    def close(self):
        logger.info(f"Cliente Gemini ({self.model_name}) 'fechado'.")