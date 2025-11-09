import grpc
import sys
import threading
import hashlib
import time
import random

# IMPORTANTE: Usar os nomes de stubs gerados pelo seu mine_grpc.proto
import mine_grpc_pb2 as pb2
import mine_grpc_pb2_grpc as pb2_grpc

# =================================================================
# 1. ESTADO GLOBAL DO CLIENTE
# =================================================================
solution_found = threading.Event() 
found_solution_string = None
CLIENT_ID = None # Será definido em run() a partir do argumento de linha de comando


# =================================================================
# 2. LÓGICA DE MINERAÇÃO E HASHING
# =================================================================

def is_valid_solution(solution_str, challenge_value):
    """Verifica se o hash SHA-1 da string atende ao desafio."""
    hash_obj = hashlib.sha1(solution_str.encode('utf-8'))
    hex_hash = hash_obj.hexdigest()
    target_zeros = '0' * challenge_value 
    return hex_hash.startswith(target_zeros)

def mine_worker(stub, transaction_id, challenge, worker_id, start_value, num_attempts):
    """Função executada por cada thread para buscar a solução."""
    global solution_found, found_solution_string

    for i in range(start_value, start_value + num_attempts):
        if solution_found.is_set():
            break 
        
        # Gera a string a ser testada, incorporando o CLIENT_ID e o ID do worker
        test_string = f"Client-{CLIENT_ID}-{i}-{worker_id}" 
        
        if is_valid_solution(test_string, challenge):
            # NÃO imprima a solução aqui, pois a impressão pode ser atrasada e poluir o output
            # A impressão será feita na função run_mine_process
            found_solution_string = test_string
            solution_found.set()
            break

# =================================================================
# 3. ORQUESTRAÇÃO DA MINERAÇÃO (Opção 6)
# =================================================================

def run_mine_process(stub):
    """Orquestra os passos de mineração (RPC + Local)."""
    global solution_found, found_solution_string
    
    solution_found.clear()
    found_solution_string = None
    
    print("\n--- INICIANDO MINERAÇÃO ---")
    
    try:
        # 1. Buscar transactionID atual
        tx_id_response = stub.getTransactionId(pb2.void())
        transaction_id = tx_id_response.result
        print(f"1. TransactionID atual: {transaction_id}")

        # 2. Buscar a challenge (desafio) associada
        challenge_response = stub.getChallenge(pb2.transactionId(transactionId=transaction_id))
        challenge = challenge_response.result
        print(f"2. Desafio (zeros à esquerda): {challenge}")

        if challenge <= 0:
            print("Erro: Desafio inválido recebido do servidor.")
            return

        # 3. Buscar, localmente, uma solução (Multithread)
        NUM_THREADS = 8
        ATTEMPTS_PER_THREAD = 20000000 
        
        threads = []
        for i in range(NUM_THREADS):
            start = i * ATTEMPTS_PER_THREAD
            thread = threading.Thread(target=mine_worker, args=(stub, transaction_id, challenge, i, start, ATTEMPTS_PER_THREAD))
            threads.append(thread)
            thread.start()

        print(f"3. Mineração multithread em andamento ({NUM_THREADS} threads)...")

        # Aguarda até que a solução seja encontrada
        while not solution_found.is_set():
            time.sleep(0.5)
            
        for thread in threads:
            thread.join(timeout=0.1) 

        # 4. Imprimir localmente a solução encontrada
        solution_str = found_solution_string
        print(f"\n4. Solução encontrada (Local): {solution_str}")
        
        if not solution_str:
             print("Aviso: Solução não encontrada.")
             return
             
        # 5. Submeter a solução ao servidor e aguardar resultado
        submit_args = pb2.challengeArgs(
            transactionId=transaction_id,
            clientId=CLIENT_ID,
            solution=solution_str
        )
        submit_result_pb = stub.submitChallenge(submit_args)
        submit_result = submit_result_pb.result

        # 6. Imprimir/Decodificar resposta do servidor
        if submit_result == 1:
            print(f"\nSUCESSO! A solução foi aceita. Você (ID {CLIENT_ID}) ganhou a recompensa e um novo desafio foi gerado!")
        elif submit_result == 0:
            print("FALHA: A solução submetida é inválida (SHA-1 não bate).")
        elif submit_result == 2:
            print("AVISO: A transação já havia sido resolvida por outro minerador.")
        elif submit_result == -1:
            print("ERRO: O TransactionID submetido é inválido ou obsoleto.")
        else:
            print(f"RESPOSTA DESCONHECIDA: {submit_result}")

    except grpc.RpcError as e:
        print(f"Erro de comunicação gRPC: {e.details()}")


# =================================================================
# 4. FUNÇÕES DE ENTRADA E MENU INTERATIVO (Final)
# =================================================================

def get_transaction_id_input(stub, prompt="Digite o ID da transação (0 para atual):"):
    while True:
        try:
            tx_id_input = input(prompt)
            tx_id_input = tx_id_input if tx_id_input.strip() else "0" 
            tx_id = int(tx_id_input)
            
            return tx_id
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
        except grpc.RpcError as e:
            print(f"Erro ao buscar ID atual: {e.details()}")
            return None


