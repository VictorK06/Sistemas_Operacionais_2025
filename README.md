# README

## BSB Compute – Sistema de Orquestração de Tarefas

Este projeto simula um sistema de orquestração de tarefas de inteligência artificial utilizando processos concorrentes em Python.
O sistema distribui requisições entre servidores (workers) de acordo com diferentes políticas de escalonamento e registra métricas de desempenho.

## Funcionalidades

* Processos concorrentes usando 'multiprocessing'
* Comunicação entre processos com 'Queue'
* Políticas de escalonamento:

  * Round Robin (RR)
  * Shortest Job First (SJF)
  * Prioridade
* Balanceamento de carga entre servidores
* Chegada dinâmica de requisições
* Logs de execução em tempo real
* Cálculo de métricas ao final da simulação

## Como Executar

1. Certifique-se de ter Python 3.8 ou superior instalado.

2. (Opcional) Crie um ambiente virtual:

   Windows:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   
3. Execute o projeto:

```
python main.py
```

## Requisitos

O projeto utiliza apenas bibliotecas internas do Python.
Nenhuma instalação via pip é necessária.

## Autores

Victor Kazuo Soares Honda
Arthur Jannuzi Rocha 
