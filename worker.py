# worker.py
import time
import os

try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    _HAS_PSUTIL = False

def worker_process(worker_id, capacidade, task_queue, result_queue, heartbeat_interval=1.0):
    """
    Loop do worker:
    - Recebe tarefas via task_queue.
    - Simula execução: time.sleep(tempo_exec / capacidade).
    - Ao final coloca um evento "END" em result_queue com duracao.
    - Periodicamente envia eventos "HEARTBEAT" com uso de CPU (se psutil disponível).
    """
    pid = os.getpid()
    proc = psutil.Process(pid) if _HAS_PSUTIL else None
    last_heartbeat = time.time()

    while True:
        # check for tasks with a small timeout style using non-blocking get
        try:
            task = task_queue.get(timeout=0.2)
        except Exception:
            task = None

        # periodic heartbeat even if no tasks
        now = time.time()
        if now - last_heartbeat >= heartbeat_interval:
            cpu_percent = 0.0
            if _HAS_PSUTIL:
                try:
                    # cpu_percent(None) gives percentage since last call; call once with 0.0 interval
                    cpu_percent = proc.cpu_percent(interval=None)
                except Exception:
                    cpu_percent = 0.0
            result_queue.put({
                "evento": "HEARTBEAT",
                "worker": worker_id,
                "pid": pid,
                "cpu_percent": cpu_percent,
                "timestamp": now
            })
            last_heartbeat = now

        if task is None:
            continue

        if task == "STOP":
            break

        inicio = time.time()
        # Simula trabalho real: tempo_exec dividido pela capacidade do servidor
        time.sleep(task["tempo_exec"] / float(capacidade))
        fim = time.time()

        result_queue.put({
            "evento": "END",
            "worker": worker_id,
            "req_id": task["id"],
            "duracao": fim - inicio,
            "timestamp": fim
        })

    # final heartbeat on exit
    result_queue.put({
        "evento": "EXIT",
        "worker": worker_id,
        "pid": pid,
        "timestamp": time.time()
    })
