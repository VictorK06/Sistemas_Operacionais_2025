# orchestrator.py
import multiprocessing as mp
import time
import random
from scheduler import escolher_politica
from worker import worker_process

class Orchestrator:
    def __init__(self, config, politica="RR", arrival_lambda=1.0, max_load_per_server=None):
        """
        config: dicionário carregado de config.json
        politica: "RR", "SJF" ou "PRIORIDADE"
        arrival_lambda: taxa (lambda) para distribuição exponencial de chegadas (média = 1/lambda)
                        se None -> usa tempos de chegada instantâneos (sem espera)
        max_load_per_server: se setado impede atribuição a servidores cuja carga >= valor
        """
        self.config = config
        self.politica = escolher_politica(politica)
        self.requisicoes_pool = config.get("requisicoes", []).copy()  # pool de chegada
        random.shuffle(self.requisicoes_pool)
        self.workers_cfg = config["servidores"]

        self.task_queues = {}
        self.result_queue = mp.Queue()

        self.tempo_chegada = 0
        self.soma_tempo_total = []
        self.tempos_resposta = []
        self.tempos_espera = []
        self.processes = []

        # monitoring
        self.estado = [{"id": ws["id"], "carga": 0} for ws in self.workers_cfg]
        self.historico_carga = {ws["id"]: [] for ws in self.workers_cfg}
        self.heartbeats = []
        self.start_time = None

        # arrival control
        self.arrival_lambda = arrival_lambda
        self.next_arrival_delay = self._sample_interarrival()
        self.pending_reqs = []

        self.max_load_per_server = max_load_per_server

    def _sample_interarrival(self):
        if self.arrival_lambda is None or self.arrival_lambda <= 0:
            return 0.0
        return random.expovariate(self.arrival_lambda)

    def iniciar(self):
        for ws in self.workers_cfg:
            q = mp.Queue()
            p = mp.Process(
                target=worker_process,
                args=(ws["id"], ws["capacidade"], q, self.result_queue)
            )
            p.start()

            self.task_queues[ws["id"]] = q
            self.processes.append(p)

    def escolher_servidor(self, estado):
        return sorted(estado, key=lambda x: x["carga"])[0]["id"]

    def _registrar_carga(self, timestamp=None):
        ts = timestamp if timestamp is not None else time.time()
        for s in self.estado:
            self.historico_carga[s["id"]].append((ts - self.start_time, s["carga"]))

    def run(self):
        self.iniciar()
        self.start_time = time.time()
        inicio_sim = self.start_time

        time_since_last_arrival = 0.0
        last_tick = time.time()

        pool = self.requisicoes_pool

        while pool or self.pending_reqs or any(w["carga"] > 0 for w in self.estado):
            now = time.time()
            dt = now - last_tick
            last_tick = now

            # 1) chegada dinâmica
            if pool:
                self.next_arrival_delay -= dt
                if self.next_arrival_delay <= 0:
                    req = pool.pop(0)
                    self.tempo_chegada = time.time()
                    self.pending_reqs.append(req)

                    print(f"[{time.time()-inicio_sim:05.2f}] Requisição {req['id']} chegou (tempo_exec={req['tempo_exec']}, prio={req['prioridade']})", flush=True)

                    self.next_arrival_delay = self._sample_interarrival()

            # 2) atribuição
            if self.pending_reqs:
                try:
                    tarefa = self.politica(self.pending_reqs)
                except IndexError:
                    tarefa = None

                if tarefa:
                    candidatos = sorted(self.estado, key=lambda x: x["carga"])
                    servidor_destino = None

                    for c in candidatos:
                        if self.max_load_per_server is None or c["carga"] < self.max_load_per_server:
                            servidor_destino = c["id"]
                            break

                    if servidor_destino is None:
                        self.pending_reqs.insert(0, tarefa)
                    else:
                        prioridade_nome = ["Alta", "Média", "Baixa"][tarefa["prioridade"] - 1]

                        print(
                            f"[{time.time()-inicio_sim:05.2f}] Requisição {tarefa['id']} ({prioridade_nome}) atribuída ao Servidor {servidor_destino}",
                            flush=True
                        )

                        self.task_queues[servidor_destino].put(tarefa)

                        for s in self.estado:
                            if s["id"] == servidor_destino:
                                s["carga"] += 1

            # 3) resultados e heartbeats
            while not self.result_queue.empty():
                evento = self.result_queue.get()
                et = evento.get("evento")

                if et == "END":
                    for s in self.estado:
                        if s["id"] == evento["worker"]:
                            s["carga"] -= 1
                            if s["carga"] < 0:
                                s["carga"] = 0

                    duracao = evento["duracao"]
                    self.tempos_resposta.append(duracao)

                    tempo_fim = evento["timestamp"]
                    tempo_duracao = evento["duracao"]
                    turnaround_time = tempo_fim - self.tempo_chegada
                    tempo_espera = turnaround_time - tempo_duracao
                    self.tempos_espera.append(abs(tempo_espera))

                    print(
                        f"[{time.time()-inicio_sim:05.2f}] Servidor {evento['worker']} concluiu Requisição {evento['req_id']} (dur={duracao:.2f}s)",
                        flush=True
                    )

                elif et == "HEARTBEAT":
                    self.heartbeats.append(evento)

                elif et == "EXIT":
                    print(f"[{time.time()-inicio_sim:05.2f}] Worker {evento['worker']} (pid {evento.get('pid')}) saiu.", flush=True)

            # 4) monitoramento
            self._registrar_carga(timestamp=now)

            time.sleep(0.1)

        for q in self.task_queues.values():
            q.put("STOP")
        for p in self.processes:
            p.join()

        fim_sim = time.time()

        media_resposta = sum(self.tempos_resposta) / len(self.tempos_resposta) if self.tempos_resposta else 0.0
        throughput = len(self.tempos_resposta) / (fim_sim - inicio_sim) if (fim_sim - inicio_sim) > 0 else 0.0

        print(self.tempos_espera)

        soma_espera = sum(self.tempos_espera)
        media_espera = sum(self.tempos_espera) / len(self.tempos_espera) if self.tempos_espera else 0
        max_espera = max(self.tempos_espera) if self.tempos_espera else 0

        resultado = {
            "tempo_total": fim_sim - inicio_sim,
            "media_resposta": media_resposta,
            "throughput": throughput,
            "tempos_resposta_individuais": self.tempos_resposta,
            "tempos_espera_individuais": self.tempos_espera,
            "tempo_espera_medio": media_espera,
            "tempo_espera_maximo": max_espera,
            "soma_tempo_espera": soma_espera,
            "historico_carga": self.historico_carga,
            "heartbeats": self.heartbeats,
            "estado_final": self.estado
        }

        return resultado
