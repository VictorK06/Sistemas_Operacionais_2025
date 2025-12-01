# scheduler.py
_rr_index = 0

def round_robin(q):
    """
    Round-robin: seleciona a próxima tarefa de forma circular.
    q é a lista de tarefas pendentes.
    """
    global _rr_index
    if not q:
        raise IndexError("Fila vazia")
    # garante index válido
    _rr_index = _rr_index % len(q)
    tarefa = q.pop(_rr_index)
    # após remover, _rr_index permanece apontando para próxima posição (não incrementamos aqui)
    # assim o próximo call irá escolher o item que veio depois do removido
    return tarefa

def sjf(q):
    """
    Shortest Job First — ordena por tempo_exec e retorna a menor.
    """
    q.sort(key=lambda t: t["tempo_exec"])
    return q.pop(0)

def prioridade(q):
    """
    Prioridade — ordena por prioridade (1 = Alta, 3 = Baixa) e retorna a de maior prioridade.
    """
    # menor valor numericamente = maior prioridade
    q.sort(key=lambda t: t["prioridade"])
    return q.pop(0)

def escolher_politica(nome):
    if nome == "RR":
        return round_robin
    if nome == "SJF":
        return sjf
    if nome == "PRIORIDADE":
        return prioridade
    raise ValueError(f"Política desconhecida: {nome}")
