# Citizen Assist AI

Assistente digital introdutório de orientação ao cidadão — Global Solution 2026.2 (FIAP), desafio CitizenTech.

**Integrante:** Gustavo Zibini Belizario — RM 561376 — Ciência da Computação, 1º ano (1CC)

> Protótipo educacional. Não é canal oficial de nenhum órgão público. As fichas de documentos pessoais são material didático fictício da "Central do Cidadão de Aurora".

## Organização do repositório

Um único projeto, com a contribuição de cada disciplina em sua própria pasta:

| Pasta | Disciplina | Conteúdo |
|---|---|---|
| [`assistente/`](assistente/) | Prompt and Artificial Intelligence | Agente (LangGraph + Groq) que responde só com base nas fichas, juiz LLM no golden dataset, notebook para Colab |
| [`dsa/`](dsa/) | Data Structures and Algorithms | Catálogo de serviços em lista encadeada (Python): CRUD, busca, merge sort, Big-O, testes |
| [`energia/`](energia/) | Soluções em Energias Renováveis e Sustentáveis | Análise do chuveiro elétrico × hábitos × aquecedor solar × fotovoltaica, integrada ao assistente |
| [`estatistica/`](estatistica/) | Estatística com Python | Análise de 5.565 municípios (Atlas do Desenvolvimento Humano, Censo 2010): probabilidade, testes de hipótese, regressões |
| [`iot-pico/`](iot-pico/) | Computer Organization and Architecture | Sentinela de Alagamento: Raspberry Pi Pico + MicroPython no Wokwi |
| [`computer-science/`](computer-science/) | Computer Science | Módulo de decisão lógica (tabela-verdade, Karnaugh, circuitos) |
| [`fichas/`](fichas/) | — | Fichas de referência FC-01 a FC-07 (fonte única de verdade do assistente) |

Cada pasta tem seu próprio `README.md` com instruções de execução.

## Execução rápida

```bash
cd dsa && python3 main.py                        # catálogo de serviços (DSA)
cd energia && python3 assistente_energia.py      # orientações de energia
cd estatistica && python3 analise_estatistica.py # análise estatística
```

O agente de IA roda no Google Colab: veja [`assistente/README.md`](assistente/README.md).
