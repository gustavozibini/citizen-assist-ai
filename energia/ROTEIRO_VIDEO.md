# Roteiro do vídeo – Energia: o banho quente na conta de luz

**Tempo:** até 3 minutos · **YouTube:** "Não listado"

## Antes de gravar

- Deixe abertos, nesta ordem:
  1. `energia/README.md` (no navegador do GitHub ou no editor)
  2. `energia/resultados/comparacao.md` (Tabela 1)
  3. `energia/resultados/grafico_custo_acumulado.png`
  4. Terminal na pasta: `cd ~/Documents/GusAgent/citizen-assist-ai/energia`
- Aumente a fonte do Terminal (Cmd + algumas vezes).

---

## 1. Apresentação (30 s)

**Mostre:** o início do README.

**Fale:**
> Olá, sou o Gustavo Zibini Belizario, RM 561376. Esta é a parte de Energia do Citizen Assist AI.
>
> O público são famílias de baixa renda de São Paulo. A necessidade é a água quente do banho. Quase sempre é um chuveiro elétrico de 5.500 watts, um dos aparelhos que mais pesam na conta de luz.

## 2. Comparação (55 s)

**Mostre:** a Tabela 1 de `comparacao.md`.

**Fale:**
> Os dados vêm de fontes oficiais, como a tarifa da Enel aprovada pela ANEEL.
>
> Uma família de 4 pessoas, com banho de 10 minutos, gasta 110 kWh por mês. São cerca de 87 reais.
>
> Comparei 4 alternativas para o mesmo banho:
> - mudar hábitos economiza 43 reais por mês, sem gastar nada;
> - o aquecedor solar comercial se paga em 4,6 anos;
> - o aquecedor solar de baixo custo se paga em 2,9 anos;
> - a placa fotovoltaica custa mais e exige telhado próprio.

**Mostre:** o gráfico.

> O gráfico mostra quanto cada opção custa em 10 anos.

## 3. Demonstração (55 s)

**Faça:** no Terminal, digite `python3 assistente_energia.py` e Enter.

**Digite 1**
> A pessoa escolhe pelo número. Aqui ela vê quanto o chuveiro gasta, com a fonte e o aviso de que é estimativa.

**Digite 7** e responda: `5` · `7` · `2` · `1`
> Na calculadora ela informa só quantas pessoas, os minutos e a posição do chuveiro. E recebe a comparação para o caso dela.

**Digite 8** e escreva: `meu cpf é 123.456.789-00, quanto gasto?`
> O assistente não pede dados pessoais. Se a pessoa digitar um CPF, ele avisa e não usa o número.

## 4. Encerramento (20 s)

**Fale:**
> A recomendação é começar pelos hábitos, ver se tem direito à Tarifa Social e, em casa própria, avaliar o aquecedor solar.
>
> Os valores são estimativas, sem impostos, e não há garantia de economia. Obrigado!

---

## Conferir antes de publicar

- [ ] Falei nome e RM
- [ ] Mostrei a tabela, o gráfico e o assistente funcionando
- [ ] No máximo 3 minutos
