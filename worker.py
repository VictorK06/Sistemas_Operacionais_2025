import time

def worker_process(worker_id, capacidade, task_queue, result_queue):
    while True:
        task=task_queue.get()
        if task=="STOP": break
        inicio=time.time()
        time.sleep(task["tempo_exec"]/capacidade)
        fim=time.time()
        result_queue.put({
            "evento":"END",
            "worker":worker_id,
            "req_id":task["id"],
            "duracao": fim-inicio
        })
