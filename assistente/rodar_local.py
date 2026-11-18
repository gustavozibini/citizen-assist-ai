# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Execução local com Ollama (sem conta e sem chave).

Uso:
    python3 rodar_local.py checar     # confere se o Ollama e o modelo estão prontos
    python3 rodar_local.py avaliar    # golden dataset: antes (v1) e depois (v2) com o juiz
    python3 rodar_local.py conversar  # menu de texto para usar o assistente
"""

import json
import os
import sys
import time
import urllib.request

os.environ.setdefault("CITIZEN_PROVEDOR", "ollama")
os.chdir(os.path.dirname(os.path.abspath(__file__)))   # roda a partir da pasta assistente/

import config  # noqa: E402


def checar_ollama():
    """Confere se o Ollama está aberto e se os modelos já foram baixados."""
    try:
        with urllib.request.urlopen(config.OLLAMA_URL + "/api/tags", timeout=5) as r:
            instalados = {m["name"] for m in json.load(r).get("models", [])}
    except Exception:
        print("ERRO: o Ollama não está respondendo em", config.OLLAMA_URL)
        print("Abra o aplicativo Ollama (ícone da lhama na barra do Mac) e tente de novo.")
        return False
    faltando = [m for m in {config.MODELO_OLLAMA_AGENTE, config.MODELO_OLLAMA_JUIZ}
                if m not in instalados and m + ":latest" not in instalados]
    if faltando:
        for m in faltando:
            print("ERRO: modelo não baixado. Rode no Terminal:  ollama pull " + m)
        return False
    print("Ollama OK. Modelos: agente =", config.MODELO_OLLAMA_AGENTE, "| juiz =", config.MODELO_OLLAMA_JUIZ)
    return True


def avaliar():
    import avaliacao
    import modelos

    llm_agente = modelos.criar_llm_agente()
    llm_juiz = modelos.criar_llm_juiz()
    inicio = time.time()

    print("\n=== Rodada ANTES (recuperação v1) ===")
    antes = avaliacao.rodar_golden(llm_agente, llm_juiz, "v1", "ollama")
    avaliacao.salvar(antes, "antes.csv")

    print("\n=== Rodada DEPOIS (recuperação v2) ===")
    depois = avaliacao.rodar_golden(llm_agente, llm_juiz, "v2", "ollama")
    avaliacao.salvar(depois, "depois.csv")

    geral, mudou = avaliacao.salvar_resumo(antes, depois)
    avaliacao.amostra_conferencia_manual(depois)
    print("\n=== Resumo ===")
    print(geral.to_string())
    print("\nMensagens que mudaram de resultado:", len(mudou))
    print("Tempo total: %.1f min" % ((time.time() - inicio) / 60))
    print("Arquivos salvos em:", avaliacao.PASTA_RESULTADOS)


def conversar():
    import modelos
    from agente import criar_agente
    from interface import loop_texto

    agente = criar_agente(modelos.criar_llm_agente(), "v2")
    loop_texto(agente)


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "checar"
    if not checar_ollama():
        sys.exit(1)
    if acao == "avaliar":
        avaliar()
    elif acao == "conversar":
        conversar()
    elif acao != "checar":
        print(__doc__)
