# run_app.py
import sys
import os
import traceback

PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_DIR)

try:
    # Corrigido: importar APP_DISPLAY_NAME de constants.py, não de app_gui.py
    from gerador_readme_ia.constants import APP_NAME, APP_AUTHOR, APP_VERSION, APP_DISPLAY_NAME
    from gerador_readme_ia.gui.app_gui import ReadmeGeneratorGUI
    from gerador_readme_ia.logger_setup import setup_logging
except ModuleNotFoundError as e:
    print(f"Erro Crítico: Não foi possível encontrar os módulos do projeto 'gerador_readme_ia'. Detalhes: {e}")
    print(f"Verifique se você está executando 'run_app.py' do diretório raiz do projeto ('{PROJECT_ROOT_DIR}')")
    print("e se a pasta 'gerador_readme_ia' existe e contém os arquivos necessários.")
    print(f"sys.path atual: {sys.path}")
    input("Pressione Enter para sair...")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QLocale, QTranslator, QLibraryInfo

logger = setup_logging(f"{APP_NAME}.runner", app_author=APP_AUTHOR, debug=True)

def setup_qt_translations(app_instance: QApplication):
    locale_name = QLocale.system().name()
    translator = QTranslator(app_instance)
    translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    logger.info(f"Tentando carregar traduções Qt de: {translations_path} para o locale: {locale_name}")
    loaded = False
    if translator.load(f"qtbase_{locale_name}", translations_path):
        loaded = True
    elif "_" in locale_name:
        lang_code = locale_name.split('_')[0]
        logger.info(f"Falhou para {locale_name}, tentando fallback para tradução: qtbase_{lang_code}")
        if translator.load(f"qtbase_{lang_code}", translations_path):
            loaded = True
            locale_name = lang_code
    if loaded:
        if app_instance.installTranslator(translator):
            logger.info(f"Tradução Qt padrão instalada para: {locale_name}")
        else:
            logger.error(f"Falha ao INSTALAR tradução Qt padrão para: {locale_name}")
    else:
        logger.warning(f"Falha ao CARREGAR qualquer tradução Qt padrão para locale base: {locale_name} de {translations_path}")

if __name__ == '__main__':
    logger.info(f"Iniciando {APP_DISPLAY_NAME} v{APP_VERSION} (PyQt5)...")

    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    setup_qt_translations(app)

    try:
        main_window = ReadmeGeneratorGUI()
        main_window.show()
        logger.info("Janela principal exibida. Iniciando loop de eventos PyQt5.")
        exit_code = app.exec_()
        logger.info(f"Loop de eventos PyQt5 encerrado com código: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar ou executar a aplicação GUI PyQt5: {e}", exc_info=True)
        error_msg_box = QMessageBox()
        error_msg_box.setIcon(QMessageBox.Critical)
        error_msg_box.setWindowTitle(f"Erro Crítico - {APP_DISPLAY_NAME}")
        error_msg_box.setText(f"Ocorreu um erro fatal e a aplicação precisa ser fechada.\n\n{type(e).__name__}: {e}")
        error_msg_box.setDetailedText(traceback.format_exc())
        error_msg_box.setStandardButtons(QMessageBox.Ok)
        error_msg_box.exec_()
        sys.exit(1)
