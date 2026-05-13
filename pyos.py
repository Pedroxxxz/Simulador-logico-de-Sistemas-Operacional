import time
import sys
import random

# ==========================================
# ESTRUTURAS DE DADOS DO KERNEL
# ==========================================

# Tabela global de processos (Nossa "RAM")
tabela_processos = []
max_processos = 5
pid_counter = 1000  # PIDs na vida real começam em 1000 
impressora_ocupada = False
processo_usando_impressora = None
scanner_ocupado = False
processo_usando_scanner = None
mensagens = {}

class PCB:
    """Bloco Descritor de Processo (Process Control Block)"""
    def __init__(self, nome, prioridade="media"):
        global pid_counter
        self.pid = pid_counter
        self.nome = nome
        self.prioridade = prioridade
        self.estado = "PRONTO"  # Estados possíveis: PRONTO, EXECUTANDO, BLOQUEADO, TERMINADO, ZUMBI
        self.ciclos_restantes = random.randint(2, 6)  # Define o "peso" do processo (quantos ticks ele precisa)
        pid_counter += 1

# ==========================================
# FUNÇÕES DO KERNEL E ESCALONADOR
# ==========================================

def boot():
    """Simula a inicialização do Sistema Operacional"""
    print("Iniciando PyOS Kernel v1.0...")
    time.sleep(1)
    print("Carregando módulos de memória [OK]")
    time.sleep(0.5)
    print("Iniciando escalonador de processos [OK]")
    time.sleep(0.5)
    print("Bem-vindo ao terminal. Digite 'help' para comandos.\n")

def spawn_process(nome, prioridade="media"):
    """Cria um novo processo e adiciona na tabela (RAM)"""
    if len(tabela_processos) >= max_processos:
        print(f"[Kernel] ERRO: Out of Memory! Limite de {max_processos} processos atingido.")
        print(f"[Kernel] Use 'kill [PID]' ou 'cpu' para liberar memória antes de continuar.")
        return
    
    novo_processo = PCB(nome, prioridade)
    tabela_processos.append(novo_processo)
    print(f"[Kernel] Processo '{nome}' criado com PID {novo_processo.pid} "
          f"({len(tabela_processos)}/{max_processos} slots usados)")

def escalonador_tick():
    """Simula um ciclo (quantum) do processador executando a fila (Round Robin)"""
    prontos = [p for p in tabela_processos if p.estado == "PRONTO"]

    prioridades = {
        "alta": 0,
        "media": 1,
        "baixa": 2
    }

    prontos.sort(key=lambda p: prioridades[p.prioridade])
    
    if not prontos:
        print("[CPU] Ociosa (Idle). Nenhum processo na fila de prontos.")
        return

    # Pega o primeiro processo da fila
    processo_atual = prontos[0]
    
    # CHAVEAMENTO DE CONTEXTO: Entrando na CPU
    processo_atual.estado = "EXECUTANDO"
    print(f"\n[CPU] Executando PID {processo_atual.pid} ({processo_atual.nome})...")
    time.sleep(1)  # Simula o tempo real da CPU processando a tarefa
    
    # Decrementa o trabalho necessário (simula que ele fez progresso)
    processo_atual.ciclos_restantes -= 1
    
    # Verifica se o processo terminou seu trabalho
    if processo_atual.ciclos_restantes <= 0:
        processo_atual.estado = "ZUMBI"
        print(f"[Kernel] Processo PID {processo_atual.pid} finalizou e liberou a memória.")
    else:
        # CHAVEAMENTO DE CONTEXTO: Saindo da CPU por preempção (acabou o tempo dele)
        processo_atual.estado = "PRONTO"
        # Tira do início da fila e coloca no final (Round Robin)
        tabela_processos.remove(processo_atual)
        tabela_processos.append(processo_atual)
        print(f"[Kernel] Chaveamento de contexto. PID {processo_atual.pid} pausado e movido para o fim da fila.")

