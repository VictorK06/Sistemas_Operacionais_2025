# main.py
import json
import os
from orchestrator import Orchestrator
import time

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(BASE_DIR, "config.json")) as f:
        config = json.load(f)

    # parâmetro: politica pode ser "RR", "SJF" ou "PRIORIDADE"
    politica = config.get("politica", "RR")

    # arrival_lambda: taxa para processo de Poisson (exponencial). Ex: 1.0 -> média 1s entre chegadas
    arrival_lambda = config.get("arrival_lambda", 0.5)  # ajuste conforme necessidade

    # opcional: max_load_per_server — evitar atribuir além desse número de tasks simultâneas por servidor
    max_load = config.get("max_load_per_server", None)

    orq = Orchestrator(config, politica=politica, arrival_lambda=arrival_lambda, max_load_per_server=max_load)
    tempo_total = time.time()
    resultado = orq.run()



    porcentagem_cpu = 1 - (resultado["soma_tempo_espera"] / tempo_total)
    print("\nResumo Final:")
    print(f"Tempo total de simulação: {resultado['tempo_total']:.2f}s")
    print(f"Tempo médio de resposta: {resultado['media_resposta']:.2f}s")
    print(f"Throughput: {resultado['throughput']:.2f} req/s")
    print(f"Tempo máximo de espera: {resultado["tempo_espera_maximo"]:.2f}s")
    print(f"Tempo de espera médio: {resultado["tempo_espera_medio"]:.2f}s")
    print(f"Uso de CPU: {porcentagem_cpu:.5f}%")

    print("\nDetalhes: tempos de resposta individuais:")
    for t in resultado.get("tempos_resposta_individuais", []):
        print(f"  {t:.2f}s")

if __name__ == "__main__":
    main()
