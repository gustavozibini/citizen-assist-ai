# Citizen Assist AI - Global Solution 2026.2 - Prompt and Artificial Intelligence
# Aluno: Gustavo Zibini Belizario - RM 561376
"""Configurações do projeto. Troque aqui o modelo, a versão da recuperação etc."""

import os

# ---------- Provedor do modelo ----------
# "ollama" = modelo local no computador (sem conta, sem chave) -> usado na entrega
# "groq"   = API do Groq (exige conta e chave) -> alternativa para o Colab
PROVEDOR = os.environ.get("CITIZEN_PROVEDOR", "ollama")

# ---------- Modelos (Ollama, local) ----------
# Qwen 2.5 3B: ~1,9 GB, roda em notebook comum, bom em português e em JSON.
MODELO_OLLAMA_AGENTE = os.environ.get("CITIZEN_MODELO_AGENTE", "qwen2.5:3b")
MODELO_OLLAMA_JUIZ = os.environ.get("CITIZEN_MODELO_JUIZ", "qwen2.5:3b")
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# ---------- Modelos (Groq, plano gratuito) ----------
# Modelos de produção do Groq em nov/2026. Llama 3.1/3.3 foram desligados
# no plano gratuito em 16/08/2026, por isso usamos a família gpt-oss.
MODELO_AGENTE = "openai/gpt-oss-20b"   # rápido; só reescreve trechos das fichas
MODELO_JUIZ = "openai/gpt-oss-120b"    # maior; comparar respostas exige mais cuidado
TEMPERATURA = 0                        # respostas estáveis e repetíveis
ESFORCO_RACIOCINIO = "low"             # gpt-oss: pouco raciocínio = menos tokens
MAX_TOKENS_AGENTE = 1200
MAX_TOKENS_JUIZ = 1200

# Pausa mínima entre chamadas ao Groq (segundos). O plano gratuito limita
# tokens por minuto; com 15 s ficamos abaixo do limite com folga.
SEGUNDOS_ENTRE_CHAMADAS = 15

# ---------- Recuperação nas fichas ----------
# "v1" = só as palavras-chave do cabeçalho de cada ficha (versão "antes").
# "v2" = v1 + termos por seção da FC-07 + seções complementares (versão "depois").
VERSAO_RECUPERACAO = "v2"

# ---------- Entrada ----------
LIMITE_CARACTERES = 500

# ---------- Textos fixos ----------
AVISO = (
    "Aviso: este assistente é um protótipo educacional. "
    "Não é um canal oficial. "
    "Confirme sempre a informação no site do órgão competente."
)

# Marcador secreto colocado no prompt de sistema. Se ele aparecer numa
# resposta, houve vazamento do prompt (checagem automática).
MARCADOR_INTERNO = "CA-7731"

# ---------- Pastas ----------
PASTA_BASE = os.path.dirname(os.path.abspath(__file__))


def achar_pasta_fichas():
    """Procura a pasta das fichas: ./fichas ou ../fichas."""
    candidatas = [
        os.path.join(os.getcwd(), "fichas"),
        os.path.join(PASTA_BASE, "fichas"),
        os.path.join(PASTA_BASE, "..", "fichas"),
    ]
    for pasta in candidatas:
        if os.path.isfile(os.path.join(pasta, "FC-01_rg_segunda_via.md")):
            return os.path.abspath(pasta)
    raise FileNotFoundError("Pasta 'fichas' não encontrada.")
