# Roteiro de testes com usuários - módulo de Energia

Citizen Assist AI - Soluções em Energias Renováveis e Sustentáveis
Aluno: Gustavo Zibini Belizario - RM 561376

> **Situação: testes com pessoas reais não realizados; foi feito o teste simulado com personas (`teste_simulado.py`, README seção 9.2).**
> Este roteiro está pronto para ser aplicado. Os resultados vão em `registro.md`.

## Objetivo

Verificar se pessoas do público (famílias de baixa renda de São Paulo, ou pessoas próximas a esse perfil) **entendem** as orientações sobre o banho quente e se acham que elas são **úteis**.

## Cuidados com dados pessoais

- Não anotar nome, idade, endereço, telefone, e-mail, CPF nem número da conta de luz.
- Cada participante recebe só um código: P1, P2, P3...
- Se for útil, anotar só o perfil geral, sem identificar a pessoa (ex.: "mora de aluguel", "tem Tarifa Social", "não sabe").
- Pedir permissão antes de começar e explicar que pode parar quando quiser.
- Não gravar voz nem imagem do participante.
- Na calculadora, a pessoa pode usar números reais da casa (moradores, minutos) ou inventados. Isso não é anotado com identificação.

## Preparação (5 minutos)

1. Abrir um terminal na pasta `energia/` e rodar `python3 assistente_energia.py`.
2. Ter em mãos este roteiro e uma cópia em branco do `registro.md`.
3. Falar para o participante (sugestão):
   "Este é um protótipo de um assistente que explica o gasto do banho quente na conta de luz. Não é da Enel nem do governo. Quero saber se as respostas são fáceis de entender. Quem está sendo testado é o assistente, não você."

## Situações a testar

Para cada situação: leia a tarefa para a pessoa, deixe que ela mesma use o teclado, observe sem ajudar (ajude só se travar por mais de 1 minuto e anote que ajudou).

### Situação 1 - Entender quanto o banho custa e como economizar

Tarefa: "Descubra quanto o chuveiro gasta por mês e o que dá para fazer para gastar menos sem comprar nada."
Caminho esperado: opções 1 e 2 do menu, ou opção 8 com uma pergunta escrita.
Observar: encontrou as opções sozinho? Leu o aviso de estimativa?

### Situação 2 - Fazer a conta do próprio caso na calculadora

Tarefa: "Use a calculadora com o número de pessoas e o tempo de banho de uma casa que você conhece (pode ser inventado)."
Caminho esperado: opção 7, responder as perguntas.
Observar: entendeu "posição verão" e "potência em watts"? Entendeu a diferença entre as alternativas B, C1, C2 e D? Entendeu o que é "retorno" (payback)?

### Situação 3 - Tarifa Social e aquecedor solar

Tarefa: "Descubra se uma família do CadÚnico tem desconto na conta e se vale a pena colocar aquecedor solar."
Caminho esperado: opções 5 e 3, ou perguntas escritas na opção 8.
Observar: entendeu que a Tarifa Social não zera a conta quando o consumo passa de 80 kWh? Entendeu que o aquecedor solar depende de telhado e de morar em casa própria?

## Perguntas depois de cada situação (compreensão)

Use a escala: 1 = nada, 2 = pouco, 3 = mais ou menos, 4 = bem, 5 = muito bem.

- C1. "Com suas palavras, quanto o banho custa por mês no exemplo?" (anotar se a resposta bate com o que o assistente mostrou)
- C2. "O que o assistente recomenda fazer primeiro?" (esperado: mudar hábitos, sem custo)
- C3. "Esses valores são garantidos?" (esperado: não, são estimativas)
- C4. "De 1 a 5, o quanto o texto foi fácil de entender?"

## Perguntas no final (utilidade)

- U1. "De 1 a 5, o quanto essas orientações seriam úteis para uma família como a que você imaginou?"
- U2. "Você mudaria algum hábito depois de ver isso? Qual?"
- U3. "Teve alguma palavra difícil? Qual?"
- U4. "O que faltou ou o que você mudaria no assistente?"
- U5. "Você confia nos números? Por quê?"

## Depois dos testes

1. Preencher `registro.md` com uma linha por participante e situação.
2. Listar os problemas que mais apareceram.
3. Fazer os ajustes no código ou nos textos (`assistente_energia.py`).
4. Rodar `python3 testes_energia.py -v` de novo.
5. Anotar no `registro.md` e na seção 9.2 do `README.md` o que foi ajustado e por quê.

Sugestão de quantidade: pelo menos 3 participantes, cerca de 15 minutos cada.
