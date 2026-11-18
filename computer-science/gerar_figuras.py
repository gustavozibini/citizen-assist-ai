# Gera as figuras do relatório: mapa de Karnaugh e circuitos original e simplificado.
# Gustavo Zibini Belizario - RM 561376
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import schemdraw
import schemdraw.logic as logic
import schemdraw.elements as elm
from decisao_logica import expressao_simplificada

schemdraw.use("matplotlib")
ORDEM = ["00", "01", "11", "10"]   # código de Gray


def mapa_karnaugh():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(-1.2, 4.2)
    ax.set_ylim(-0.6, 5.0)
    ax.axis("off")
    for i, ab in enumerate(ORDEM):          # linhas = AB
        for j, cd in enumerate(ORDEM):      # colunas = CD
            a, b, c, d = map(int, ab + cd)
            m = a * 8 + b * 4 + c * 2 + d
            y = 3 - i
            ax.add_patch(plt.Rectangle((j, y), 1, 1, fill=False, lw=1.2))
            ax.text(j + 0.5, y + 0.5, str(expressao_simplificada(a, b, c, d)),
                    ha="center", va="center", fontsize=18, fontweight="bold")
            ax.text(j + 0.06, y + 0.78, "m%d" % m, fontsize=7, color="gray")
    for j, cd in enumerate(ORDEM):
        ax.text(j + 0.5, 4.2, cd, ha="center", fontsize=12)
    for i, ab in enumerate(ORDEM):
        ax.text(-0.35, 3 - i + 0.5, ab, ha="center", va="center", fontsize=12)
    ax.text(-0.75, 4.55, "AB \\ CD", fontsize=12)
    # Grupo 1: m12 + m13 -> A B C'   (linha AB=11, colunas 00 e 01)
    ax.add_patch(FancyBboxPatch((0.06, 1.06), 1.88, 0.66, boxstyle="round,pad=0.02",
                                fill=False, ec="tab:blue", lw=2.5))
    # Grupo 2: m13 + m15 -> A B D    (linha AB=11, colunas 01 e 11)
    ax.add_patch(FancyBboxPatch((1.14, 1.16), 1.72, 0.46, boxstyle="round,pad=0.02",
                                fill=False, ec="tab:red", lw=2.5, ls="--"))
    ax.text(0.0, -0.25, "Grupo azul: m12 + m13 = A·B·C'", color="tab:blue", fontsize=11)
    ax.text(0.0, -0.6, "Grupo vermelho: m13 + m15 = A·B·D", color="tab:red", fontsize=11)
    fig.savefig("figuras/mapa_karnaugh.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def entrada(d, porta, pino, rotulo):
    """Fio curto com rótulo na entrada de uma porta (ligação por nome do sinal)."""
    L = d.add(elm.Line().at(getattr(porta, pino)).left(1.0))
    d.add(elm.Dot(open=True, radius=0.06).at(L.end).label(rotulo, "left"))


def circuito_original():
    with schemdraw.Drawing(file="figuras/circuito_original.png", show=False, dpi=200) as d:
        d.config(fontsize=13)
        # Inversores compartilhados: geram C' e D'
        n1 = d.add(logic.Not().at((0, 3)).right())
        L = d.add(elm.Line().at(n1.in1).left(1.0)); d.add(elm.Dot(open=True).at(L.end).label("C", "left"))
        L = d.add(elm.Line().at(n1.out).right(1.2)); d.add(elm.Dot(open=True).at(L.end).label("C'", "right", ofst=0.25))
        n2 = d.add(logic.Not().at((0, 1)).right())
        L = d.add(elm.Line().at(n2.in1).left(1.0)); d.add(elm.Dot(open=True).at(L.end).label("D", "left"))
        L = d.add(elm.Line().at(n2.out).right(1.2)); d.add(elm.Dot(open=True).at(L.end).label("D'", "right", ofst=0.25))
        # Três portas AND de 4 entradas (um mintermo cada)
        g1 = d.add(logic.And(inputs=4).at((7, 5)).anchor("in1").right().label("m12", "top"))
        for p, r in zip(["in1", "in2", "in3", "in4"], ["A", "B", "C'", "D'"]):
            entrada(d, g1, p, r)
        g2 = d.add(logic.And(inputs=4).at((7, 1.5)).anchor("in1").right().label("m13", "top"))
        for p, r in zip(["in1", "in2", "in3", "in4"], ["A", "B", "C'", "D"]):
            entrada(d, g2, p, r)
        g3 = d.add(logic.And(inputs=4).at((7, -2)).anchor("in1").right().label("m15", "top"))
        for p, r in zip(["in1", "in2", "in3", "in4"], ["A", "B", "C", "D"]):
            entrada(d, g3, p, r)
        # OR de 3 entradas
        o = d.add(logic.Or(inputs=3).at((12.5, 1.2)).anchor("in2").right())
        d.add(elm.Wire("-|").at(g1.out).to(o.in1))
        d.add(elm.Line().at(g2.out).to(o.in2))
        d.add(elm.Wire("-|").at(g3.out).to(o.in3))
        L = d.add(elm.Line().at(o.out).right(0.8)); d.add(elm.Dot(open=True).at(L.end).label("S", "right"))


def circuito_simplificado():
    with schemdraw.Drawing(file="figuras/circuito_simplificado.png", show=False, dpi=200) as d:
        d.config(fontsize=13)
        n = d.add(logic.Not().at((0, 0)).right())
        L = d.add(elm.Line().at(n.in1).left(1.0)); d.add(elm.Dot(open=True).at(L.end).label("C", "left"))
        o = d.add(logic.Or(inputs=2).at((3.2, 0)).anchor("in1").right())
        d.add(elm.Line().at(n.out).to(o.in1))
        L = d.add(elm.Line().at(o.in2).left(1.0)); d.add(elm.Dot(open=True).at(L.end).label("D", "left"))
        g = d.add(logic.And(inputs=3).at((7.5, 1.0)).anchor("in1").right())
        entrada(d, g, "in1", "A")
        entrada(d, g, "in2", "B")
        d.add(elm.Wire("-|").at(o.out).to(g.in3))
        L = d.add(elm.Line().at(g.out).right(0.8)); d.add(elm.Dot(open=True).at(L.end).label("S", "right"))


if __name__ == "__main__":
    mapa_karnaugh()
    circuito_original()
    circuito_simplificado()
    print("Figuras geradas em figuras/")
