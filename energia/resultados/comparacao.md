# Comparação das alternativas para o banho quente

Arquivo gerado por `calculos_energia.py`. Não edite à mão: rode o script de novo.

Necessidade comparada: banho quente de 4 pessoas, 1 banho por pessoa por dia, 10 minutos, chuveiro de 5.500 W, em São Paulo (SP). Período: mês de 30 dias, ano de 12 meses e horizonte de 10 anos.

## Tabela 1 - Tarifa residencial convencional (0,78938 R$/kWh, sem impostos)

| Alt. | Alternativa | Consumo da rede (kWh/mês) | Consumo (kWh/ano) | Custo (R$/mês) | Custo (R$/ano) | Investimento (R$) | Economia (R$/mês) | Economia (R$/ano) | Payback simples | CO2 evitado (kg/ano) | Saldo em 10 anos (R$) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| A | Chuveiro elétrico sem cuidado (caso-base) | 110,0 | 1.320,0 | 86,83 | 1.041,98 | 0,00 | 0,00 | 0,00 | sem investimento | 0,0 | 0,00 |
| B | Hábitos: banho curto e posição verão | 56,1 | 673,2 | 44,28 | 531,41 | 0,00 | 42,55 | 510,57 | sem investimento | 24,9 | 5.105,71 |
| C1 | Aquecedor solar comercial + chuveiro de apoio | 33,0 | 396,0 | 26,05 | 312,59 | 3.359,57 | 60,78 | 729,39 | 55 meses (4,6 anos) | 35,6 | 3.934,30 |
| C2 | Aquecedor solar de baixo custo (ASBC) + apoio | 55,0 | 660,0 | 43,42 | 520,99 | 1.500,00 | 43,42 | 520,99 | 35 meses (2,9 anos) | 25,4 | 3.709,91 |
| D | Solar fotovoltaica (compensação de energia) | 0,0 | 0,0 | 0,00 | 0,00 | 6.392,10 | 86,83 | 1.041,98 | 74 meses (6,1 anos) | 50,8 | 4.027,72 |

## Tabela 2 - Família com Tarifa Social (80 kWh gratuitos; excedente a 0,61191 R$/kWh, sem impostos)

Premissa estimada: o resto da casa consome 100 kWh/mês. Assim a gratuidade já é usada pelos outros aparelhos e o banho é todo pago na tarifa do excedente.

| Alt. | Alternativa | Consumo da rede (kWh/mês) | Consumo (kWh/ano) | Custo (R$/mês) | Custo (R$/ano) | Investimento (R$) | Economia (R$/mês) | Economia (R$/ano) | Payback simples | CO2 evitado (kg/ano) | Saldo em 10 anos (R$) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| A | Chuveiro elétrico sem cuidado (caso-base) | 110,0 | 1.320,0 | 67,31 | 807,72 | 0,00 | 0,00 | 0,00 | sem investimento | 0,0 | 0,00 |
| B | Hábitos: banho curto e posição verão | 56,1 | 673,2 | 34,33 | 411,94 | 0,00 | 32,98 | 395,78 | sem investimento | 24,9 | 3.957,83 |
| C1 | Aquecedor solar comercial + chuveiro de apoio | 33,0 | 396,0 | 20,19 | 242,32 | 3.359,57 | 47,12 | 565,40 | 71 meses (5,9 anos) | 35,6 | 2.294,48 |
| C2 | Aquecedor solar de baixo custo (ASBC) + apoio | 55,0 | 660,0 | 33,66 | 403,86 | 1.500,00 | 33,66 | 403,86 | 45 meses (3,7 anos) | 25,4 | 2.538,61 |
| D | Solar fotovoltaica (compensação de energia) | 0,0 | 0,0 | 0,00 | 0,00 | 6.392,10 | 67,31 | 807,72 | 95 meses (7,9 anos) | 50,8 | 1.685,11 |

## Análise de sensibilidade

- Aquecedor solar comercial com a fração solar mínima da Lei Solar de São Paulo (40%): economia de R$ 34,73 por mês e payback de 97 meses (8,1 anos) (no caso-base: 55 meses (4,6 anos)).
- No inverno a irradiação cai para 3,784 kWh/m2/dia. O coletor comercial de 2,0 m2 capta no máximo 90,8 kWh/mês de calor útil, ou 83% do caso-base. O apoio elétrico é mais usado no inverno.
- Emissões do caso-base: 50,8 kg CO2/ano com o fator de 0,0385 kg CO2/kWh. Com o fator alternativo de 0,0247 kg CO2/kWh seriam 32,6 kg CO2/ano.
- Fotovoltaica: o banho do caso-base pede cerca de 1,07 kWp. Na tabela usamos 6,00 R$/Wp (sistema pequeno, estimado). Com o preço médio de um sistema de 4 kWp (2,84 R$/Wp), o investimento cairia para R$ 3.025,59 e o retorno para 35 meses (2,9 anos). Nos dois casos a compensação tem cobranças mínimas que não entraram no cálculo.
- Fotovoltaica comprando um sistema inteiro de 2 kWp (cerca de R$ 12.000,00, estimado) e pagando só com a economia do banho: retorno em 138 meses (11,5 anos).

## Observações

- Valores sem ICMS, PIS/Cofins, bandeira tarifária e iluminação pública.
- Tarifa mantida constante no horizonte. Sem custo de manutenção.
- Na alternativa D, o consumo da rede é o líquido depois da compensação (simplificação).
- São estimativas. O resultado real depende do uso, do clima e da instalação.
- Origem de cada número: `dados/premissas.csv` e `dados/FONTES.md`.
