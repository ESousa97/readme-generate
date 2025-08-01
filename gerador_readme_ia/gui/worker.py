import traceback
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import logging

logger = logging.getLogger(__name__)

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    result = pyqtSignal(object)
    progress = pyqtSignal(str, int)
    step_update = pyqtSignal(str, str, str)  # step_name, status, details

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_interruption_requested = False

    def request_interruption(self):
        self._is_interruption_requested = True

    def is_interruption_requested(self):
        return self._is_interruption_requested

    @pyqtSlot()
    def run(self):
        logger.debug(f"Worker ({self.func.__name__}): Iniciando execução na thread {QThread.currentThreadId()}.")
        try:
            res = self.func(self.progress.emit, self.step_update.emit, self, *self.args, **self.kwargs)
            logger.debug(f"Worker ({self.func.__name__}): Execução concluída. Resultado: {type(res)}")
            if res is not None and not self.is_interruption_requested():
                self.result.emit(res)
        except Exception as e:
            if not self.is_interruption_requested():
                logger.error(f"Erro na thread worker ({self.func.__name__}): {e}", exc_info=True)
                self.error.emit(f"Erro na Tarefa ({self.func.__name__})", f"Ocorreu um erro: {e}\n\nDetalhes:\n{traceback.format_exc()}")
        finally:
            logger.debug(f"Worker ({self.func.__name__}): Finalizando.")
            self.finished.emit()
