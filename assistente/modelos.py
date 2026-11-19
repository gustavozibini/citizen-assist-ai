# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Criação dos modelos: Ollama (local, padrão), Groq (alternativa) ou modelos falsos para testes offline.

Os modelos falsos são determinísticos e NÃO usam IA. Servem só para testar
o grafo e o pipeline sem internet. Tudo que eles geram é marcado como SIMULADO.
"""

import json
import os
import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

import config
from fichas import STOPWORDS, normalizar

# ================================================================ chave


def ler_chave_groq():
    """Lê a chave dos Secrets do Colab ou da variável GROQ_API_KEY. Nunca do código."""
    try:
        from google.colab import userdata  # só existe no Colab
        chave = userdata.get("GROQ_API_KEY")
        if chave:
            return chave
    except Exception:
        pass
    chave = os.environ.get("GROQ_API_KEY")
    if not chave:
        raise RuntimeError(
            "Chave GROQ_API_KEY não encontrada. No Colab: ícone de chave (Secrets) > "
            "Add new secret > nome GROQ_API_KEY > ative 'Notebook access'."
        )
    return chave


def _criar_groq(modelo, max_tokens):
    from langchain_core.rate_limiters import InMemoryRateLimiter
    from langchain_groq import ChatGroq

    limitador = InMemoryRateLimiter(
        requests_per_second=1 / config.SEGUNDOS_ENTRE_CHAMADAS,
        check_every_n_seconds=0.5,
        max_bucket_size=1,
    )
    return ChatGroq(
        model=modelo,
        temperature=config.TEMPERATURA,
        reasoning_effort=config.ESFORCO_RACIOCINIO,
        max_tokens=max_tokens,
        max_retries=6,                 # espera e tenta de novo se bater no limite (429)
        rate_limiter=limitador,
        api_key=ler_chave_groq(),
    )


def _criar_ollama(modelo, max_tokens, saida_json=False):
    """Modelo local pelo Ollama. Temperatura 0 = respostas estáveis."""
    from langchain_ollama import ChatOllama

    opcoes = dict(model=modelo, temperature=config.TEMPERATURA, num_predict=max_tokens,
                  base_url=config.OLLAMA_URL)
    if saida_json:
        opcoes["format"] = "json"      # o juiz precisa devolver JSON válido
    return ChatOllama(**opcoes)


def nome_modelo_agente():
    return config.MODELO_OLLAMA_AGENTE if config.PROVEDOR == "ollama" else config.MODELO_AGENTE


def nome_modelo_juiz():
    return config.MODELO_OLLAMA_JUIZ if config.PROVEDOR == "ollama" else config.MODELO_JUIZ


def criar_llm_agente(modo_offline=False):
    if modo_offline:
        return LLMFalso()
    if config.PROVEDOR == "ollama":
        return _criar_ollama(config.MODELO_OLLAMA_AGENTE, config.MAX_TOKENS_AGENTE)
    return _criar_groq(config.MODELO_AGENTE, config.MAX_TOKENS_AGENTE)


def criar_llm_juiz(modo_offline=False):
    if modo_offline:
        return JuizFalso()
    if config.PROVEDOR == "ollama":
        return _criar_ollama(config.MODELO_OLLAMA_JUIZ, config.MAX_TOKENS_JUIZ, saida_json=True)
    return _criar_groq(config.MODELO_JUIZ, config.MAX_TOKENS_JUIZ)


# ================================================================ modelos falsos


def _entre(texto, tag):
    achou = re.search(rf"<{tag}>\n?(.*?)\n?</{tag}>", texto, re.S)
    return achou.group(1) if achou else ""


def _palavras(texto):
    return set(normalizar(texto).split()) - STOPWORDS


class LLMFalso(BaseChatModel):
    """Agente falso: devolve as linhas das fichas mais parecidas com a pergunta."""

    @property
    def _llm_type(self):
        return "llm-falso-offline"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        pedido = messages[-1].content
        pergunta = _palavras(_entre(pedido, "mensagem_usuario"))
        # Cada trecho começa com "[FC-xx | Seção]" e pode ter várias linhas.
        trechos = [t.strip() for t in re.split(r"(?m)^(?=\[FC-)", _entre(pedido, "fichas")) if t.strip()]
        ordenados = sorted(trechos, key=lambda t: -len(pergunta & _palavras(t)))
        corpo = "\n".join(
            re.sub(r"^\[(FC-\d\d) \| ([^\]]+)\]\s*(.*)$", r"\2: \3 (\1)", " ".join(t.split()))
            for t in ordenados[:2]
        ) or "Não encontrei essa informação nas fichas."
        texto = "[SIMULADO - modo offline, sem IA]\n" + corpo
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=texto))])


class JuizFalso(BaseChatModel):
    """Juiz falso: nota por sobreposição de palavras. Só para testar o pipeline."""

    @property
    def _llm_type(self):
        return "juiz-falso-offline"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        pedido = messages[-1].content
        esperado = _palavras(_entre(pedido, "resposta_esperada"))
        resposta = _entre(pedido, "resposta_do_agente")
        fichas = re.findall(r"FC-\d\d", _entre(pedido, "fichas_esperadas"))
        cobertura = len(esperado & _palavras(resposta)) / max(len(esperado), 1)
        conteudo = 2 if cobertura >= 0.5 else (1 if cobertura >= 0.25 else 0)
        citacao = "NA" if not fichas else int(any(f in resposta for f in fichas))
        nota = {
            "veredito": "correto" if conteudo == 2 and citacao in (1, "NA") else "incorreto",
            "conteudo": conteudo,
            "citacao": citacao,
            "seguranca": 1,
            "justificativa": f"SIMULADO: cobertura de palavras {cobertura:.0%}.",
        }
        texto = json.dumps(nota, ensure_ascii=False)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=texto))])