def block_process(pid):
    for p in tabela_processos:
        if p.pid == pid:
            p.estado = "BLOQUEADO"
            print(f"[Kernel] Processo {pid} bloqueado.")
            return
        
    print("[Kernel] PID não encontrado.")

def unblock_process(pid):
    for p in tabela_processos:
        if p.pid == pid:
            p.estado = "PRONTO"
            print(f"[Kernel] Processo {pid} desbloqueado.")
            return
        
    print("[Kernel] PID não encontrado.")


def run_scheduler():
    print("[Kernel] Iniciando execução automática...\n")

    while any(p.estado == "PRONTO" for p in tabela_processos):
        escalonador_tick()

    print("\n[Kernel] Todos os processos foram finalizados.")    

def use_printer(pid):

    global impressora_ocupada
    global processo_usando_impressora

    if impressora_ocupada:
        print(f"[Kernel] Impressora ocupada pelo PID {processo_usando_impressora}")
        return
    
    for p in tabela_processos:
        if p.pid == pid:
            impressora_ocupada = True
            processo_usando_impressora = pid
            print(f"[Kernel] PID {pid} está usando a impressora.")
            return

    print("[Kernel] PID não encontrado.")    


def release_printer():

    global impressora_ocupada
    global processo_usando_impressora

    if not impressora_ocupada:
        print(f"[Kernel] Impressora já está livre.")
        return
    
    print(f"[Kernel] PID {processo_usando_impressora} liberou a impressora.")

    impressora_ocupada = False
    processo_usando_impressora = None

def use_scanner(pid):

    global scanner_ocupado
    global processo_usando_scanner

    if scanner_ocupado:
        print(f"[Kernel] Scanner ocupado pelo PID {processo_usando_scanner}")
        return
    
    scanner_ocupado = True
    processo_usando_scanner = pid

    print(f"[Kernel] PID {pid} está usando o scanner.")


def detectar_deadlock():

    if impressora_ocupada and scanner_ocupado:
        print("\n[ALERTA] DEADLOCK DETECTADO!")    
        print(f"PID {processo_usando_impressora} espera scanner")
        print(f"PID {processo_usando_scanner} espera impressora\n")

def limpar_zumbis():

    global tabela_processos

    tabela_processos = [
        p for p in tabela_processos
        if p.estado != "ZUMBI"
    ]   

    print("[Kernel] Processos zumbis removidos.")     


def fork_process(pid):

    for p in tabela_processos:
        if p.pid == pid:
            clone = PCB(p.nome, p.prioridade)    
            clone.ciclos_restantes = p.ciclos_restantes
            tabela_processos.append(clone)
            print(f"[Kernel] Processo {pid} clonado.")
            print(f"[Kernel] Novo PID: {clone.pid}")
            return
        
    print("[Kernel] PID não encontrado.")

def send_message(origem, destino, texto):

    if destino not in mensagens:
        mensagens[destino] = []

    mensagens[destino].append(
        f"Mensagem de PID {origem}: {texto}"
    )    

    print("[Kernel] Mensagem enviada.")

def read_messages(pid):

    if pid not in mensagens:
        print("[Kernel] Nenhuma mensagem.")
        return
    
    print("\n--- CAIXA DE ENTRADA ---")

    for msg in mensagens[pid]:
        print(msg)

    mensagens[pid] = []    

# ==========================================
# INTERFACE COM O USUÁRIO (SHELL)
# ==========================================  

