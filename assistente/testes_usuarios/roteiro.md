# Roteiro dos testes com usuários — Citizen Assist AI

Gustavo Zibini Belizario — RM 561376

## Objetivo
Medir três indicadores com **pelo menos 5 pessoas de fora do grupo**:
1. **Acerto**: a pessoa encontrou a informação certa?
2. **Tempo**: quantos segundos levou para encontrar.
3. **Facilidade de uso**: questionário de 5 perguntas, escala de 1 a 5.

## Privacidade (obrigatório)
- **Não anote nome, idade, e-mail, telefone nem qualquer dado da pessoa.** Use só P1, P2, P3, P4, P5.
- Avise: "Não digite dados pessoais. Use só as perguntas das tarefas."
- Não grave tela, voz ou foto.
- Registre só: participante (P1..P5), tarefa, tempo em segundos, acertou (sim/não) e as 5 notas.

## Preparação
- Assistente aberto no menu de texto (`bash rodar_mac.sh conversar`, na pasta `assistente/`).
- Cronômetro (celular).
- Planilha `registro.csv` aberta.

## Instrução para o participante (ler em voz alta)
> "Este é um protótipo de assistente sobre documentos. Ele não é um canal oficial.
> Vou pedir 3 tarefas. Use o menu ou escreva sua pergunta, como preferir.
> Quando achar a resposta, me diga. Não digite dados pessoais."

## Tarefas
Comece o cronômetro quando terminar de ler a tarefa. Pare quando a pessoa disser a resposta.

| Tarefa | O que pedir | Resposta certa (para conferir) |
|---|---|---|
| T1 | "Descubra o que levar para fazer a segunda via do RG." | Certidão de nascimento ou casamento; comprovante de residência dos últimos 90 dias; boletim de ocorrência (roubo/furto) ou declaração de extravio (perda). (FC-01) |
| T2 | "Descubra se a Central atende aos sábados." | Não. Segunda a sexta, das 8h às 17h. (FC-07) |
| T3 | "Descubra com quanta antecedência dá para renovar a CNH." | A partir de 30 dias antes do vencimento. (FC-06) |

- **acertou = sim** se a pessoa disser a resposta certa (pode ser com outras palavras).
- Se passar de **180 s**, pare, anote `tempo_s = 180` e `acertou = nao`.

## Questionário (depois das 3 tarefas)
Notas de 1 (discordo totalmente) a 5 (concordo totalmente):

| Pergunta | Afirmação |
|---|---|
| q1 | Foi fácil encontrar a informação que eu procurava. |
| q2 | As respostas foram claras e fáceis de entender. |
| q3 | Ficou claro de onde veio a informação (ficha e data). |
| q4 | O menu e as mensagens de erro me ajudaram a seguir em frente. |
| q5 | Eu usaria este assistente de novo. |

## Como preencher `registro.csv`
- Uma linha por participante e tarefa (já estão criadas: P1..P5 × T1..T3).
- `tempo_s`: número inteiro de segundos.
- `acertou`: `sim` ou `nao`.
- `q1` a `q5`: preencha **só na linha da T3** de cada participante.
- Depois, salve o arquivo em `testes_usuarios/` e calcule os indicadores com `avaliacao.py` (ou a seção 13 do notebook).

## Indicadores calculados pelo notebook
- Tempo médio e mediana por tarefa (s).
- Acerto por tarefa e geral (%).
- Facilidade média (1 a 5) e média de cada pergunta.
