import grpc
import time
import hashlib
from concurrent import futures

#arquivos gerado pelo protoc
import mine_grpc_pb2 as pb2
import mine_grpc_pb2_grpc as pb2_grpc

# estado do servidor
# -----------------------------------------------------------
# o estado armazena a transação atual e o historico dos ids
SERVER_STATE = {
    "current_transaction_id": 0, #id do challenge que está pendente (que vai mudando)
    "current_challenge_zeros": 1, #desafio inicial
    "transaction_history": {}  #ja resolvido: {1: {'status': 0, 'challenge': 3, 'solution': 'Client-nanana', 'winner': 100}}
}

# funcoes auxiliares
# -----------------------------------------------------------

def is_valid_solution(solution_str, challenge_value):
    #aqui verifica se o hash (SHA-1) da string atende o desafio 
    hash_obj = hashlib.sha1(solution_str.encode('utf-8'))
    hex_hash = hash_obj.hexdigest()
    target_zeros = '0' * challenge_value #desafios comecando com 0
    return hex_hash.startswith(target_zeros)

def generate_new_challenge(old_id):
    #incrementar o id e gerar novo desafio 
    #1. incrementa o ID da transação
    SERVER_STATE["current_transaction_id"] = old_id + 1
    
    #2. calcula novo desafio
    old_challenge = SERVER_STATE["current_challenge_zeros"] 
    new_challenge = old_challenge + 1
    
    #define a dificuldade maxima do challenge = 20
    MAX_CHALLENGE = 20
    if new_challenge > MAX_CHALLENGE:
        new_challenge = MAX_CHALLENGE 
        #nao deixa passar da dificuldade maxima
        
    SERVER_STATE["current_challenge_zeros"] = new_challenge 
    
    print(f"✅ NOVO DESAFIO GERADO: ID {SERVER_STATE['current_transaction_id']}, ZEROS {SERVER_STATE['current_challenge_zeros']}")


# classe SERVICO - implementacao do servdidor grpc
# -----------------------------------------------------------

class MinerServicer(pb2_grpc.apiServicer):

    def getTransactionId(self, request, context):
        #informa  o ID da transação atual disponivel p mineracao
        return pb2.intResult(result=SERVER_STATE["current_transaction_id"])

    def getChallenge(self, request, context):
        #informa o valor do desafio (qntd. de zeros) para um ID
        tx_id = request.transactionId
        #se tx id for atual, retorna o valor do challenge
        #se tiver no historio, retorna o desafio originalao que ja foi resolvido
        if tx_id == SERVER_STATE["current_transaction_id"]:
            return pb2.intResult(result=SERVER_STATE["current_challenge_zeros"])
        
        if tx_id in SERVER_STATE["transaction_history"]:
            return pb2.intResult(result=SERVER_STATE["transaction_history"][tx_id]['challenge'])
            
        # retornar -1 se o transactionID for invalido
        return pb2.intResult(result=-1)

    def getTransactionStatus(self, request, context):
        #retorna 1 p pendente, 0 p resolvido e -1 quando invalido 
        tx_id = request.transactionId
        
        if tx_id == SERVER_STATE["current_transaction_id"]:
            # define transacao atual sempre como pendente
            return pb2.intResult(result=1) 
        
        if tx_id in SERVER_STATE["transaction_history"]:
            #p transacao no historico resolvida
            return pb2.intResult(result=0) 
            
        #para id que nao é atual e ainda nao foi processado
        return pb2.intResult(result=-1) 

    def getWinner(self, request, context):
        # retorna o ID do cliente vencedor quando >0
        # 0 quando pendentee -1 para invalidos

        tx_id = request.transactionId
        # 1. verifica se o ID é o atual pendente
        if tx_id == SERVER_STATE["current_transaction_id"]:
            return pb2.intResult(result=0)
        # regra: 0 se ainda nao tem vencedor (pendente)
            
        # 2. verifica se o ID ta no histórico (resolvido)
        if tx_id in SERVER_STATE["transaction_history"]:
            return pb2.intResult(result=SERVER_STATE["transaction_history"][tx_id]['winner']) # Retorna o ID do vencedor
            
        # 3. ID invalido = -1
        return pb2.intResult(result=-1)

    def submitChallenge(self, request, context):
        #retona 1 p valido, 0 p invalido, 2 p resolvidos e -1 para invalidos
        #estados vao atualizando

        tx_id = request.transactionId
        client_id = request.clientId
        solution = request.solution

        # 1. verifica se o id atual é o certo (único que pode ser minerado)
        if tx_id != SERVER_STATE["current_transaction_id"]:
            if tx_id in SERVER_STATE["transaction_history"]:
                print(f"ALERTA: Cliente {client_id} submeteu ID {tx_id} já resolvido.")
                return pb2.intResult(result=2) #casos ja resolvidos
            else:
                print(f"ERRO: Cliente {client_id} submeteu ID {tx_id} inválido/obsoleto.")
                return pb2.intResult(result=-1) #ID invalido

        # 2. verifica a validade da solucao
        challenge = SERVER_STATE["current_challenge_zeros"]
        if not is_valid_solution(solution, challenge):
            print(f"FALHA: Cliente {client_id} submeteu solução inválida para ID {tx_id}.")
            return pb2.intResult(result=0) # solucao invalida
        
        # 3. VENCEDOR: salva o estado e gera o proximo desafio
        old_id = SERVER_STATE["current_transaction_id"]
        
        # salva a transacao no historico
        SERVER_STATE["transaction_history"][old_id] = {
            'status': 0, # resolvido
            'challenge': challenge,
            'solution': solution,
            'winner': client_id
        }
        
        # incrementa o id p o proximo desafio
        generate_new_challenge(old_id)
        
        print(f"\n🏆 SUCESSO! Solução aceita para ID {old_id} pelo ClientID {client_id}.")
        return pb2.intResult(result=1) # desafio com sucesso
    
    def getSolution(self, request, context):
        #retorna a estrutura de dados completa -status, solução, desafio
        tx_id = request.transactionId
        
        if tx_id == SERVER_STATE["current_transaction_id"]:
            # transação atual - PENDENTE
            return pb2.structResult(
                status=1,
                challenge=SERVER_STATE["current_challenge_zeros"],
                solution="N/A"
            )

        if tx_id in SERVER_STATE["transaction_history"]:
            # transação no histórico - RESOLVIDA
            hist = SERVER_STATE["transaction_history"][tx_id]
            return pb2.structResult(
                status=0,
                challenge=hist['challenge'],
                solution=hist['solution']
            )

        # ids invalidos
        return pb2.structResult(status=-1, challenge=0, solution="ID INVÁLIDO")

# FUNÇÃO PRINCIPAL - execução do servidor
# -----------------------------------------------------------
def serve():
    # numero maximo de threads
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_apiServicer_to_server(MinerServicer(), server)
    
    server_port = '50051' #porta usada para rodar o servidor
    server.add_insecure_port(f'[::]:{server_port}')
    server.start()
    print(f"Servidor gRPC Minerador rodando na porta {server_port}...")
    
    try:
        # mantem o servidor em loop até ser interrompido
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Servidor encerrado.")
        server.stop(0)


if __name__ == '__main__':
    # incializa o primeiro desafio
    generate_new_challenge(-1) # começa no ID 0
    serve()