def shell():
    """O laço principal que aguarda comandos do usuário"""
    global tabela_processos
    
    while True:
        try:
            # O Prompt do nosso SO
            comando = input("root@pyos:~# ").strip().lower().split()
            
            # Evita erro se o usuário apertar Enter vazio
            if not comando:
                continue
                
            acao = comando[0]
            
            if acao == "exit":
                print("Desligando o sistema...")
                break
                
            elif acao == "help":
                print("Comandos disponíveis:")
                print("  spawn [nome] [prioridade] - Cria processo (prioridade: alta/media/baixa)")
                print("  ps                        - Lista os processos ativos")
                print("  cpu                       - Executa 1 ciclo do processador (Escalonador)")
                print("  run                       - Executa automaticamente até a fila esvaziar")
                print("  kill [PID]                - Encerra um processo à força")
                print("  block [PID]               - Bloqueia um processo (simula espera de E/S)")
                print("  unblock [PID]             - Desbloqueia um processo")
                print("  use_printer [PID]         - Processo ocupa a impressora")
                print("  release_printer           - Libera a impressora")
                print("  use_scanner [PID]         - Processo ocupa o scanner")
                print("  deadlock                  - Detecta espera circular entre recursos")
                print("  wait                      - Remove processos zumbis da RAM")
                print("  fork [PID]                - Clona um processo existente")
                print("  send [orig] [dest] [msg]  - Envia mensagem entre processos")
                print("  read [PID]                - Lê mensagens recebidas por um processo")
                print("  clear                     - Limpa a tela")
                print("  exit                      - Desliga o sistema")
                
            elif acao == "clear":
                print("\033[H\033[J", end="")  # Código ANSI para limpar terminal
                
            elif acao == "spawn":
               if len(comando) > 1:
                   prioridade = "media"

                   if len(comando) > 2:
                       prioridade = comando[2]

                   spawn_process(comando[1], prioridade)

               else:
                   print("Uso correto: spawn [nome] [prioridade]")        
                    
            elif acao == "ps":
                # Formatação em colunas para ficar parecido com o Linux
                print(f"{'PID':<6} | {'NOME':<12} | {'PRIORIDADE':<12} | {'ESTADO':<12} | {'CICLOS'}")
                print("-" * 55)
                for p in tabela_processos:
                    print(f"{p.pid:<6} | {p.nome[:12]:<12} | {p.prioridade:<12} | {p.estado:<12} | {p.ciclos_restantes}")
                if not tabela_processos:
                    print("Nenhum processo em execução.")
                    
            elif acao == "kill":
                if len(comando) > 1:
                    try:
                        alvo = int(comando[1])
                        tabela_processos = [p for p in tabela_processos if p.pid != alvo]
                        print(f"[Kernel] Sinal SIGKILL enviado. PID {alvo} destruído.")
                    except ValueError:
                        print("Erro: O PID deve ser um número inteiro.")
                else:
                    print("Uso correto: kill [PID]")
                    
            elif acao == "cpu":
                escalonador_tick()

            elif acao == "run":
                run_scheduler()    

            elif acao == "block":
                if len(comando) > 1:
                    block_process(int(comando[1]))    

            elif acao == "unblock":
                if len(comando) > 1:
                    unblock_process(int(comando[1]))    

            elif acao == "use_printer":
                if len(comando) > 1:
                    use_printer(int(comando[1]))

            elif acao == "use_scanner":
                if len(comando) > 1:
                    use_scanner(int(comando[1]))
                        
            elif acao == "release_printer":
                release_printer()

            elif acao == "deadlock":
                detectar_deadlock()    

            elif acao == "wait":
                limpar_zumbis()

            elif acao == "fork":
                if len(comando) > 1:
                    fork_process(int(comando[1]))

            elif acao == "send":
                if len(comando) > 3:
                    origem = int(comando[1])
                    destino = int(comando[2])
                    texto = " ".join(comando[3:])
                    send_message(origem, destino, texto)

            elif acao == "read":
                if len(comando) > 1:
                    read_messages(int(comando[1]))

            else:
                print(f"bash: {acao}: comando não encontrado. Digite 'help'.")
                
        # Intercepta o Ctrl+C para não "quebrar" o simulador com erro feio
        except KeyboardInterrupt:
            print("\nPor favor, use 'exit' para sair do PyOS.")

# ==========================================
# INÍCIO DO SISTEMA
# ==========================================

if __name__ == "__main__":
    boot()
    shell()
