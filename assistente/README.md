# Citizen Assist AI — Prompt and Artificial Intelligence

**Gustavo Zibini Belizario — RM 561376** — FIAP, Ciência da Computação, Global Solution 2026.2 (individual)

Assistente sobre documentos pessoais (RG, CPF, título, carteira de trabalho, certidões, CNH) que responde
**somente** com as 7 fichas da Central do Cidadão de Aurora (fictícia), citando ficha e data.
Feito com **LangGraph** + **Ollama** (`gemma3:4b`, local, sem conta nem chave). Relatório completo: `Relatorio_Citizen_Assist_AI.md`.

## Rodar (Mac/Linux, com Ollama)

1. Instale o Ollama (https://ollama.com/download) e abra o aplicativo.
2. No Terminal:

```bash
ollama pull gemma3:4b
cd citizen-assist-ai/assistente
bash rodar_mac.sh            # golden dataset antes/depois + juiz
bash rodar_mac.sh conversar                                   # usar o assistente (menu de texto)
```

Resultados em `resultados/` (a primeira tentativa com `qwen2.5:3b` está em `resultados_qwen2.5-3b/`).

## Arquivos

| Arquivo | O que é |
|---|---|
| `rodar_mac.sh`, `rodar_local.py` | **Execução principal** com Ollama: avaliação antes/depois e menu de conversa. |
| `rejulgar.py` | Reavalia respostas salvas com o juiz atual, sem chamar o agente. |
| `resultados/` | Resultados reais (gemma3:4b): `antes.csv`, `depois.csv`, `resumo_comparativo.md`, `conferencia_manual.csv`. |
| `Citizen_Assist_AI.ipynb` | Alternativa no Colab com Groq (exige conta e chave). |
| `Relatorio_Citizen_Assist_AI.md` | Relatório: justificativas, régua do juiz, resultados, limitações. |
| `config.py` | Modelos, versão da recuperação, limites e aviso. |
| `fichas.py` | Leitura das fichas, divisão em seções e busca por palavras-chave (v1 e v2). |
| `seguranca.py` | Validação de entrada, dados pessoais (regex) e prompt injection. |
| `prompts.py` | Prompt de sistema e respostas prontas. |
| `agente.py` | Grafo LangGraph (7 nós) e verificação final. |
| `modelos.py` | Ollama (local), Groq (chave via Secrets/variável) e modelos falsos para teste offline. |
| `juiz.py` | LLM as a Judge, régua e checagens determinísticas. |
| `avaliacao.py` | Roda o golden, salva CSVs, compara antes/depois, indicadores dos testes com usuários. |
| `interface.py` | Menu de texto e interface Gradio (opcional). |
| `diagrama.py` / `grafo_agente.png` | Diagrama do grafo. |
| `golden_dataset.csv` | As 26 mensagens da seção 4.1 do enunciado. |
| `testes.py` | Testes offline (96 verificações). Saída em `evidencias/saida_testes.txt`. |
| `conferir_golden.py` | Confere o golden contra o texto do PDF. Saída em `evidencias/conferencia_golden_pdf.txt`. |
| `gerar_notebook.py` | Gera o notebook a partir dos `.py`, das fichas e do golden. |
| `testes_usuarios/` | `roteiro.md`, `registro.csv` (para teste com pessoas), `teste_simulado.py` e `resultado_simulado.csv` (teste com 5 personas). |
| `evidencias/` | Saídas reais dos testes offline e da execução offline do notebook. |

## Alternativa: Google Colab com Groq

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

## Rodar o notebook localmente (alternativa com Groq)

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
O teste com 5 personas roda com `.venv/bin/python testes_usuarios/teste_simulado.py` (Ollama aberto) e salva
`testes_usuarios/resultado_simulado.csv`. Resultados na seção 10 do relatório. Para repetir com pessoas, siga
`testes_usuarios/roteiro.md` e preencha `testes_usuarios/registro.csv`.
