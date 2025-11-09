# Sistemas Distribuídos RPC - Calculadora e Minerador
Este repositório contém dois projetos que demonstram a implementação de Comunicação por RPC utilizando diferentes frameworks.

1. 📂 Estrutura do Repositório
O repositório está organizado em duas subpastas principais:

c/: Contém a implementação da Calculadora Simples.
grpc/: Contém a implementação do Minerador.

ORIENTAÇÃO: Dentro de cada pasta haverá um 'GUIA.md' que contém as informações necessárias para rodar os programas.

2. 🔢 Projeto 1: Calculadora RPC 
O projeto implementa uma calculadora simples com operações de soma, subtração, divisão e multiplicação. 

2.1.  Metodologia de Implementação - C/rpcgen
A implementação segue o modelo tradicional de RPC em C, centrado na ferramenta rpcgen:

Definição da interface (rpcCalc.x): Um arquivo de definição de interface (.x) foi utilizado para declarar as funções remotas (ADD, SUB, DIV, MULT), a estrutura de dados para os operandos (operandos) e os identificadores de programa/versão.

Geração de stubs (rpcgen): O comando rpcgen gerou automaticamente os Stubs de cliente (rpcCalc_clnt.c) e servidor (rpcCalc_svc.c), além do código de conversão de dados (XDR) e o arquivo de cabeçalho (rpcCalc.h).

Implementação da lógica: A lógica das funções de operações foram implementadas manualmente no arquivo rpcCalc_server.c, nas funções que são invocadas pelo stub do servidor.

Implementação do cliente: O código do cliente (rpcCalc_client.c) foi modificado para receber os argumentos do usuário, estabelecer a conexão com o servidor e chamar as funções remotas através dos stubs gerados - ou seja, o cliente que escolhe qual operação o sistema vai fazer e quais valores ele irá utilizar.


3. 🪙 Projeto 2: Minerador 
Este projeto simula um sistema de Mineração com Prova de Trabalho onde clientes competem para resolver um desafio criptográfico (SHA-1).

3.1. Metodologia de Implementação - gRPC/Python
A implementação foca na alta concorrência e gerenciamento de estado:

i. Protocolo e stubs
    Protocol Buffers: O arquivo mine_grpc.proto define o serviço (api) e as mensagens que controlam o fluxo de trabalho da mineração.

    Geração de stubs: A ferramenta protoc gera os módulos Python (mine_grpc_pb2.py e mine_grpc_pb2_grpc.py) para comunicação eficiente.

ii. Lógica do Servidor (grpcCalc_server.py)
    O Servidor mantém o estado global (SERVER_STATE) com a transação pendente (current_transaction_id) e um histórico de vencedores.

    Proof-of-Work (PoW- prova de trabalho): A validação é feita via SHA-1 - um hash é considerado válido se começar com um número de zeros igual ao challenge_value.

    Concorrência (submitChallenge): A lógica é crítica para o PoW. O servidor aceita a primeira solução válida para o current_transaction_id, registra o clientID vencedor e imediatamente incrementa o ID da transação. Submissões subsequentes para o ID já resolvido são rejeitadas com o código 2 ("Já resolvido"), garantindo que apenas um minerador vença a disputa.

iii. Lógica do Cliente (grpcCalc_client.py)
    O cliente implementa a função Mine, que automatiza a prova de trabalho: busca o desafio, itera sobre nonces e submete a primeira solução válida encontrada. O uso de múltiplos clientes com IDs únicos (ex: 100 e 200) simula a disputa real.

3.2. Testes e Resultados Chave
Os testes focaram na garantia de que o servidor lida corretamente com a Concorrência e a Integridade do Estado:

Resultado 1.
Lógica de vitória: Ao rodar dois clientes simultaneamente, apenas um cliente obtém o retorno 1 (Sucesso) de submitChallenge. O outro cliente recebe o código 2 ("Já resolvido"), confirmando o funcionamento da disputa de PoW.

Resultado 2.
Dificuldade progressiva: O servidor incrementa o challenge_value (número de zeros) a cada transação resolvida, simulando o aumento de dificuldade. O limite de dificuldade (MAX_CHALLENGE = 20) garante que os testes não se prolonguem indefinidamente.

4. 🧠 Aprendizagem e Considerações Finais
O desenvolvimento dos projetos de Calculadora (em C/ONC RPC) e Minerador (em Python/gRPC) proporcionou um entendimento prático das arquiteturas de sistemas distribuídos e destacou diferenças cruciais em metodologias de implementação.

O desenvolvimento dos dois projetos revelou as vantagens de cada tecnologia RPC:
- RPC em C (antigo): É uma tecnologia mais próxima do sistema operacional. O trabalho é mais manual, exigindo lidar com a conversão de dados (XDR) e arquivos de código gerados pelo rpcgen.

- gRPC em Python (moderno): É muito mais fácil e rápido de implementar lógicas complexas, como o sistema de concorrência do minerador. O uso do Protocol Buffers cuida da serialização dos dados, permitindo que o foco total do programador seja na lógica do negócio (a mineração e a gestão do estado).

Em resumo, o gRPC se mostrou ideal para o projeto de alta concorrência (minerador), enquanto o RPC em C deu a base para entender o funcionamento fundamental dos sistemas distribuídos (calculadora).