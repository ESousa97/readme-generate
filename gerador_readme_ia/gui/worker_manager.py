# gerador_readme_ia/gui/worker_manager.py

from PyQt5.QtCore import QThread
from .worker import Worker

def run_in_thread(func, *args, callback_slot=None, error_slot=None, **kwargs):
    thread = QThread()
    worker = Worker(func, *args, **kwargs)
    worker.moveToThread(thread)

    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    if callback_slot:
        worker.result.connect(callback_slot)

    if error_slot:
        worker.error.connect(error_slot)
    else:
        # pode definir handler genérico aqui
        pass

    # Pode conectar sinais de progresso e status do worker aqui

    thread.started.connect(worker.run)
    thread.start()

    return thread
