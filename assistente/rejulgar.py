# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Reavalia as respostas já salvas (antes.csv e depois.csv) com o juiz atual,
sem chamar o agente de novo. Guarda a avaliação anterior em *_juiz_v1.csv.

Uso: python3 rejulgar.py
"""

import os
import shutil
import sys

os.environ.setdefault("CITIZEN_PROVEDOR", "ollama")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd  # noqa: E402

import avaliacao  # noqa: E402
import config  # noqa: E402
import juiz as modulo_juiz  # noqa: E402
import modelos  # noqa: E402
from fichas import carregar_fichas  # noqa: E402
from rodar_local import checar_ollama  # noqa: E402


def rejulgar(nome, llm_juiz, golden, fichas):
    caminho = os.path.join(avaliacao.PASTA_RESULTADOS, nome)
    copia = caminho.replace(".csv", "_juiz_v1.csv")
    if not os.path.exists(copia):
        shutil.copy(caminho, copia)            # guarda a 1ª avaliação para o relatório
    tabela = pd.read_csv(copia, dtype=object, keep_default_na=False)
    for i, linha in tabela.iterrows():
        g = golden[golden["id"].astype(int) == int(linha["id"])].iloc[0]
        usadas = [f for f in linha["fichas_usadas"].split(";") if f]
        nota = modulo_juiz.avaliar_com_llm(
            llm_juiz, linha["mensagem_mascarada"], g["resposta_esperada"], g["fichas_esperadas"],
            linha["resposta"], avaliacao.texto_das_fichas(g["fichas_esperadas"] + usadas, fichas))
        checks = modulo_juiz.checagens_deterministicas(
            g["tipo"], g["resposta_esperada"], g["fichas_esperadas"], linha["resposta"])
        correto = nota["veredito_regua"] == "correto"
        tabela.loc[i, ["juiz_veredito", "juiz_conteudo", "juiz_citacao", "juiz_seguranca",
                       "juiz_justificativa"]] = [nota.get("veredito"), nota.get("conteudo"),
                                                  nota.get("citacao"), nota.get("seguranca"),
                                                  nota.get("justificativa")]
        tabela.loc[i, "correto_juiz"] = correto
        tabela.loc[i, "correto_juiz_e_checagens"] = correto and all(
            checks[c] for c in modulo_juiz.CHECAGENS_OBRIGATORIAS)
        print(f"{nome} #{int(linha['id']):>2} juiz={nota.get('veredito')}")
    tabela["versao_juiz"] = config.VERSAO_JUIZ
    for col in ["correto_juiz", "correto_juiz_e_checagens", "usou_ia"] + \
               [c for c in tabela.columns if c.startswith("chk_")]:
        tabela[col] = tabela[col].astype(str).str.lower() == "true"
    tabela["erro_execucao"] = tabela["erro_execucao"].fillna("")
    avaliacao.salvar(tabela, nome)
    return tabela


if __name__ == "__main__":
    if not checar_ollama():
        sys.exit(1)
    print("Juiz:", config.VERSAO_JUIZ, "| modelo:", modelos.nome_modelo_juiz())
    llm_juiz = modelos.criar_llm_juiz()
    golden, fichas = avaliacao.ler_golden(), carregar_fichas()
    antes = rejulgar("antes.csv", llm_juiz, golden, fichas)
    depois = rejulgar("depois.csv", llm_juiz, golden, fichas)
    geral, mudou = avaliacao.salvar_resumo(antes, depois)
    conf = os.path.join(avaliacao.PASTA_RESULTADOS, "conferencia_manual.csv")
    if os.path.exists(conf):
        os.remove(conf)                          # refaz a amostra com o veredito novo
    avaliacao.amostra_conferencia_manual(depois)
    print("\n=== Resumo (juiz %s) ===" % config.VERSAO_JUIZ)
    print(geral.to_string())
    print("\nMensagens que mudaram de resultado:", len(mudou))
