import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Simulação de uma fila")
    parser.add_argument("--servers", type=int, required=True, help="Número de servidores")
    parser.add_argument("--capacity", type=int, required=True, help="Capacidade da fila")
    parser.add_argument("--a_chegada", type=float, required=True, help="Parâmetro a da distribuição de chegada")
    parser.add_argument("--b_chegada", type=float, required=True, help="Parâmetro b da distribuição de chegada")
    parser.add_argument("--a_servico", type=float, required=True, help="Parâmetro a da distribuição de serviço")
    parser.add_argument("--b_servico", type=float, required=True, help="Parâmetro b da distribuição de serviço")
    return parser.parse_args()

args = parse_args()

servers = args.servers
capacity = args.capacity
a_chegada, b_chegada = args.a_chegada, args.b_chegada
a_servico, b_servico = args.a_servico, args.b_servico

fila = []
tempo_atual = 0
eventos = [{'tipo': 'CHEGADA', 'tempo': 2.0}]
estados_tempo_acumulado = {i: 0.0 for i in range(capacity + 1)} 
tempo_ultimo_evento = 0
perdas = 0

simulation_log = []


a = 1664525
c = 101390422
M = 2**32
seed = 1
quantidade_numeros_aleatorios = 100000

def NextRandom():
    global seed, quantidade_numeros_aleatorios
    if quantidade_numeros_aleatorios > 0:
        seed = (a * seed + c) % M
        quantidade_numeros_aleatorios -= 1
        return seed / M
    else:
        return None

def calcular_tempo_uniforme(a, b):
    x = NextRandom()
    print(f"Gerado número pseudoaleatório: {x}")
    if x is not None:
        return a + ((b - a) * x)
    else:
        return None
    

def atualizar_tempo_estado_atual(novo_tempo):
    global tempo_ultimo_evento
    estado_atual = len(fila)
    tempo_desde_ultimo_evento = novo_tempo - tempo_ultimo_evento
    estados_tempo_acumulado[estado_atual] += tempo_desde_ultimo_evento
    tempo_ultimo_evento = novo_tempo

def processar_chegada(tempo):
    global perdas
    atualizar_tempo_estado_atual(tempo)
    tempo_proximo = calcular_tempo_uniforme(a_chegada, b_chegada)
    if tempo_proximo is not None:
        if len(fila) < capacity:
            fila.append('cliente')
            simulation_log.append(f"Tempo {tempo:.2f}: Cliente chegou, fila agora tem {len(fila)} cliente(s).")
            if len(fila) <= servers:
                tempo_servico = tempo + calcular_tempo_uniforme(a_servico, b_servico)
                if tempo_servico is not None:
                    eventos.append({'tipo': 'SAIDA', 'tempo': tempo_servico})
                    simulation_log.append(f"Tempo {tempo:.2f}: Saída agendada para o tempo {tempo_servico:.2f}.")
        else:
            perdas += 1
            simulation_log.append(f"Tempo {tempo:.2f}: Cliente perdeu, fila está cheia com {len(fila)} cliente(s).")

        proxima_chegada = tempo + tempo_proximo
        eventos.append({'tipo': 'CHEGADA', 'tempo': proxima_chegada})
        simulation_log.append(f"Tempo {tempo:.2f}: Próxima chegada agendada para o tempo {proxima_chegada:.2f}.")

def processar_saida(tempo):
    atualizar_tempo_estado_atual(tempo)
    if fila:
        fila.pop(0)
        simulation_log.append(f"Tempo {tempo:.2f}: Cliente atendido e saiu, fila agora tem {len(fila)} cliente(s).")
        if len(fila) >= servers:
            tempo_servico = tempo + calcular_tempo_uniforme(a_servico, b_servico)
            if tempo_servico is not None:
                eventos.append({'tipo': 'SAIDA', 'tempo': tempo_servico})
                simulation_log.append(f"Tempo {tempo:.2f}: Saída agendada para o tempo {tempo_servico:.2f}.")

while eventos and quantidade_numeros_aleatorios > 0:
    eventos.sort(key=lambda e: e['tempo'])
    evento_atual = eventos.pop(0)
    tempo_atual = evento_atual['tempo']

    if evento_atual['tipo'] == 'CHEGADA':
        processar_chegada(tempo_atual)
    elif evento_atual['tipo'] == 'SAIDA':
        processar_saida(tempo_atual)

atualizar_tempo_estado_atual(tempo_atual) 

tempo_total_simulacao = tempo_ultimo_evento
distribuicao_probabilidades = {estado: tempo / tempo_total_simulacao for estado, tempo in estados_tempo_acumulado.items()}
print("\nDistribuição de Probabilidades dos Estados da Fila:")
for estado, probabilidade in distribuicao_probabilidades.items():
    print(f"Estado {estado}: {probabilidade*100:.2f}%")

print("\nTempos Acumulados para os Estados da Fila:")
for estado, tempo in estados_tempo_acumulado.items():
    print(f"Estado {estado}: {tempo} segundos")

if perdas > 0:
    print(f"\nNúmero de Perdas (clientes que não puderam entrar na fila): {perdas}")

print(f"\nTempo Global da Simulação: {tempo_total_simulacao} segundos")
