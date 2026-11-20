# Roteiro do vídeo – Energia

**Até 3 minutos · YouTube "Não listado"**

Antes de gravar, deixe abertos no navegador, nesta ordem:
1. README: https://github.com/gustavozibini/citizen-assist-ai/tree/main/energia
2. Tabela: https://github.com/gustavozibini/citizen-assist-ai/blob/main/energia/resultados/comparacao.md
3. Gráfico: https://github.com/gustavozibini/citizen-assist-ai/blob/main/energia/resultados/grafico_custo_acumulado.png
4. Terminal já na pasta: `cd ~/Documents/GusAgent/citizen-assist-ai/energia`

---

**[mostre o README]**

Olá, eu sou o Gustavo, e esta é a parte de Energias Renováveis do Citizen Assist AI. O público são as famílias de baixa renda de São Paulo, e a necessidade é a água quente do banho. Nessas casas quem esquenta a água é o chuveiro elétrico, de cerca de 5.500 watts, que pesa muito na conta de luz.

**[mostre a tabela]**

Usei dados de fontes oficiais, como a tarifa da Enel aprovada pela ANEEL, e marquei o que é dado real e o que é estimativa. A conta é simples: energia é potência vezes tempo. Uma família de quatro pessoas, com banhos de dez minutos, gasta 110 quilowatts-hora por mês só no chuveiro, cerca de 87 reais sem impostos.

Comparei quatro alternativas para esse mesmo banho. Mudar hábitos, com banho mais curto e o chuveiro na posição verão, economiza uns 43 reais por mês sem gastar nada. O aquecedor solar comercial custa cerca de 3.360 reais e se paga em quatro anos e meio. O aquecedor solar de baixo custo custa 1.500 reais e se paga em menos de três anos. E a placa fotovoltaica exige telhado próprio e um investimento maior.

**[mostre o gráfico]**

Neste gráfico está o custo acumulado de cada opção em dez anos, somando o investimento e a conta de luz. A linha azul é o chuveiro sem nenhum cuidado, que termina como a mais cara. As opções solares começam mais caras por causa do investimento, mas cruzam a linha azul entre três e seis anos. E a mudança de hábitos fica abaixo de todas, porque não custa nada.

**[mostre o Terminal]**

**[digite `python3 assistente_energia.py`]** Agora, no assistente. A pessoa escolhe pelo número do menu. **[digite `1`]** Na opção 1 ela vê quanto o chuveiro gasta, com a fonte e o aviso de que é uma estimativa. **[digite `7`]** Na opção 7 está a calculadora: eu informo cinco pessoas **[digite `5`]**, sete minutos de banho **[digite `7`]**, chuveiro na posição verão **[digite `2`]** e que a família tem Tarifa Social **[digite `1`]**, e o assistente mostra a comparação para esse caso. **[digite `8`]** Na opção 8 a pessoa escreve do jeito dela, **[digite `meu cpf é 123.456.789-00, quanto gasto?`]** e se digitar um CPF o assistente avisa que não precisa desse dado e não usa o número. **[digite `0`]**

Para fechar, a recomendação é começar pelos hábitos, que não custam nada, conferir se a família tem direito à Tarifa Social e, em casa própria com sol no telhado, avaliar o aquecedor solar. São estimativas sem impostos e não há garantia de economia. Obrigado!

