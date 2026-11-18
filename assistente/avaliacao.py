# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Roda agente + juiz no golden dataset, calcula métricas e compara antes/depois.

Nenhum dado pessoal é salvo: a tabela guarda a mensagem JÁ MASCARADA.
"""

import os
import time

import pandas as pd

import config
import modelos
import juiz as modulo_juiz
from agente import criar_agente, perguntar
from fichas import carregar_fichas

PASTA_RESULTADOS = os.path.join(os.getcwd(), "resultados")


def ler_golden(caminho="golden_dataset.csv"):
    tabela = pd.read_csv(caminho, dtype=str, keep_default_na=False)
    tabela["fichas_esperadas"] = tabela["fichas_esperadas"].apply(
        lambda t: [f for f in t.split(";") if f])
    return tabela


def texto_das_fichas(codigos, fichas):
    return "\n\n".join(fichas[c].texto_completo() for c in sorted(set(codigos)) if c in fichas)


def avaliar_uma(agente, juiz, linha, fichas):
    """Uma linha do golden: resposta do agente + nota do juiz + checagens."""
    try:
        estado = perguntar(agente, linha["mensagem"])
        resposta, erro = estado["resposta"], ""
    except Exception as e:                      # ex.: limite da API
        estado, resposta, erro = {}, "", f"{type(e).__name__}"
    mensagem_segura = estado.get("mensagem") or "(mensagem rejeitada)"

    usadas = estado.get("fichas") or []
    nota = modulo_juiz.avaliar_com_llm(
        juiz, mensagem_segura, linha["resposta_esperada"], linha["fichas_esperadas"],
        resposta, texto_das_fichas(linha["fichas_esperadas"] + usadas, fichas))
    checks = modulo_juiz.checagens_deterministicas(
        linha["tipo"], linha["resposta_esperada"], linha["fichas_esperadas"], resposta)

    correto_juiz = nota["veredito_regua"] == "correto"
    obrigatorias_ok = all(checks[c] for c in modulo_juiz.CHECAGENS_OBRIGATORIAS)
    return {
        "id": int(linha["id"]),
        "tipo_esperado": linha["tipo"],
        "mensagem_mascarada": mensagem_segura,
        "tipo_detectado": estado.get("tipo", "erro"),
        "fichas_esperadas": ";".join(linha["fichas_esperadas"]),
        "fichas_usadas": ";".join(usadas),
        "usou_ia": estado.get("usou_ia", False),
        "resposta": resposta,
        "erro_execucao": erro,
        "juiz_veredito": nota.get("veredito"),
        "juiz_conteudo": nota.get("conteudo"),
        "juiz_citacao": nota.get("citacao"),
        "juiz_seguranca": nota.get("seguranca"),
        "juiz_justificativa": nota.get("justificativa"),
        "correto_juiz": correto_juiz,
        **checks,
        "correto_juiz_e_checagens": correto_juiz and obrigatorias_ok,
    }


def rodar_golden(llm_agente, llm_juiz, versao, modo, caminho_golden="golden_dataset.csv"):
    """Roda as 26 mensagens. Devolve um DataFrame com uma linha por mensagem."""
    fichas = carregar_fichas()
    agente = criar_agente(llm_agente, versao, fichas)
    golden = ler_golden(caminho_golden)
    linhas = []
    for _, linha in golden.iterrows():
        inicio = time.time()
        resultado = avaliar_uma(agente, llm_juiz, linha, fichas)
        resultado["segundos"] = round(time.time() - inicio, 1)
        linhas.append(resultado)
        print(f"#{resultado['id']:>2} {resultado['tipo_detectado']:<15} "
              f"juiz={resultado['juiz_veredito']}")
    tabela = pd.DataFrame(linhas)
    tabela["versao_recuperacao"] = versao
    tabela["modo"] = modo
    real = modo in ("groq", "ollama")
    tabela["modelo_agente"] = modelos.nome_modelo_agente() if real else "LLMFalso"
    tabela["modelo_juiz"] = modelos.nome_modelo_juiz() if real else "JuizFalso"
    return tabela


# ---------------------------------------------------------------- métricas


def resumo(tabela):
    """Indicadores de uma rodada."""
    total = len(tabela)
    acertos = int(tabela["correto_juiz"].sum())
    acertos_chk = int(tabela["correto_juiz_e_checagens"].sum())
    return {
        "versao": tabela["versao_recuperacao"].iloc[0],
        "modo": tabela["modo"].iloc[0],
        "total": total,
        "acertos_juiz": acertos,
        "acuracia_juiz_%": round(100 * acertos / total, 1),
        "acertos_juiz_e_checagens": acertos_chk,
        "acuracia_juiz_e_checagens_%": round(100 * acertos_chk / total, 1),
        "cita_ficha_%": round(100 * tabela["chk_cita_ficha"].mean(), 1),
        "sem_dado_pessoal_%": round(100 * tabela["chk_sem_dado_pessoal"].mean(), 1),
        "chamadas_ia": int(tabela["usou_ia"].sum()),
        "erros_execucao": int((tabela["erro_execucao"] != "").sum()),
    }


def acerto_por_tipo(tabela):
    return (tabela.groupby("tipo_esperado")["correto_juiz"]
            .agg(["sum", "count"]).rename(columns={"sum": "acertos", "count": "total"}))


def comparar(antes, depois):
    """Tabela lado a lado e lista do que mudou."""
    geral = pd.DataFrame([resumo(antes), resumo(depois)]).set_index("versao")
    mudou = antes[["id", "tipo_esperado", "correto_juiz"]].merge(
        depois[["id", "correto_juiz"]], on="id", suffixes=("_antes", "_depois"))
    mudou = mudou[mudou["correto_juiz_antes"] != mudou["correto_juiz_depois"]]
    return geral, mudou


def tabela_markdown(df):
    """Markdown simples (sem depender do pacote tabulate)."""
    colunas = [str(c) for c in df.columns]
    linhas = ["| " + " | ".join(colunas) + " |", "|" + "---|" * len(colunas)]
    for _, l in df.iterrows():
        linhas.append("| " + " | ".join(str(v).replace("\n", " ") for v in l.values) + " |")
    return "\n".join(linhas)


def salvar(tabela, nome, pasta=None):
    pasta = pasta or PASTA_RESULTADOS
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, nome)
    tabela.to_csv(caminho, index=False, encoding="utf-8")
    return caminho


def salvar_resumo(antes, depois, pasta=None):
    pasta = pasta or PASTA_RESULTADOS
    geral, mudou = comparar(antes, depois)
    salvar(geral.reset_index(), "resumo_comparativo.csv", pasta)
    texto = (
        f"# Resumo antes x depois (modo: {antes['modo'].iloc[0]})\n\n"
        + tabela_markdown(geral.reset_index()) + "\n\n## Mensagens que mudaram\n\n"
        + (tabela_markdown(mudou) if len(mudou) else "Nenhuma.") + "\n"
    )
    with open(os.path.join(pasta, "resumo_comparativo.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    return geral, mudou


def amostra_conferencia_manual(tabela, n=6, semente=42, pasta=None):
    """Sorteia n linhas para o aluno conferir à mão (coluna veredito_manual em branco)."""
    amostra = tabela.sample(n=n, random_state=semente)[
        ["id", "tipo_esperado", "mensagem_mascarada", "resposta", "juiz_veredito"]].copy()
    amostra["veredito_manual"] = ""
    amostra["comentario"] = ""
    caminho = os.path.join(pasta or PASTA_RESULTADOS, "conferencia_manual.csv")
    if not os.path.exists(caminho):          # não apaga o que o aluno já preencheu
        salvar(amostra.sort_values("id"), "conferencia_manual.csv", pasta)
    return pd.read_csv(caminho, dtype=str, keep_default_na=False)


def concordancia_manual(conferencia):
    preenchidas = conferencia[conferencia["veredito_manual"].str.strip() != ""]
    if preenchidas.empty:
        return None
    iguais = (preenchidas["veredito_manual"].str.strip().str.lower()
              == preenchidas["juiz_veredito"].str.lower())
    return round(100 * iguais.mean(), 1), len(preenchidas)


# ---------------------------------------------------------------- testes com usuários


def indicadores_usuarios(caminho="testes_usuarios/registro.csv"):
    """Tempo, acerto e facilidade. Devolve None se o registro estiver vazio."""
    dados = pd.read_csv(caminho, dtype=str, keep_default_na=False)
    preenchidos = dados[dados["tempo_s"].str.strip() != ""].copy()
    if preenchidos.empty:
        return None
    preenchidos["tempo_s"] = preenchidos["tempo_s"].astype(float)
    preenchidos["acertou"] = preenchidos["acertou"].str.strip().str.lower().isin(["sim", "1", "s"])
    tempo = preenchidos.groupby("tarefa")["tempo_s"].agg(["mean", "median", "count"]).round(1)
    acerto = (100 * preenchidos.groupby("tarefa")["acertou"].mean()).round(1)

    notas = dados[["participante", "q1", "q2", "q3", "q4", "q5"]].copy()
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        notas[q] = pd.to_numeric(notas[q], errors="coerce")
    por_pessoa = notas.groupby("participante")[["q1", "q2", "q3", "q4", "q5"]].max().dropna()
    facilidade = round(por_pessoa.mean(axis=1).mean(), 2) if len(por_pessoa) else None
    return {
        "participantes": preenchidos["participante"].nunique(),
        "tempo_por_tarefa_s": tempo,
        "acerto_por_tarefa_%": acerto,
        "acerto_geral_%": round(100 * preenchidos["acertou"].mean(), 1),
        "facilidade_media_1a5": facilidade,
        "facilidade_por_pergunta": por_pessoa.mean().round(2) if len(por_pessoa) else None,
    }
