# Roteiro do vídeo técnico (máximo 3 minutos)

Citizen Assist AI - Soluções em Energias Renováveis e Sustentáveis
Gustavo Zibini Belizario - RM 561376

Vídeo **não listado** no YouTube. Tempo-alvo: 2 min 45 s (folga de 15 s).
Os números das falas são os da tabela gerada por `calculos_energia.py` (seção 7 do README). Se mudar alguma premissa, rode o script de novo e atualize as falas.

| Tempo | O que mostrar na tela | Fala sugerida |
|---|---|---|
| **0:00 - 0:30**<br>1. Público e necessidade | Título do README (nome e RM). Depois, a seção 1 do README. | "Olá, sou Gustavo Zibini Belizario, RM 561376. Esta é a parte de Energia do Citizen Assist AI. O público são famílias de baixa renda da cidade de São Paulo. A necessidade é a água quente do banho. Nessas casas quase sempre é um chuveiro elétrico de cerca de 5.500 watts, um dos aparelhos que mais pesam na conta de luz." |
| **0:30 - 1:25**<br>2. Análise de consumo e comparação | `dados/premissas.csv` aberto rapidamente (colunas fonte e REAL/ESTIMADO). Depois a Tabela 1 de `resultados/comparacao.md`. Depois o gráfico `grafico_custo_acumulado.png`. | "Os dados vêm de fontes oficiais, como a tarifa da Enel homologada pela ANEEL, e cada um está marcado como real ou estimado. A conta é energia igual a potência vezes tempo. Uma família de 4 pessoas, com banhos de 10 minutos, gasta 110 kWh por mês, cerca de 87 reais sem impostos. Comparei para o mesmo banho: mudar hábitos, que economiza uns 43 reais por mês sem investir nada; o aquecedor solar comercial, que se paga em cerca de 4,6 anos; o aquecedor solar de baixo custo, em cerca de 2,9 anos; e a fotovoltaica, que exige mais dinheiro e telhado próprio. O gráfico mostra o custo acumulado em 10 anos." |
| **1:25 - 2:20**<br>3. Demonstração no assistente | Terminal: `python3 assistente_energia.py`. Opção 1 (gasto). Opção 7 (calculadora: 5 pessoas, 7 minutos, posição verão, Tarifa Social = sim). Opção 8 com um CPF fictício, mostrando o aviso. | "No assistente, a pessoa escolhe uma opção pelo teclado. Aqui ela vê quanto o chuveiro gasta, com a fonte e o aviso de que é estimativa. Na calculadora ela informa só o número de pessoas, os minutos e a posição do chuveiro, e recebe a comparação para o caso dela. Os números vêm do mesmo código da tabela. O assistente não pede dados pessoais e avisa se a pessoa digitar um CPF." |
| **2:20 - 2:45**<br>4. Recomendações e limitações | Seção 8 do README (recomendação) e seção 10 (limitações). Terminal com `python3 testes_energia.py` mostrando "OK". | "A recomendação é começar pelos hábitos, conferir a Tarifa Social e, em casa própria com sol no telhado, avaliar o aquecedor solar. Limitações: a tarifa está sem impostos, os tempos de banho e o rendimento solar são estimados e não há garantia de economia. Os testes automáticos conferem as contas e a coerência das respostas. Obrigado." |

## Dicas de gravação

- Aumentar a fonte do terminal e do editor antes de gravar.
- Deixar os arquivos já abertos em abas, na ordem do roteiro.
- Na demonstração, digitar devagar; se o tempo apertar, mostrar só as opções 1 e 7.
- Não mostrar e-mail, área de trabalho pessoal ou outras abas do navegador.
- Conferir no final: duração de até 3:00 e vídeo como **não listado**.
- Se quiser, citar em uma frase um ajuste feito a partir do teste com personas (README, seção 9.2): por exemplo, a calculadora passou a entender "somos 3 e o banho dura 12 minutos".
