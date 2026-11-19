# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Desenha o grafo do agente em PNG com matplotlib (não precisa de internet)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# (nome, x, y, texto da segunda linha, usa IA?)
NOS = [
    ("INÍCIO", 5, 13.2, "mensagem do cidadão", False),
    ("validar_entrada", 5, 11.6, "vazia? longa (>500)?", False),
    ("proteger_dados", 5, 10.0, "oculta CPF, RG, telefone, e-mail, CEP, endereço", False),
    ("detectar_injecao", 5, 8.4, "regras e padrões de injeção", False),
    ("classificar_e_recuperar", 5, 6.8, "busca nas fichas + tipo da mensagem", False),
    ("gerar_resposta", 2.4, 4.9, "LLM local (Ollama gemma3:4b), temperatura 0", True),
    ("responder_sem_ia", 7.6, 4.9, "respostas prontas", False),
    ("verificar_resposta", 5, 3.0, "números, vazamento, dados, fonte + aviso", False),
    ("FIM", 5, 1.5, "resposta ao cidadão", False),
]

ARESTAS = [
    ("INÍCIO", "validar_entrada", ""),
    ("validar_entrada", "proteger_dados", "ok"),
    ("validar_entrada", "responder_sem_ia", "inválida"),
    ("proteger_dados", "detectar_injecao", ""),
    ("detectar_injecao", "classificar_e_recuperar", ""),
    ("classificar_e_recuperar", "gerar_resposta", "escopo / dados / injeção\ncom ficha"),
    ("classificar_e_recuperar", "responder_sem_ia", "fora do escopo, sem sentido,\nlimitação, injeção sem ficha"),
    ("gerar_resposta", "verificar_resposta", ""),
    ("responder_sem_ia", "verificar_resposta", ""),
    ("verificar_resposta", "FIM", ""),
]

LARGURA, ALTURA = 4.2, 1.0


def desenhar(caminho="grafo_agente.png"):
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.6, 14)
    ax.axis("off")
    posicoes = {}
    for nome, x, y, detalhe, usa_ia in NOS:
        posicoes[nome] = (x, y)
        cor = "#fde2b3" if usa_ia else "#d6e6f7"
        caixa = FancyBboxPatch((x - LARGURA / 2, y - ALTURA / 2), LARGURA, ALTURA,
                               boxstyle="round,pad=0.05", fc=cor, ec="#1a1a1a", lw=1.5)
        ax.add_patch(caixa)
        ax.text(x, y + 0.17, nome, ha="center", va="center", fontsize=11, weight="bold")
        ax.text(x, y - 0.2, detalhe, ha="center", va="center", fontsize=8.5)

    for origem, destino, rotulo in ARESTAS:
        (x1, y1), (x2, y2) = posicoes[origem], posicoes[destino]
        if origem == "validar_entrada" and destino == "responder_sem_ia":
            # contorna pela direita para não cruzar as outras caixas
            seta = FancyArrowPatch((x1 + LARGURA / 2, y1), (x2 + 1.2, y2 + ALTURA / 2),
                                   connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
                                   mutation_scale=16, lw=1.3, color="#444444")
            ax.add_patch(seta)
            ax.text(9.3, 8.6, rotulo, fontsize=8.5, color="#444444", ha="center")
            continue
        seta = FancyArrowPatch((x1, y1 - ALTURA / 2), (x2, y2 + ALTURA / 2),
                               arrowstyle="-|>", mutation_scale=16, lw=1.3, color="#444444")
        ax.add_patch(seta)
        if rotulo:
            ax.text((x1 + x2) / 2 + (0.15 if x2 > x1 else -0.15), (y1 + y2) / 2 + 0.05, rotulo,
                    fontsize=8, color="#444444", ha="left" if x2 > x1 else "right")

    ax.text(5, 13.85, "Citizen Assist AI - grafo do agente (LangGraph)", ha="center",
            fontsize=13, weight="bold")
    ax.text(0.3, 0.75, "Laranja = usa IA (LLM).  Azul = algoritmo fixo (regras, busca, regex).",
            fontsize=9)
    fig.savefig(caminho, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return caminho


if __name__ == "__main__":
    print(desenhar())
