# gerador_readme_ia/ia_client/gemini_client.py
import google.generativeai as genai
import logging
from typing import Optional

from ..constants import APP_NAME

logger = logging.getLogger(f"{APP_NAME}.gemini_client")

class QuotaExceededException(Exception):
    """Exceção específica para quota excedida"""
    def __init__(self, message, model_name=None):
        self.model_name = model_name
        super().__init__(message)

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
            
            # Garantir que o modelo tenha o formato correto
            if not model_name.startswith('models/'):
                model_name = f'models/{model_name}'
            
            # Verificar se o modelo existe na lista de modelos disponíveis
            try:
                available_models = list(genai.list_models())
                model_exists = False
                for model in available_models:
                    if hasattr(model, 'name') and model.name == model_name:
                        # Verificar se suporta generateContent
                        if hasattr(model, 'supported_generation_methods'):
                            if 'generateContent' in model.supported_generation_methods:
                                model_exists = True
                                break
                        else:
                            model_exists = True
                            break
                
                if not model_exists:
                    raise ValueError(f"Modelo '{model_name}' não encontrado ou não suporta generateContent")
                    
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "429" in str(e):
                    display_name = model_name.replace('models/', '')
                    raise QuotaExceededException(
                        f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                        display_name
                    )
                logger.warning(f"Não foi possível verificar disponibilidade do modelo: {e}")
                # Continuar mesmo assim, deixar a API decidir
            
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
            self.model_name = model_name
            self.api_key = api_key
            
        except QuotaExceededException:
            # Re-propagar sem modificar
            raise
        except Exception as e:
            logger.error(f">>> GeminiClient __init__: EXCEÇÃO CRÍTICA durante a inicialização do modelo '{model_name}': {type(e).__name__} - {e}", exc_info=True)
            
            # Mensagem de erro mais específica
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                display_name = model_name.replace('models/', '')
                raise QuotaExceededException(
                    f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                    display_name
                )
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise ConnectionError(f"Modelo '{model_name}' não encontrado. Verifique se você tem acesso a este modelo com sua API Key.") from e
            elif "403" in error_msg or "permission" in error_msg.lower():
                raise ConnectionError(f"Sem permissão para usar o modelo '{model_name}'. Verifique sua API Key e quota.") from e
            elif "401" in error_msg:
                raise ConnectionError("API Key inválida ou expirada.") from e
            else:
                raise ConnectionError(f"Não foi possível inicializar o modelo Gemini '{model_name}'. Erro: {error_msg}") from e

    def send_conversational_prompt(self, prompt_text: str) -> Optional[str]:
        logger.info(f"Enviando prompt para o modelo: {self.model_name}. Tamanho (aprox): {len(prompt_text):,} chars.")
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=8192,
                top_p=0.8,
                top_k=40
            )
            
            logger.debug(">>> GeminiClient send_conversational_prompt: Chamando model.generate_content...")
            response = self.model.generate_content(
                contents=prompt_text,
                generation_config=generation_config
            )
            logger.debug(f">>> GeminiClient send_conversational_prompt: Resposta bruta do Gemini: {type(response)}")

            # Verificar se a resposta foi bloqueada
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    block_reason_str = str(response.prompt_feedback.block_reason)
                    logger.error(f"Solicitação bloqueada pelo Gemini. Razão: {block_reason_str}")
                    if hasattr(response.prompt_feedback, 'safety_ratings') and response.prompt_feedback.safety_ratings:
                        for rating in response.prompt_feedback.safety_ratings:
                            logger.error(f"  Safety Rating: Category={rating.category}, Probability={rating.probability}")
                    raise ValueError(f"PROMPT BLOQUEADO PELA IA. Razão: {block_reason_str}")

            # Extrair texto da resposta
            if hasattr(response, 'text') and response.text:
                logger.info("Resposta textual recebida do Gemini.")
                return response.text
            elif hasattr(response, 'parts') and response.parts:
                full_response_text = ""
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        full_response_text += part.text
                if full_response_text:
                    logger.info("Resposta textual (via response.parts) recebida do Gemini.")
                    return full_response_text
            elif hasattr(response, 'candidates') and response.candidates:
                # Tentar extrair de candidates
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            candidate_text = ""
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    candidate_text += part.text
                            if candidate_text:
                                logger.info("Resposta textual (via candidates) recebida do Gemini.")
                                return candidate_text
            
            logger.warning("Resposta do Gemini não continha conteúdo textual esperado.")
            return None
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                display_name = self.model_name.replace('models/', '')
                raise QuotaExceededException(
                    f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                    display_name
                )
            logger.error(f"Erro durante chamada à API Gemini (modelo {self.model_name}): {type(e).__name__} - {e}", exc_info=True)
            raise

    def test_connection(self) -> bool:
        logger.info(f">>> GeminiClient test_connection: Testando com modelo '{self.model_name}'...")
        try:
            response = self.model.generate_content(
                "Test connection. Please respond with just 'OK'",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1, 
                    max_output_tokens=10,
                    top_p=0.8
                )
            )
            logger.debug(f">>> GeminiClient test_connection: Resposta do teste: {type(response)}")
            
            # Verificar bloqueios
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    logger.error(f">>> GeminiClient test_connection: Prompt de teste bloqueado. Razão: {response.prompt_feedback.block_reason}")
                    raise ConnectionError(f"Teste de conexão falhou: prompt bloqueado pela IA (Razão: {response.prompt_feedback.block_reason})")
            
            # Verificar se há resposta
            has_response = False
            if hasattr(response, 'text') and response.text:
                has_response = True
            elif hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        has_response = True
                        break
            elif hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    has_response = True
                                    break
                    if has_response:
                        break
            
            if has_response:
                logger.info(f">>> GeminiClient test_connection: Resposta recebida de '{self.model_name}'. Conexão OK.")
                return True
            else:
                logger.warning(f">>> GeminiClient test_connection: Resposta vazia, mas sem erro de API. Considerando conexão OK.")
                return True
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                display_name = self.model_name.replace('models/', '')
                raise QuotaExceededException(
                    f"Quota excedida para o modelo '{display_name}'. Tente outro modelo ou aguarde.",
                    display_name
                )
            logger.error(f">>> GeminiClient test_connection: EXCEÇÃO CRÍTICA no teste: {type(e).__name__} - {e}", exc_info=True)
            
            # Re-processar erro para mensagem mais clara
            if "404" in error_msg:
                raise ConnectionError(f"Modelo '{self.model_name}' não encontrado ou não acessível") from e
            elif "403" in error_msg:
                raise ConnectionError(f"Sem permissão para acessar modelo '{self.model_name}'") from e
            elif "401" in error_msg:
                raise ConnectionError("API Key inválida ou expirada") from e
            else:
                raise

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