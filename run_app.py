# run_app.py
"""
Ponto de entrada da aplicação modernizada com CustomTkinter
"""
import os
import sys
import traceback
from importlib import util
from tkinter import messagebox

import customtkinter as ctk

# Adicionar diretório raiz ao path
PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_DIR)

try:
    from gerador_readme_ia.constants import APP_AUTHOR, APP_DISPLAY_NAME, APP_NAME, APP_VERSION
    from gerador_readme_ia.gui.app_gui import ReadmeGeneratorApp
    from gerador_readme_ia.logger_setup import setup_logging
except ModuleNotFoundError as e:
    print("Erro Crítico: Não foi possível encontrar os módulos do projeto 'gerador_readme_ia'.")
    print(f"Detalhes: {e}")
    print(f"Verifique se você está executando 'run_app.py' do diretório raiz do projeto ('{PROJECT_ROOT_DIR}')")
    print("e se a pasta 'gerador_readme_ia' existe e contém os arquivos necessários.")
    print(f"sys.path atual: {sys.path}")
    input("Pressione Enter para sair...")
    sys.exit(1)

# Configurar logger
logger = setup_logging(
    f"{APP_NAME}.runner",
    app_author=APP_AUTHOR,
    debug=os.getenv("APP_DEBUG", "false").lower() == "true",
)

def setup_customtkinter():
    """Configura CustomTkinter para melhor aparência"""
    try:
        # Configurar tema padrão
        ctk.set_appearance_mode("system")  # Seguir tema do sistema
        ctk.set_default_color_theme("blue")  # Tema base (será sobrescrito)
        
        # Configurar DPI scaling
        try:
            ctk.deactivate_automatic_dpi_awareness()
        except Exception:
            pass  # Ignorar se não disponível
        
        logger.info("CustomTkinter configurado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar CustomTkinter: {e}")

def check_dependencies():
    """Verifica dependências essenciais"""
    missing_deps = []

    if util.find_spec("customtkinter") is None:
        missing_deps.append("customtkinter")

    if util.find_spec("google.generativeai") is None:
        missing_deps.append("google-generativeai")

    if util.find_spec("markdown") is None:
        missing_deps.append("markdown")

    if util.find_spec("darkdetect") is None:
        missing_deps.append("darkdetect")
    
    if missing_deps:
        error_msg = f"""
Dependências faltando:
{chr(10).join(f"• {dep}" for dep in missing_deps)}

Para instalar, execute:
pip install {' '.join(missing_deps)}

Ou instale todas as dependências:
pip install -r requirements.txt
        """
        print(error_msg)
        
        try:
            root = ctk.CTk()
            root.withdraw()  # Ocultar janela principal
            messagebox.showerror("Dependências Faltando", error_msg)
            root.destroy()
        except Exception:
            pass
        
        sys.exit(1)

def main():
    """Função principal da aplicação"""
    logger.info(f"Iniciando {APP_DISPLAY_NAME} v{APP_VERSION} (CustomTkinter)...")
    
    # Verificar dependências
    check_dependencies()
    
    # Configurar CustomTkinter
    setup_customtkinter()
    
    try:
        # Criar e executar aplicação
        app = ReadmeGeneratorApp()
        
        logger.info("Interface criada com sucesso. Iniciando loop principal...")
        
        # Executar aplicação
        app.mainloop()
        
        logger.info("Aplicação encerrada normalmente.")
        
    except Exception as e:
        logger.critical(f"Erro crítico ao executar a aplicação: {e}", exc_info=True)
        
        error_msg = f"""
Erro fatal na aplicação:

{type(e).__name__}: {e}

Detalhes técnicos:
{traceback.format_exc()}

Por favor, reporte este erro com as informações acima.
        """
        
        try:
            # Tentar mostrar erro na interface
            root = ctk.CTk()
            root.withdraw()
            messagebox.showerror(f"Erro Crítico - {APP_DISPLAY_NAME}", error_msg)
            root.destroy()
        except Exception:
            # Se falhar, mostrar no console
            print(error_msg)
        
        sys.exit(1)

if __name__ == '__main__':
    main()
    