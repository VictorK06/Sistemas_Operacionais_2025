def round_robin(q): return q.pop(0)
def sjf(q):
    q.sort(key=lambda t:t["tempo_exec"])
    return q.pop(0)
def prioridade(q):
    q.sort(key=lambda t:t["prioridade"])
    return q.pop(0)

def escolher_politica(nome):
    if nome=="RR": return round_robin
    if nome=="SJF": return sjf
    if nome=="PRIORIDADE": return prioridade
