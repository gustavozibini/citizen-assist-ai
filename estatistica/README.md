# Estatística com Python - Global Solution 2026.2 (CitizenTech)

**Projeto:** Citizen Assist AI
**Aluno:** Gustavo Zibini Belizario - RM 561376 (trabalho individual)

## Arquivos da entrega

| Arquivo | O que é |
|---|---|
| `base_dados.csv` | Base de dados (5.565 municípios, 16 colunas, Censo 2010) |
| `analise_estatistica.py` | Código principal: questões 02 a 06, na ordem do enunciado |
| `Relatorio_Estatistico.pdf` | Relatório estatístico (questão 07) |
| `preparar_base.py` | Gera `base_dados.csv` a partir do arquivo original (só filtra e seleciona colunas) |
| `gerar_relatorio.py` | Monta o PDF a partir de `resultados.json` e de `figuras/` |
| `figuras/` | Gráficos gerados pelo código |
| `resultados.json` | Números calculados pelo código (usados no relatório) |
| `dados_brutos/pnud_muni.rda` | Arquivo original baixado da fonte |

## Como executar

```
pip install pandas numpy scipy statsmodels scikit-learn matplotlib seaborn
python analise_estatistica.py
```

Basta ter `analise_estatistica.py` e `base_dados.csv` na mesma pasta. O script imprime os
resultados de cada alínea no terminal, salva os gráficos em `figuras/` e grava `resultados.json`.
A semente aleatória é fixa (561376), então os resultados são sempre os mesmos.

Opcional (refazer a base e o PDF):

```
pip install pyreadr reportlab
python preparar_base.py
python gerar_relatorio.py
```

## Fonte dos dados

Atlas do Desenvolvimento Humano no Brasil 2013 (PNUD, Ipea e Fundação João Pinheiro), com base
nos Censos Demográficos do IBGE. Tabela `pnud_muni` do pacote abjData:
https://github.com/abjur/abjData - acesso em 16/11/2026.
