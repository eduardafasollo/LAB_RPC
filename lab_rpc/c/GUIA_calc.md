# INSTRUÇÕES DE COMPILAÇÃO E EXECUCÇÃO

Este guia detalha o processo para compilar e executar o projeto da Calculadora RPC (Remote Procedure Call) usando C e o `rpcgen` em um ambiente Linux (como WSL ou Debian/Ubuntu), com base no protocolo `rpcCalc.x`.

## Pré-requisitos

Para executar este projeto, você deve ter os seguintes pacotes instalados no seu sistema:

* **GNU Compiler Collection (GCC):** Para compilar os arquivos C.
* **RPC Tools (`rpcgen`):** Essencial para gerar os stubs do cliente e servidor.
* **RPCBIND / Portmapper:** O serviço responsável por registrar e localizar os programas RPC.
* **Bibliotecas TIRPC/Glibc:** Para ambientes Linux modernos, é crucial ter as bibliotecas de RPC.

Instalação em sistemas baseados em Debian/Ubuntu:
    sudo apt update
    sudo apt install build-essential rpcbind libtirpc-dev

# Compilação e Execução
Será necessário dois terminais>
    1. Servidor
    2. Cliente

i. Em um terminal, abra a pasta referente ao projeto da calculadora.
    Utilize o comando (altere o nome de usuário) para abrir a pasta correta:
    cd /mnt/c/Users/Seu_Nome_de_Usuário/Downloads/lab_rpc/lab_rpc/c

ii. Com a pasta aberta, insira o comando 
    ./rpcCalc_server 
    no terminal. O sistema não irá informar que o servidor está rodando.

iii. Em outro terminal, abra a pasta referente ao projeto utilizando o mesmo caminho definido a cima.

iv. Com a pasta aberta, insira o comando 
    ./rpcCalc_client localhost
    Aparecerá o menu interativo da calculadora, onde o cliente poderá escolher com qual operação deseja prosseguir.

# Modo de Uso do Menu Interativo

     CLIENTE RPC
---- CALCULADORA ----
1. Soma (x + y)
2. Subtração (x - y)
3. Multiplicação (x * y)
4. Divisão  (x / y)
5. Sair
Escolha a operação desejada:

O cliente insere comandos no modo interativo. 
Para escolher a opção desejada, insira um número de 1 a 5. A entrada deve ser um número inteiro, sem caracteres extras.
Para as operações de 1 a 4, a calculadora pedirá dois operandos (x e y), onde só serão aceitos números inteiros. Qualquer outro tipo de entrada será rejeitada (ex: 10,5, 10.5, caracteres especiais).
A partir deste momento, o cliente é livre para resolver quantas operações desejar.