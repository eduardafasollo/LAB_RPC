# INSTRUÇÕES DE COMPILAÇÃO E EXECUCÇÃO

Este guia detalha o processo de execução e teste do sistema Minerador PoW, simulando uma rede com um Servidor Árbitro Central e múltiplos Clientes Mineradores concorrentes, em um ambiente Linux (Ubuntu/WSL).

## Pré-requisitos
Pré-requisitos
Para executar este projeto, você deve ter os seguintes componentes instalados no seu sistema:

* **Python 3: Versão 3.6 ou superior.**
* **PIP: Gerenciador de pacotes do Python.**

Para criar o diretório raiz no projeto gRPC:
    python -m venv venv_miner
Para Instalar gRPC, Pybreaker, e os pacotes relacionados:
    pip install grpcio grpcio-tools pybreaker

# Compilação e Execução
Será necessário três terminais>
    1. Servidor
    2. Cliente 1
    3. Cliente 2

**Nos três terminais preciserá:**
i. Abrir a pasta referente ao projeto do Minerador gRPC.
    Utilize o comando (altere o nome de usuário) para abrir a pasta correta:
    cd /mnt/c/Users/Seu_Nome_de_Usuário/Downloads/lab_rpc/lab_rpc/grpc

ii. Com a pasta aberta, será necessário ativar o ambiente virtual para garantir que todas as dependências estejam carregadas. Para isso, utilize o comando:
    source venv_miner/bin/activate

1. TERMINAL 1 - SERVIDOR
    Utilize o comando abaixo para iniciar o servidor.
    python grpcCalc_server.py
    O sistema irá informar que o servidor está ativo e já ira gerar o primeiro Challenge pendente.

2. TERMINAL 2 - CLIENTE 1 
    Utilize o comando
    python grpcCalc_client.py localhost:50051 100
    Neste comando, passamos a porta onde nosso servidor está rodando e o ID (100) escolhido para o cliente 1. O ID (100) pode ser alterado a gosto do usuário.

3. TERMINAL 3 - CLIENTE 3
    Utilize o comando
    python grpcCalc_client.py localhost:50051 200
    Neste comando, passamos a porta onde nosso servidor está rodando e o ID (200) escolhido para o cliente 2. O ID (200) pode ser alterado a gosto do usuário.

# Modo de Uso do Menu Interativo

CLIENTE INICIADO: ID ÚNICO = 100. Conectando a localhost:50051...

--- CLIENTE MINERADOR gRPC ---
ID Cliente Atual: 100
1. getTransactionID (Consultar ID Pendente)
2. getChallenge (Consultar Valor do Desafio)
3. getTransactionStatus (Consultar Status)
4. getWinner (Consultar Vencedor)
5. GetSolution (Consultar Detalhes/Solução)
6. INICIAR MINERAÇÃO (MINE)
7. Sair
Escolha uma opção:

O cliente insere comandos no modo interativo. Para escolher a opção desejada, insira um número de 1 a 7.
Cada opção corresponde a uma chamada de procedimento remoto definida no seu protocolo (arquivo.proto).

getTransactionID: Consulta ID pendente. Pede ao servidor o ID da transação atual que está sendo disputada. Este é o identificador que os clientes precisam resolver.

getChallenge: Consulta valor do desafio. Pede ao Servidor o número de zeros que o hash da solução deve ter no início (ex: challenge_value = 3 significa que o hash deve começar com 000...). Este valor determina a dificuldade.

getTransactionStatus: Consulta status. Permite verificar o estado de uma transação específica (passando o ID). O Servidor retornará se a transação está pendente (aberta para mineração) ou resolvida (encerrada por um vencedor).

getWinner: Consulta vencedor. Retorna o ID do cliente que resolveu uma transação específica. Útil para verificar quem venceu uma disputa já resolvida.

GetSolution: Consulta detalhes/solução. Consulta e retorna os detalhes completos da solução vencedora de uma transação resolvida. Isso inclui o Nonce e o Hash SHA-1 válido submetido pelo vencedor.

INICIAR MINERAÇÃO: Função central de PoW. Esta é a função que automatiza o processo de mineração.
O Cliente: 
1) consulta o desafio e o ID; 
2) itera sobre valores de nonce (Provas de Trabalho); 
3) calcula o hash; e 
4) submete a primeira solução válida encontrada (chamando submitChallenge no Servidor).

