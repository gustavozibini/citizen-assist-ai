# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Agente único em LangGraph: etapas fixas (algoritmos) + IA só para redigir.

validar_entrada -> proteger_dados -> detectar_injecao -> classificar_e_recuperar
    -> gerar_resposta (IA)  ou  responder_sem_ia
    -> verificar_resposta -> FIM

Sem memória entre perguntas (nenhum checkpointer): nada fica guardado.
"""

import re
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

import config
import prompts
import seguranca
from fichas import buscar, carregar_fichas, formatar_trechos, vocabulario


class Estado(TypedDict, total=False):
    mensagem: str            # depois de proteger_dados, só a versão mascarada
    tipo: str                # escopo, fora_do_escopo, invalida, dados_pessoais, injecao, limitacao
    motivo_invalida: str     # vazia, longa, sem_sentido
    dados_encontrados: list  # tipos de dado ocultados (ex.: ["CPF"]), nunca o valor
    intencao_dados: bool
    injecao: list            # regras de injeção que dispararam
    fichas: list             # códigos usados, ex.: ["FC-01", "FC-07"]
    trechos: str             # texto das fichas enviado ao modelo
    resposta: str
    usou_ia: bool
    checagens: dict


def criar_agente(llm, versao_recuperacao=None, fichas=None):
    """Monta e compila o grafo. `llm` pode ser o Groq ou o modelo falso."""
    versao = versao_recuperacao or config.VERSAO_RECUPERACAO
    base = fichas or carregar_fichas()
    vocab = vocabulario(base)
    datas = {codigo: ficha.data_verificacao for codigo, ficha in base.items()}

    # ------------------------------------------------------------ nós

    def validar_entrada(estado):
        motivo = seguranca.validar_entrada(estado.get("mensagem"))
        if motivo:
            # Não processa nem guarda o texto rejeitado.
            return {"tipo": "invalida", "motivo_invalida": motivo, "mensagem": ""}
        return {"tipo": ""}

    def proteger_dados(estado):
        intencao = seguranca.tem_intencao_de_dados(estado["mensagem"])
        mascarada, tipos = seguranca.mascarar_dados(estado["mensagem"])
        # A partir daqui o texto original não existe mais no estado.
        return {"mensagem": mascarada, "dados_encontrados": tipos, "intencao_dados": intencao}

    def detectar_injecao(estado):
        return {"injecao": seguranca.detectar_injecao(estado["mensagem"])}

    def classificar_e_recuperar(estado):
        msg = estado["mensagem"]
        tem_dados = bool(estado["dados_encontrados"] or estado["intencao_dados"])
        achado = buscar(msg, base, versao, tem_dado_pessoal=tem_dados)
        saida = {"fichas": achado["fichas"], "trechos": formatar_trechos(achado["trechos"])}

        if estado["injecao"]:
            saida["tipo"] = "injecao"
        elif seguranca.texto_sem_sentido(msg, vocab):
            saida.update(tipo="invalida", motivo_invalida="sem_sentido")
        elif tem_dados:
            saida["tipo"] = "dados_pessoais"
        elif seguranca.pergunta_sobre_limitacao(msg):
            saida["tipo"] = "limitacao"
        elif achado["fichas"]:
            saida["tipo"] = "escopo"
        else:
            saida["tipo"] = "fora_do_escopo"
        return saida

    def gerar_resposta(estado):
        alertas = []
        if estado["tipo"] == "injecao":
            alertas.append(prompts.ALERTA_INJECAO)
        if estado["tipo"] == "dados_pessoais":
            alertas.append(prompts.ALERTA_DADOS)
        pedido = prompts.montar_mensagem(
            seguranca.neutralizar(estado["mensagem"]), estado["trechos"], alertas)
        resposta = llm.invoke([SystemMessage(prompts.PROMPT_SISTEMA), HumanMessage(pedido)])
        return {"resposta": str(resposta.content).strip(), "usou_ia": True}

    def responder_sem_ia(estado):
        tipo = estado["tipo"]
        chave = estado.get("motivo_invalida") if tipo == "invalida" else tipo
        if tipo == "dados_pessoais":   # dado pessoal sem assunto das fichas
            texto = prompts.RESPOSTAS_FIXAS["fora_do_escopo"]
        else:
            texto = prompts.RESPOSTAS_FIXAS[chave]
        return {"resposta": texto, "usou_ia": False, "fichas": []}

    def verificar_resposta(estado):
        resposta, fichas_usadas = estado["resposta"], list(estado.get("fichas") or [])
        checagens = {}

        # 1) Números: todo número da resposta da IA precisa existir nas fichas ou na pergunta.
        if estado.get("usou_ia"):
            faltando = numeros_inventados(resposta, estado["trechos"] + " " + estado["mensagem"])
            checagens["numeros_conferem"] = not faltando
            if faltando:
                resposta = ("Não consegui confirmar a resposta gerada. "
                            "Veja o trecho original da ficha:\n" + estado["trechos"])

        # 2) Vazamento do prompt de sistema.
        if config.MARCADOR_INTERNO in resposta:
            resposta = prompts.RESPOSTAS_FIXAS["injecao"]
            checagens["vazamento_bloqueado"] = True

        # 3) Nenhum dado pessoal sai na resposta.
        resposta, tipos = seguranca.mascarar_dados(resposta)
        checagens["dado_pessoal_na_saida"] = bool(tipos)

        # 4) Prefixos fixos de segurança.
        if estado["tipo"] == "dados_pessoais":
            resposta = prompts.prefixo_dados(estado["dados_encontrados"]) + "\n\n" + resposta
            if "FC-07" not in fichas_usadas:   # o aviso de privacidade vem da FC-07
                fichas_usadas.append("FC-07")
        if estado["tipo"] == "injecao" and estado.get("usou_ia"):
            resposta = prompts.PREFIXO_INJECAO + "\n\n" + resposta

        # 5) Fonte e data (sempre que a resposta usou fichas) e aviso (sempre).
        if fichas_usadas:
            fontes = ", ".join(f"{c} (verificada em {datas.get(c, '?')})" for c in fichas_usadas)
            resposta += f"\n\nFonte: Central do Cidadão de Aurora, ficha {fontes}."
        resposta += "\n\n" + config.AVISO

        checagens["cita_ficha"] = bool(re.search(r"FC-0[1-7]", resposta))
        return {"resposta": resposta, "fichas": fichas_usadas, "checagens": checagens}

    # ------------------------------------------------------------ rotas

    def rota_validacao(estado):
        return "responder_sem_ia" if estado["tipo"] == "invalida" else "proteger_dados"

    def rota_resposta(estado):
        precisa_ia = estado["tipo"] in ("escopo", "dados_pessoais", "injecao") and estado["fichas"]
        return "gerar_resposta" if precisa_ia else "responder_sem_ia"

    # ------------------------------------------------------------ grafo

    grafo = StateGraph(Estado)
    for nome, funcao in [
        ("validar_entrada", validar_entrada), ("proteger_dados", proteger_dados),
        ("detectar_injecao", detectar_injecao), ("classificar_e_recuperar", classificar_e_recuperar),
        ("gerar_resposta", gerar_resposta), ("responder_sem_ia", responder_sem_ia),
        ("verificar_resposta", verificar_resposta),
    ]:
        grafo.add_node(nome, funcao)

    grafo.add_edge(START, "validar_entrada")
    grafo.add_conditional_edges("validar_entrada", rota_validacao,
                                ["proteger_dados", "responder_sem_ia"])
    grafo.add_edge("proteger_dados", "detectar_injecao")
    grafo.add_edge("detectar_injecao", "classificar_e_recuperar")
    grafo.add_conditional_edges("classificar_e_recuperar", rota_resposta,
                                ["gerar_resposta", "responder_sem_ia"])
    grafo.add_edge("gerar_resposta", "verificar_resposta")
    grafo.add_edge("responder_sem_ia", "verificar_resposta")
    grafo.add_edge("verificar_resposta", END)
    return grafo.compile()


# ---------------------------------------------------------------- apoio


def numeros_inventados(resposta, fonte):
    """Números da resposta que não aparecem na fonte (fichas + pergunta)."""
    def numeros(texto):
        texto = re.sub(r"FC-\d\d", " ", texto)                  # códigos de ficha
        return set(re.findall(r"\d+(?:,\d+)?", texto))

    resposta = re.sub(r"(?m)^[\s*\-]*\d+[.)]\s", " ", resposta)  # numeração dos passos da IA
    permitidos = numeros(fonte)
    permitidos |= {n.split(",")[0] for n in permitidos}          # "38,00" aceita "38"
    return numeros(resposta) - permitidos


def perguntar(agente, texto):
    """Roda uma pergunta no grafo e devolve o estado final (já sem dado pessoal)."""
    return agente.invoke({"mensagem": texto})
