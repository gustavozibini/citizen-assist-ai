# Citizen Assist AI — Prompt and Artificial Intelligence

**Gustavo Zibini Belizario — RM 561376** — FIAP, Ciência da Computação, Global Solution 2026.2 (individual)

Assistente sobre documentos pessoais (RG, CPF, título, carteira de trabalho, certidões, CNH) que responde
**somente** com as 7 fichas da Central do Cidadão de Aurora (fictícia), citando ficha e data.
Feito com **LangGraph** + **Groq**. Relatório completo: `Relatorio_Citizen_Assist_AI.md`.

## Arquivos

| Arquivo | O que é |
|---|---|
| `Citizen_Assist_AI.ipynb` | **Entregável principal.** Notebook autocontido para o Colab (sem saídas: execute você). |
| `Relatorio_Citizen_Assist_AI.md` | Relatório: justificativas, régua do juiz, resultados, limitações. |
| `config.py` | Modelos, versão da recuperação, limites e aviso. |
| `fichas.py` | Leitura das fichas, divisão em seções e busca por palavras-chave (v1 e v2). |
| `seguranca.py` | Validação de entrada, dados pessoais (regex) e prompt injection. |
| `prompts.py` | Prompt de sistema e respostas prontas. |
| `agente.py` | Grafo LangGraph (7 nós) e verificação final. |
| `modelos.py` | Groq (chave via Secrets/variável) e modelos falsos para teste offline. |
| `juiz.py` | LLM as a Judge, régua e checagens determinísticas. |
| `avaliacao.py` | Roda o golden, salva CSVs, compara antes/depois, indicadores dos testes com usuários. |
| `interface.py` | Menu de texto e interface Gradio (opcional). |
| `diagrama.py` / `grafo_agente.png` | Diagrama do grafo. |
| `golden_dataset.csv` | As 26 mensagens da seção 4.1 do enunciado. |
| `testes.py` | Testes offline (96 verificações). Saída em `evidencias/saida_testes.txt`. |
| `conferir_golden.py` | Confere o golden contra o texto do PDF. Saída em `evidencias/conferencia_golden_pdf.txt`. |
| `gerar_notebook.py` | Gera o notebook a partir dos `.py`, das fichas e do golden. |
| `testes_usuarios/` | `roteiro.md` e `registro.csv` (em branco, para preencher). |
| `evidencias/` | Saídas reais dos testes offline e da execução offline do notebook. |

## Rodar no Google Colab (com IA)

1. Crie a chave gratuita: **console.groq.com** > **API Keys** > **Create API Key** (começa com `gsk_`).
2. Abra `Citizen_Assist_AI.ipynb` no Colab (Arquivo > Fazer upload de notebook).
3. Ícone de **chave** (Secrets) na barra esquerda > **Add new secret** > nome `GROQ_API_KEY`, valor = sua chave,
   ative **Notebook access**. Não cole a chave no código.
4. **Ambiente de execução > Executar tudo.** A avaliação leva uns 15 minutos (limite gratuito do Groq).
5. Os resultados ficam em `resultados/` no Colab: `antes.csv`, `depois.csv`, `resumo_comparativo.csv/.md`,
   `comparacao.png`, `conferencia_manual.csv`. **Baixe-os** (ícone de pasta > botão direito > Fazer download),
   porque o Colab apaga os arquivos ao fechar.
6. No fim, o menu de texto abre. Digite um número (1 a 7) ou uma pergunta. `sair` encerra.
7. Para salvar o "notebook executado": Arquivo > Fazer download > .ipynb.

Se aparecer erro de limite (429) ou cota diária, espere alguns minutos e rode de novo, ou aumente
`SEGUNDOS_ENTRE_CHAMADAS` em `config.py` (célula `%%writefile config.py`).
Para trocar o modelo, edite `MODELO_AGENTE` / `MODELO_JUIZ` na mesma célula.

**Sem chave:** na célula de configuração, `MODO_OFFLINE = True`. Roda com modelos falsos (sem IA), salva em
`resultados_offline/` e marca tudo como SIMULADO.

## Rodar localmente

```bash
pip install langgraph==1.2.22 langchain-groq==1.2.0 langchain-core==1.8.1 pandas matplotlib
cd assistente
python testes.py                       # testes offline, não precisa de chave
export GROQ_API_KEY=gsk_...            # só para usar o Groq
jupyter notebook Citizen_Assist_AI.ipynb
```

O código procura as fichas em `./fichas` ou `../fichas`. Depois de alterar um `.py`, rode
`python gerar_notebook.py` para atualizar o notebook.

## Testes com usuários
Siga `testes_usuarios/roteiro.md` com 5 pessoas de fora, sem identificar ninguém. Preencha
`testes_usuarios/registro.csv`, envie para a mesma pasta no Colab e rode a seção 13 do notebook.
