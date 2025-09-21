📌Descrição do Projeto
O Projeto é um programa simples em Python que permite aos usuários registrar pensamentos, anotações ou eventos diários em um arquivo de texto. Cada entrada é armazenada junto com a data e a hora exatas em que foi escrita, tornando-o um diário eletrônico prático e acessível.

Os usuários podem visualizar todas as entradas anteriores e continuar adicionando novas anotações sempre que quiserem. O programa apresenta um menu interativo, onde é possível escolher entre escrever no diário, ler todas as entradas ou sair do programa.

🎯Objetivos do Projeto

✅ Ensinar a trabalhar com manipulação de arquivos (open, write, read).

✅ Demonstrar o uso de datas e horários em Python com datetime.

✅ Desenvolver habilidades em (if, while).

✅ Criar um programa prático e funcional, incentivando a criatividade.

✅ Introduzir conceitos básicos de tratamento de arquivos e interação com o usuário.


🛠Funcionamento do Programa

1️⃣ Quando o programa inicia, um menu aparece com três opções:
O usuário pode digitar um texto que será salvo com a data e a hora.
O programa exibe todas as anotações salvas.
Finaliza o programa.
2️⃣ Quando o usuário escolhe escrever no diário, ele digita um texto, que será salvo no arquivo diario.txt no seguinte formato:
csharp
CopiarEditar
[20/03/2025 14:35:12] Hoje foi um dia muito produtivo! Consegui estudar bastante.

3️⃣ O programa verifica se o arquivo existe e exibe todas as entradas salvas. Caso o diário esteja vazio, uma mensagem informativa aparece.

4️⃣ O usuário pode escolher sair do programa a qualquer momento digitando a opção correspondente.


🔧Código Explicado
📂Manipulação de Arquivos
O programa usa open("diario.txt", "a") para adicionar novas entradas ao diário.
O modo "a" (append) garante que as novas anotações sejam adicionadas sem apagar as antigas.
Para ler o diário, usamos open("diario.txt", "r") e readlines() para exibir cada linha armazenada.

🕒Uso de Datas e Horas
O módulo datetime é utilizado para capturar a data e a hora no momento da escrita.
datetime.now().strftime("%d/%m/%Y %H:%M:%S") formata a data de maneira legível para o usuário.

🔄Estrutura de Controle
O loop while True mantém o programa em execução até o usuário escolher sair.
if-elif é usado para processar a escolha do usuário no menu.
os.path.exists("diario.txt") garante que o programa não tente ler um arquivo inexistente.