def run():
    global CLIENT_ID
    
    # Requer 3 argumentos: [script] [server_address:port] [client_id]
    if len(sys.argv) < 3:
        print("Uso: python grpcCalc_client.py <server_address:port> <client_id>")
        sys.exit(1)
        
    server_address = sys.argv[1]
    
    try:
        # Define o ID do cliente a partir do argumento de linha de comando
        CLIENT_ID = int(sys.argv[2]) 
    except ValueError:
        print("Erro: O ID do cliente deve ser um número inteiro.")
        sys.exit(1)
        
    print(f"\nCLIENTE INICIADO: ID ÚNICO = {CLIENT_ID}. Conectando a {server_address}...")
    
    # CRIA O STUB
    channel = grpc.insecure_channel(server_address)
    stub = pb2_grpc.apiStub(channel) 
    
    while True:
        print("\n--- CLIENTE MINERADOR gRPC ---")
        print(f"ID Cliente Atual: {CLIENT_ID}")
        print("1. getTransactionID (Consultar ID Pendente)")
        print("2. getChallenge (Consultar Valor do Desafio)")
        print("3. getTransactionStatus (Consultar Status)")
        print("4. getWinner (Consultar Vencedor)")
        print("5. GetSolution (Consultar Detalhes/Solução)")
        print("6. INICIAR MINERAÇÃO (MINE)")
        print("7. Sair")
        
        try:
            choice = input("Escolha uma opção: ")
            
            if choice == '1':
                # getTransactionID() (Sem parâmetros)
                res = stub.getTransactionId(pb2.void())
                print(f"ID da Transação Atual Pendente: {res.result}")
            
            elif choice == '2':
                # getChallenge(transactionID)
                tx_id = get_transaction_id_input(stub, "ID da transação para consultar o Desafio:")
                if tx_id is not None:
                    res = stub.getChallenge(pb2.transactionId(transactionId=tx_id))
                    if res.result >= 1:
                        print(f"Desafio associado ao ID {tx_id}: {res.result} zeros à esquerda.")
                    else: # Retorne -1 se o transactionID for inválido
                         print(f"Erro: ID {tx_id} inválido. Retorno: {res.result}")
                         
            elif choice == '3':
                # getTransactionStatus(transactionID)
                tx_id = get_transaction_id_input(stub, "ID da transação para consultar o Status:")
                if tx_id is not None:
                    res = stub.getTransactionStatus(pb2.transactionId(transactionId=tx_id))
                    # Regra: 0=Resolvido, 1=Pendente, -1=Inválido
                    status_map = {1: "Pendente", 0: "Resolvido", -1: "ID Inválido"}
                    print(f"Status da Transação ID {tx_id}: {status_map.get(res.result, 'Desconhecido')}")
            
            elif choice == '4':
                # getWinner(transactionID)
                tx_id = get_transaction_id_input(stub, "ID da transação para consultar o Vencedor:")
                if tx_id is not None:
                    res = stub.getWinner(pb2.transactionId(transactionId=tx_id))
                    winner_id = res.result
                    
                    # Regra: >0 = clientID, 0 = sem vencedor/pendente, -1 = inválido
                    if winner_id == -1:
                        print(f"Vencedor da Transação ID {tx_id}: ID INVÁLIDO.")
                    elif winner_id == 0:
                        # Este é o ponto onde seu SERVIDOR falha ao retornar 0 mesmo após o sucesso, mas o CLIENTE deve interpretar 0 como 'sem vencedor'
                        print(f"Vencedor da Transação ID {tx_id}: PENDENTE (Nenhum vencedor registrado).")
                    else:
                        print(f"🏆 VENCEDOR: Client ID {winner_id} para Transação ID {tx_id}!")
                        
            elif choice == '5':
                # getSolution(transactionID)
                tx_id = get_transaction_id_input(stub, "ID da transação para consultar a Solução e Detalhes:")
                if tx_id is not None:
                    res = stub.getSolution(pb2.transactionId(transactionId=tx_id))
                    
                    status_map = {-1: "ID Inválido", 0: "Resolvido", 1: "Pendente"}
                    print(f"\n--- Detalhes da Transação ID {tx_id} ---")
                    print(f"Status: {status_map.get(res.status, 'Desconhecido')}")
                    print(f"Desafio (zeros): {res.challenge}")
                    print(f"Solução: {res.solution}")
                
            elif choice == '6':
                # INICIAR MINERAÇÃO (MINE)
                run_mine_process(stub)
            
            elif choice == '7':
                break
            else:
                print("Opção inválida. Escolha de 1 a 7.")
                
        except ValueError:
            print("Entrada inválida. Digite um número.")
        except grpc.RpcError as e:
            print(f"Erro de comunicação gRPC: {e.details()}")
        except KeyboardInterrupt:
            break

    print("Cliente encerrado.")


# =================================================================
# 5. BLOCL DE EXECUÇÃO
# =================================================================
if __name__ == '__main__':
    run()