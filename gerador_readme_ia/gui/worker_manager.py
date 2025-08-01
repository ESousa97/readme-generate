# gerador_readme_ia/gui/worker_manager.py

from PyQt5.QtCore import QThread, QTimer
from .worker import Worker
import logging

logger = logging.getLogger(__name__)

def run_in_thread(func, *args, callback_slot=None, error_slot=None, 
                  progress_slot=None, step_slot=None, timeout_ms=120000, **kwargs):
    """
    Executa uma função em thread separada com timeout opcional e callbacks de progresso
    
    Args:
        func: Função a ser executada
        *args: Argumentos posicionais para a função
        callback_slot: Slot para receber o resultado (success)
        error_slot: Slot para receber erros
        progress_slot: Slot para receber updates de progresso (message, percentage)
        step_slot: Slot para receber updates de step (step_name, status, details)
        timeout_ms: Timeout em milissegundos (padrão: 2 minutos)
        **kwargs: Argumentos nomeados para a função
    
    Returns:
        QThread: Thread criada
    """
    thread = QThread()
    worker = Worker(func, *args, **kwargs)
    worker.moveToThread(thread)

    # Conectar sinais básicos
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    # Conectar callbacks customizados
    if callback_slot:
        worker.result.connect(callback_slot)

    if error_slot:
        worker.error.connect(error_slot)
    else:
        # Handler genérico de erro
        worker.error.connect(lambda title, msg: logger.error(f"Worker error - {title}: {msg}"))

    # *** NOVA FUNCIONALIDADE: Conectar callbacks de progresso ***
    if progress_slot:
        worker.progress.connect(progress_slot)
        logger.debug("Progress callback conectado")

    if step_slot:
        worker.step_update.connect(step_slot)
        logger.debug("Step callback conectado")

    # Configurar timeout se especificado
    timeout_timer = None
    if timeout_ms > 0:
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(lambda: _handle_timeout(worker, thread, timeout_timer))
        
        # Parar timer quando worker terminar
        worker.finished.connect(timeout_timer.stop)

    # Conectar início da execução
    thread.started.connect(worker.run)
    
    # Iniciar thread
    thread.start()
    
    # Iniciar timeout se configurado
    if timeout_timer:
        timeout_timer.start(timeout_ms)

    logger.debug(f"Thread iniciada para função: {func.__name__}")
    return thread

def _handle_timeout(worker, thread, timer):
    """Trata timeout de thread"""
    logger.warning(f"Timeout detectado para worker: {worker.func.__name__}")
    
    # Solicitar interrupção
    worker.request_interruption()
    
    # Emitir sinal de erro
    worker.error.emit(
        "Timeout", 
        f"A operação '{worker.func.__name__}' demorou mais que o esperado e foi cancelada."
    )
    
    # Forçar finalização da thread
    if thread.isRunning():
        thread.quit()
        if not thread.wait(3000):  # Aguarda 3s para finalização limpa
            logger.warning("Thread não finalizou limpo, forçando término")
            thread.terminate()
            thread.wait(1000)
    
    # Limpar timer
    if timer:
        timer.deleteLater()

class ThreadManager:
    """Gerenciador centralizado de threads para a aplicação"""
    
    def __init__(self):
        self.active_threads = []
        
    def start_thread(self, func, *args, callback_slot=None, error_slot=None, 
                    progress_slot=None, step_slot=None, timeout_ms=120000, **kwargs):
        """Inicia uma nova thread e a registra no gerenciador"""
        
        thread = run_in_thread(
            func, *args, 
            callback_slot=callback_slot,
            error_slot=error_slot,
            progress_slot=progress_slot,
            step_slot=step_slot,
            timeout_ms=timeout_ms,
            **kwargs
        )
        
        # Registrar thread
        self.active_threads.append(thread)
        
        # Remover da lista quando finalizar
        thread.finished.connect(lambda: self._remove_thread(thread))
        
        return thread
    
    def _remove_thread(self, thread):
        """Remove thread da lista de threads ativas"""
        if thread in self.active_threads:
            self.active_threads.remove(thread)
            logger.debug(f"Thread removida do gerenciador. Threads ativas: {len(self.active_threads)}")
    
    def cleanup_all(self):
        """Para e limpa todas as threads ativas"""
        logger.info(f"Limpando {len(self.active_threads)} threads ativas...")
        
        for thread in self.active_threads.copy():
            if thread.isRunning():
                thread.quit()
                if not thread.wait(2000):
                    logger.warning("Thread não finalizou, forçando término")
                    thread.terminate()
                    thread.wait(1000)
        
        self.active_threads.clear()
        logger.info("Cleanup de threads concluído")
    
    def get_active_count(self):
        """Retorna número de threads ativas"""
        return len(self.active_threads)
    