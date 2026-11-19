# -*- coding: utf-8 -*-
"""
Global Solution 2026.2 - CitizenTech - Projeto Citizen Assist AI
Aluno: Gustavo Zibini Belizario - RM 561376

gerar_relatorio.py
Monta o Relatorio_Estatistico.pdf a partir de resultados.json e das figuras
geradas por analise_estatistica.py. Nenhum número é digitado à mão: todos
vêm do arquivo resultados.json.

Uso:  python analise_estatistica.py   (gera resultados.json e figuras/)
      python gerar_relatorio.py       (gera Relatorio_Estatistico.pdf)
Requer: pip install reportlab matplotlib
"""

import json
import os

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table,
                                TableStyle, PageBreak, KeepTogether, CondPageBreak)

with open("resultados.json", encoding="utf-8") as arquivo:
    R = json.load(arquivo)

# Fonte com acentos e símbolos (DejaVu, que acompanha o matplotlib)
pasta_fontes = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(pasta_fontes, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(pasta_fontes, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", os.path.join(pasta_fontes, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                              italic="DejaVu-Italic", boldItalic="DejaVu-Bold")

AZUL = colors.HexColor("#1f5fae")
CINZA_CLARO = colors.HexColor("#f1f0ec")
CINZA = colors.HexColor("#52514e")
LARGURA_UTIL = A4[0] - 4 * cm

normal = ParagraphStyle("normal", fontName="DejaVu", fontSize=9.5, leading=14, alignment=TA_JUSTIFY,
                        spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=15, leading=19, textColor=AZUL,
                    spaceBefore=4, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=11.5, leading=15, textColor=colors.black,
                    spaceBefore=8, spaceAfter=5, keepWithNext=1)
legenda = ParagraphStyle("legenda", fontName="DejaVu-Italic", fontSize=8, leading=11, textColor=CINZA,
                         alignment=TA_CENTER, spaceAfter=8)
celula = ParagraphStyle("celula", fontName="DejaVu", fontSize=8, leading=10.5)
celula_b = ParagraphStyle("celula_b", fontName="DejaVu-Bold", fontSize=8, leading=10.5, textColor=colors.white)
formula = ParagraphStyle("formula", fontName="DejaVu", fontSize=9.5, leading=14, alignment=TA_CENTER,
                         backColor=CINZA_CLARO, borderPadding=6, spaceBefore=4, spaceAfter=10)
item = ParagraphStyle("item", parent=normal, leftIndent=14, bulletIndent=2, spaceAfter=3)


def n(valor, casas=2):
    """Número no padrão brasileiro (vírgula decimal, ponto de milhar)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def pv(p):
    """p-valor formatado."""
    return "< 0,001" if p < 0.001 else n(p, 4)


def P(texto, estilo=normal, marcador=None):
    return Paragraph(texto, estilo, bulletText=marcador)


def tabela(linhas, larguras):
    """Tabela com cabeçalho azul; células viram Paragraph para quebrar linha."""
    dados = [[Paragraph(str(c), celula_b) for c in linhas[0]]]
    for linha in linhas[1:]:
        dados.append([Paragraph(str(c), celula) for c in linha])
    t = Table(dados, colWidths=larguras, repeatRows=1, splitByRow=0)  # não divide entre páginas
    t.keepWithNext = True  # mantém a tabela junto da legenda
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9c8c2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def figura(nome, largura_cm, texto_legenda):
    """Imagem centralizada, mantendo a proporção, com legenda."""
    caminho = os.path.join("figuras", nome)
    w, h = ImageReader(caminho).getSize()
    largura = largura_cm * cm
    img = Image(caminho, width=largura, height=largura * h / w)
    return KeepTogether([img, P(texto_legenda, legenda)])


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.2 * cm,
                      "Citizen Assist AI - Relatório Estatístico - Gustavo Zibini Belizario (RM 561376)")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, "Página %d" % doc.page)
    canvas.restoreState()


q1, q2, q3, q4, q5, q6, q7 = (R[k] for k in ["q01", "q02", "q03", "q04", "q05", "q06", "q07"])
d = q1["descritivas"]
c5, c6 = q5["coeficientes"], q6["coeficientes"]
pct_prior = 100 * q6["n_classe1"] / q1["n_linhas"]
pct_pop_prior = 100 * q7["pop_prioritarios"] / q7["pop_total"]
top = q7["por_uf"][:8]

E = []  # elementos do documento

# ---------------------------------------------------------------- CAPA
E += [Spacer(1, 4.5 * cm),
      P("FIAP - Global Solution 2026.2 - Desafio CitizenTech",
        ParagraphStyle("c0", parent=normal, alignment=TA_CENTER, textColor=CINZA, fontSize=11)),
      Spacer(1, 1.2 * cm),
      P("Relatório Estatístico", ParagraphStyle("c1", fontName="DejaVu-Bold", fontSize=28, leading=34,
                                                alignment=TA_CENTER, textColor=AZUL)),
      Spacer(1, 0.5 * cm),
      P("Onde o cidadão mais precisa de orientação clara:<br/>análise dos indicadores municipais "
        "para o projeto Citizen Assist AI",
        ParagraphStyle("c2", fontName="DejaVu", fontSize=13, leading=19, alignment=TA_CENTER)),
      Spacer(1, 3 * cm),
      P("Gustavo Zibini Belizario — RM 561376",
        ParagraphStyle("c3", fontName="DejaVu-Bold", fontSize=13, leading=18, alignment=TA_CENTER)),
      P("Ciência da Computação - 1º ano - trabalho individual",
        ParagraphStyle("c4", parent=normal, alignment=TA_CENTER, fontSize=10.5)),
      P("Disciplina: Estatística com Python (questões 02 a 07)",
        ParagraphStyle("c5", parent=normal, alignment=TA_CENTER, fontSize=10.5)),
      Spacer(1, 4 * cm),
      P("Novembro de 2026", ParagraphStyle("c6", parent=normal, alignment=TA_CENTER, fontSize=11)),
      PageBreak()]

# ---------------------------------------------------------------- RESUMO
E += [P("1. Resumo executivo", h1),
      P("O <b>Citizen Assist AI</b> é um assistente digital que orienta cidadãos sobre serviços, documentos e "
        "direitos. Este relatório usa dados públicos reais dos <b>%s municípios brasileiros</b> (Atlas do "
        "Desenvolvimento Humano no Brasil, Censo 2010) para responder a uma pergunta de negócio: <b>em quais "
        "municípios a população mais depende de orientação clara e acessível, e que características o "
        "assistente precisa ter para funcionar nesses lugares?</b>" % n(q1["n_linhas"], 0)),
      P("Principais achados:", normal),
      P("<b>Analfabetismo é uma barreira concreta.</b> A taxa média municipal de analfabetismo adulto é de "
        "%s%% (mediana de %s%%). Pelo modelo normal, a probabilidade de um município estar acima da mediana "
        "é de %s%% (questão 02)." % (n(q2["media"]), n(q2["mediana"]), n(100 * q2["b_prob"])), item, "•"),
      P("<b>Pobreza e analfabetismo andam juntos.</b> A correlação de Pearson entre as duas taxas é de %s "
        "(%s). Cada ponto percentual a mais de analfabetismo está associado a %s ponto percentual a mais de "
        "pobres; o modelo simples explica %s%% da variação da pobreza (questão 04)."
        % (n(q4["pearson"], 3), q4["forca"], n(q4["b1"]), n(100 * q4["r2"], 1)), item, "•"),
      P("<b>Falta de serviços básicos reforça o quadro.</b> Somando ao modelo o acesso a banheiro com água "
        "encanada e a energia elétrica, a explicação sobe para %s%% (questão 05)."
        % n(100 * q5["r2"], 1), item, "•"),
      P("<b>É possível apontar os municípios prioritários.</b> Uma regressão logística com três indicadores "
        "simples identifica os municípios de IDHM Baixo ou Muito Baixo com acurácia de %s%% em dados que o "
        "modelo não viu, contra %s%% de referência (questão 06)."
        % (n(100 * q6["acuracia"]), n(100 * q6["acuracia_base"])), item, "•"),
      P("<b>Tamanho do público.</b> %s municípios (%s%%) estão nas faixas Baixo ou Muito Baixo do IDHM e somam "
        "%s milhões de habitantes (%s%% da população analisada), concentrados em %s, %s e %s."
        % (n(q6["n_classe1"], 0), n(pct_prior, 1), n(q7["pop_prioritarios"] / 1e6, 1), n(pct_pop_prior, 1),
           top[0]["ufn"], top[1]["ufn"], top[2]["ufn"]), item, "•"),
      P("<b>Recomendação central:</b> o assistente deve ser projetado primeiro para o usuário de baixa "
        "escolaridade (linguagem simples, opções numeradas, leitura em voz alta), ser leve o bastante para "
        "funcionar com infraestrutura precária e priorizar conteúdo de documentos básicos e programas sociais. "
        "Os detalhes estão na seção 9.", normal),
      P("<b>Aviso de leitura:</b> as relações apresentadas são associações estatísticas entre municípios, não "
        "provas de causa e efeito. As limitações estão descritas na seção 9.3.", normal),
      PageBreak()]

# ---------------------------------------------------------------- BASE
E += [P("2. Base de dados (questão 01)", h1),
      P("2.1 Fonte", h2),
      P("<b>Atlas do Desenvolvimento Humano no Brasil 2013</b>, elaborado pelo Programa das Nações Unidas para "
        "o Desenvolvimento (PNUD), pelo Instituto de Pesquisa Econômica Aplicada (Ipea) e pela Fundação João "
        "Pinheiro (FJP), com base nos Censos Demográficos do IBGE de 1991, 2000 e 2010. O arquivo usado é a "
        "tabela municipal <i>pnud_muni</i>, redistribuída no pacote de dados abertos <b>abjData</b>: "
        "https://github.com/abjur/abjData (arquivo data/pnud_muni.rda). Data de acesso: <b>16/11/2026</b>."),
      P("O arquivo original tem 16.695 linhas (5.565 municípios × 3 censos) e 125 colunas. O script "
        "<i>preparar_base.py</i> apenas <b>filtra o ano de 2010</b> e <b>seleciona %d colunas</b>, gerando "
        "<i>base_dados.csv</i> com <b>%s linhas</b>. Nenhum valor foi alterado, preenchido ou criado. Foram "
        "encontrados <b>%d valores ausentes</b>, portanto nenhuma linha precisou ser removida."
        % (q1["n_colunas"], n(q1["n_linhas"], 0), q1["ausentes"])),
      P("2.2 Por que esta base", h2),
      P("O Citizen Assist AI existe para facilitar o acesso a informações sobre serviços e documentos. Para "
        "decidir <b>para quem</b> e <b>como</b> construir a solução, é preciso saber onde estão as pessoas com "
        "mais dificuldade de acessar e entender informação pública. Os indicadores municipais de escolaridade "
        "(analfabetismo, anos de estudo), renda e pobreza e de acesso a serviços básicos (água, banheiro, "
        "coleta de lixo e energia elétrica) medem exatamente isso: mostram onde a população mais depende de "
        "orientação clara e acessível e onde a solução teria mais impacto. A base é oficial, pública, cobre "
        "todos os municípios do país e usa definições padronizadas, o que permite comparações."),
      P("2.3 Dicionário das variáveis", h2)]

dicionario = [
    ["Coluna", "Descrição (dicionário do Atlas)", "Unidade"],
    ["codmun7", "Código do município no IBGE, com 7 dígitos", "código"],
    ["municipio", "Nome do município", "texto"],
    ["ufn", "Nome da unidade da federação", "texto"],
    ["pop", "População residente em domicílios particulares permanentes", "habitantes"],
    ["espvida", "Esperança de vida ao nascer", "anos"],
    ["e_anosestudo", "Expectativa de anos de estudo aos 18 anos de idade", "anos"],
    ["t_analf18m", "Taxa de analfabetismo da população de 18 anos ou mais (não sabe ler nem escrever um "
                   "bilhete simples)", "%"],
    ["rdpc", "Renda per capita média", "R$ de ago/2010"],
    ["gini", "Índice de Gini da renda domiciliar per capita (0 = igualdade; 1 = desigualdade máxima)", "0 a 1"],
    ["pmpob", "Proporção de pobres: pessoas com renda domiciliar per capita igual ou inferior a R$ 140,00 "
              "mensais", "%"],
    ["t_agua", "Percentual da população em domicílios com água encanada", "%"],
    ["t_banagua", "Percentual da população em domicílios com banheiro exclusivo e água encanada", "%"],
    ["t_lixo", "Percentual da população em domicílios urbanos com coleta de lixo", "%"],
    ["t_luz", "Percentual da população em domicílios com energia elétrica", "%"],
    ["t_des", "Taxa de desocupação da população de 10 anos ou mais", "%"],
    ["idhm", "Índice de Desenvolvimento Humano Municipal (média geométrica das dimensões Renda, Educação e "
             "Longevidade)", "0 a 1"],
]
E += [tabela(dicionario, [2.6 * cm, 11.4 * cm, 3 * cm]),
      P("Tabela 1 - Variáveis de base_dados.csv. Descrições conforme o glossário do Atlas (tabela pnud_siglas "
        "do pacote abjData).", legenda),
      P("2.4 Estatísticas descritivas", h2)]

linhas = [["Variável", "Média", "Desvio padrão", "Mínimo", "Mediana", "Máximo", "Assimetria"]]
for v in ["e_anosestudo", "t_analf18m", "rdpc", "pmpob", "t_agua", "t_banagua", "t_lixo", "t_luz", "t_des",
          "idhm"]:
    casas = 3 if v == "idhm" else 2
    linhas.append([v, n(d[v]["media"], casas), n(d[v]["desvio"], casas), n(d[v]["minimo"], casas),
                   n(d[v]["mediana"], casas), n(d[v]["maximo"], casas), n(d[v]["assimetria"], 2)])
E += [tabela(linhas, [2.9 * cm] + [2.35 * cm] * 6),
      P("Tabela 2 - Estatísticas descritivas das principais variáveis (%s municípios)."
        % n(q1["n_linhas"], 0), legenda),
      P("A assimetria mostra que várias variáveis <b>não</b> são simétricas como a curva normal: a energia "
        "elétrica (assimetria de %s) está concentrada perto de 100%%, com poucos municípios muito abaixo, e o "
        "analfabetismo (%s) tem cauda para a direita. A suposição de normalidade das questões 02 e 03 é "
        "imposta pelo enunciado e deve ser lida como uma aproximação."
        % (n(d["t_luz"]["assimetria"]), n(d["t_analf18m"]["assimetria"]))),
      PageBreak()]

# ---------------------------------------------------------------- Q02
E += [P("3. Questão 02 - Probabilidade com a distribuição normal", h1),
      P("<b>Variável escolhida:</b> taxa de analfabetismo da população de 18 anos ou mais (t_analf18m). "
        "<b>Justificativa:</b> é a barreira mais direta ao uso de um assistente baseado em texto. "
        "Seguindo o enunciado, assume-se X ~ Normal(μ, σ), com μ = média e σ = desvio padrão populacional "
        "(divisor N) dos %s municípios." % n(q1["n_linhas"], 0)),
      tabela([["Medida", "Valor"],
              ["Média (μ)", n(q2["media"], 4) + " %"],
              ["Mediana", n(q2["mediana"], 4) + " %"],
              ["Desvio padrão populacional (σ)", n(q2["desvio_pop"], 4) + " p.p."]],
             [8 * cm, 5 * cm]),
      P("Tabela 3 - Parâmetros usados na questão 02.", legenda),
      P("<b>Escala de classificação adotada:</b> P = 0: evento impossível; 0 &lt; P &lt; 0,5: evento pouco "
        "provável; P = 0,5: evento equiprovável (tão provável quanto não ocorrer); 0,5 &lt; P &lt; 1: evento "
        "provável; P = 1: evento certo."),
      P("02A) Probabilidade de X ser menor do que a média", h2),
      P("P(X &lt; μ) = P(X &lt; %s) = P(Z &lt; 0) = <b>%s</b> (%s%%)"
        % (n(q2["media"], 4), n(q2["a_prob"], 4), n(100 * q2["a_prob"])), formula),
      P("<b>Classificação: %s.</b> Na distribuição normal a média divide a curva em duas metades iguais, por "
        "isso o resultado é exatamente 50%%: sorteando um município ao acaso, a chance de ele ter analfabetismo "
        "abaixo da média é a mesma de ter acima." % q2["a_classificacao"]),
      P("02B) Probabilidade de X ser maior do que a mediana", h2),
      P("z = (%s − %s) / %s = %s &nbsp;&nbsp;→&nbsp;&nbsp; P(X &gt; %s) = 1 − Φ(%s) = <b>%s</b> (%s%%)"
        % (n(q2["mediana"], 4), n(q2["media"], 4), n(q2["desvio_pop"], 4), n(q2["b_z"], 4),
           n(q2["mediana"], 4), n(q2["b_z"], 4), n(q2["b_prob"], 4), n(100 * q2["b_prob"])), formula),
      P("<b>Classificação: %s.</b> Como a mediana (%s%%) é menor do que a média (%s%%), a área da curva normal "
        "à direita da mediana é maior do que a metade."
        % (q2["b_classificacao"], n(q2["mediana"]), n(q2["media"]))),
      figura("q02_distribuicao_normal.png", 16.5,
             "Figura 1 - Histograma dos dados, curva normal ajustada e áreas correspondentes às alíneas 02A e 02B."),
      P("<b>Leitura crítica.</b> Nos dados reais, %s%% dos municípios ficam abaixo da média e %s%% acima da "
        "mediana. A diferença em relação ao modelo normal (50%% e %s%%) aparece porque a variável é assimétrica "
        "(assimetria de %s): muitos municípios com taxa baixa e uma cauda de municípios com taxa alta. "
        "<b>Para o projeto:</b> a média é puxada para cima por um grupo grande de municípios com analfabetismo "
        "elevado, justamente onde um assistente só de texto falharia."
        % (n(100 * q2["obs_menor_media"]), n(100 * q2["obs_maior_mediana"]), n(100 * q2["b_prob"]),
           n(q2["assimetria"]))),
      PageBreak()]

# ---------------------------------------------------------------- Q03
a, b = q3["a"], q3["b"]
E += [P("4. Questão 03 - Teste de hipótese para a média", h1),
      P("<b>Variável escolhida:</b> expectativa de anos de estudo (e_anosestudo). <b>Justificativa:</b> mede a "
        "escolaridade esperada e é uma das variáveis mais simétricas da base (assimetria de %s), o que torna a "
        "suposição de normalidade mais razoável para amostras pequenas." % n(q3["assimetria"])),
      P("<b>Método:</b> teste z para a média, pois o desvio padrão populacional é conhecido (calculado sobre "
        "todos os municípios). Média populacional de referência μ₀ = <b>%s anos</b>; desvio padrão "
        "populacional σ = <b>%s anos</b>. As amostras são aleatórias simples, sorteadas da própria base com "
        "semente fixa (561376 em 03A e 561377 em 03B) para que o resultado seja reproduzível. A amostra não foi "
        "escolhida para produzir um resultado específico." % (n(q3["mu0"], 4), n(q3["sigma"], 4))),
      P("Estatística de teste: z = (x̄ − μ₀) / (σ / √n)", formula)]


def bloco_teste(t, letra, sinal, lado_txt):
    regra = "z < z crítico" if t["lado"] == "esquerda" else "z > z crítico"
    return [
        P("03%s) Teste unilateral à %s - significância de %s%% - amostra de tamanho %d"
          % (letra, lado_txt, n(100 * t["alfa"], 0), t["n"]), h2),
        tabela([["Item", "Resultado"],
                ["Hipótese nula (H₀)", "μ = %s (a média do grupo é igual à de referência)" % n(q3["mu0"], 4)],
                ["Hipótese alternativa (H₁)", "μ %s %s (a média do grupo é %s do que a de referência)"
                 % (sinal, n(q3["mu0"], 4), "menor" if sinal == "<" else "maior")],
                ["Média amostral (x̄)", n(t["media_amostral"], 4) + " anos"],
                ["Erro padrão (σ / √n)", "%s / √%d = %s" % (n(q3["sigma"], 4), t["n"], n(t["erro_padrao"], 4))],
                ["Estatística z calculada", n(t["z"], 4)],
                ["Valor crítico (α = %s%%)" % n(100 * t["alfa"], 0),
                 "%s (rejeita-se H₀ se %s)" % (n(t["z_critico"], 4), regra)],
                ["p-valor", pv(t["p_valor"])],
                ["Decisão", "<b>%s</b>" % t["decisao"].replace("H0", "H₀")]],
               [5.2 * cm, 11.8 * cm]),
        P("Tabela %d - Teste de hipótese da alínea 03%s." % (4 if letra == "A" else 5, letra), legenda),
        P("<b>Conclusão:</b> %s O p-valor (%s) é %s do que o nível de significância (%s)."
          % (t["conclusao"][0].upper() + t["conclusao"][1:], pv(t["p_valor"]),
             "menor" if t["p_valor"] < t["alfa"] else "maior", n(t["alfa"], 2))),
    ]


E += bloco_teste(a, "A", "<", "esquerda")
E += bloco_teste(b, "B", ">", "direita")
E += [figura("q03_teste_hipotese.png", 16.5,
             "Figura 2 - Curva normal padrão com a região crítica (laranja) e a estatística z calculada (azul)."),
      P("<b>Interpretação para o cliente.</b> %s O valor prático do procedimento está em reutilizá-lo: quando "
        "o Citizen Assist AI for testado em um grupo de municípios (por exemplo, um piloto), o mesmo teste "
        "indica se a escolaridade daquele grupo é realmente diferente da média nacional ou se a diferença "
        "observada cabe na variação normal de uma amostra pequena."
        % ("Nas duas alíneas a diferença entre a média da amostra e a média de referência é pequena demais "
           "para ser distinguida do acaso, o que é o esperado quando a amostra é sorteada da própria população."
           if not a["rejeita_h0"] and not b["rejeita_h0"] else
           "Pelo menos um dos testes rejeitou H₀; como as amostras vêm da própria população, um resultado assim "
           "pode ocorrer por acaso com probabilidade igual ao nível de significância.")),
      PageBreak()]

# ---------------------------------------------------------------- Q04
E += [P("5. Questão 04 - Análise bivariada", h1),
      P("<b>Variáveis:</b> X = taxa de analfabetismo de 18 anos ou mais (t_analf18m, %) e Y = proporção de "
        "pobres (pmpob, %). <b>Justificativa:</b> a pobreza indica onde a população mais depende de serviços "
        "públicos e de documentos para acessá-los; o analfabetismo indica a dificuldade de entender a "
        "orientação escrita. As duas são medidas de forma independente no Censo (uma não entra no cálculo da "
        "outra), então a relação não é automática."),
      P("04A) Gráfico de dispersão", h2),
      figura("q04a_dispersao.png", 11.5,
             "Figura 3 - Dispersão entre analfabetismo e pobreza (cada ponto é um município)."),
      P("<b>Interpretação:</b> a nuvem de pontos sobe da esquerda para a direita: municípios com mais "
        "analfabetismo tendem a ter mais pobres. A relação é aproximadamente linear, mas a dispersão aumenta "
        "para taxas mais altas, isto é, entre os municípios com muito analfabetismo há mais variação na "
        "pobreza. Também se notam dois agrupamentos (um de taxas baixas e outro de taxas altas), reflexo das "
        "diferenças regionais do país."),
      P("04B) Covariância e correlação linear de Pearson", h2),
      tabela([["Medida", "Valor", "Leitura"],
              ["Covariância", n(q4["covariancia"], 4),
               "Positiva: as duas variáveis variam no mesmo sentido. O valor depende das unidades (p.p.²) e "
               "não mede força."],
              ["Correlação de Pearson (r)", n(q4["pearson"], 4),
               "Correlação %s (escala de −1 a 1). p-valor %s." % (q4["forca"], pv(q4["pearson_p"]))]],
             [4.3 * cm, 2.7 * cm, 10 * cm]),
      P("Tabela 6 - Covariância e correlação entre analfabetismo e pobreza.", legenda),
      P("<b>Interpretação:</b> a covariância positiva confirma o sentido visto no gráfico. A correlação de "
        "%s indica associação linear %s: é estatisticamente significativa (p-valor %s), ou seja, muito "
        "improvável de ter surgido por acaso. Correlação não é causalidade: analfabetismo e pobreza "
        "provavelmente se reforçam mutuamente e ambos dependem de fatores históricos e regionais não medidos "
        "aqui." % (n(q4["pearson"], 3), q4["forca"], pv(q4["pearson_p"]))),
      CondPageBreak(10 * cm),  # evita título sozinho no fim da página
      P("04C) Gráfico de correlação linear de Pearson", h2),
      figura("q04c_correlacao.png", 7.5,
             "Figura 4 - Mapa de calor da matriz de correlação de Pearson entre as duas variáveis."),
      P("<b>Interpretação:</b> a diagonal vale 1 (cada variável com ela mesma). A célula fora da diagonal, em "
        "vermelho escuro, mostra a correlação de %s: quanto mais escuro o vermelho, mais forte a associação "
        "positiva." % n(q4["pearson"], 3)),
      P("04D) Reta e equação da regressão linear simples", h2),
      P("pmpob = %s + %s × t_analf18m" % (n(q4["b0"], 4), n(q4["b1"], 4)), formula),
      figura("q04d_regressao.png", 11.5,
             "Figura 5 - Gráfico de dispersão com a reta de regressão linear simples."),
      P("<b>Interpretação:</b> a inclinação indica que cada 1 ponto percentual a mais de analfabetismo está "
        "associado, em média, a %s ponto percentual a mais de pobres. O intercepto (%s) é apenas o ponto onde "
        "a reta cruza o eixo; não tem leitura prática, pois nenhum município tem analfabetismo zero (o mínimo "
        "observado é %s%%)." % (n(q4["b1"]), n(q4["b0"]), n(q4["x_min"]))),
      P("04E) Adequação do modelo: R² e teste F", h2),
      tabela([["Medida", "Valor"],
              ["Coeficiente de determinação (R²)", n(q4["r2"], 4)],
              ["Estatística F (%d e %s graus de liberdade)" % (q4["gl_modelo"], n(q4["gl_residuo"], 0)),
               n(q4["f"], 2)],
              ["p-valor do teste F", pv(q4["f_p"])],
              ["Erro padrão dos resíduos", n(q4["erro_padrao_residuos"], 2) + " p.p."]],
             [9 * cm, 4 * cm]),
      P("Tabela 7 - Medidas de adequação da regressão linear simples.", legenda),
      P("<b>Interpretação:</b> o R² mostra que o analfabetismo, sozinho, explica %s%% da variação da proporção "
        "de pobres entre os municípios; os outros %s%% dependem de fatores fora do modelo. O teste F compara o "
        "modelo com um modelo sem variável explicativa (H₀: inclinação = 0); como o p-valor é %s, rejeita-se "
        "H₀ e o modelo é estatisticamente significativo. O erro padrão dos resíduos diz que as previsões erram, "
        "tipicamente, cerca de %s pontos percentuais."
        % (n(100 * q4["r2"], 1), n(100 * (1 - q4["r2"]), 1), pv(q4["f_p"]),
           n(q4["erro_padrao_residuos"], 1))),
      P("04F) Previsão", h2),
      P("<b>Entrada declarada:</b> município com taxa de analfabetismo de %s%% (valor dentro do intervalo "
        "observado, de %s%% a %s%%)." % (n(q4["prev_x"], 1), n(q4["x_min"]), n(q4["x_max"]))),
      P("pmpob = %s + %s × %s = <b>%s%%</b>"
        % (n(q4["b0"], 4), n(q4["b1"], 4), n(q4["prev_x"], 1), n(q4["prev_y"])), formula),
      P("<b>Interpretação:</b> para um município com %s%% de adultos analfabetos, o modelo prevê que cerca de "
        "%s%% da população seja pobre, isto é, aproximadamente uma em cada %s pessoas é público provável de "
        "programas sociais e precisa de orientação sobre documentos e cadastros."
        % (n(q4["prev_x"], 0), n(q4["prev_y"], 0), n(100 / q4["prev_y"], 0))),
      PageBreak()]

# ---------------------------------------------------------------- Q05
rot5 = {"pmpob": "pmpob", "t_analf18m": "t_analf18m", "t_banagua": "t_banagua", "t_luz": "t_luz"}
ordem5 = [q5["y"]] + q5["x"]


def matriz_para_tabela(m, casas):
    linhas = [[""] + ordem5]
    for i in ordem5:
        linhas.append([i] + [n(m[j][i], casas) for j in ordem5])
    return tabela(linhas, [3.4 * cm] + [3.2 * cm] * 4)


mc = q5["matriz_corr"]
E += [P("6. Questão 05 - Análise multivariada (regressão linear múltipla)", h1),
      P("<b>Variáveis (4 quantitativas):</b> Y = proporção de pobres (pmpob); X₁ = taxa de analfabetismo "
        "(t_analf18m); X₂ = população em domicílios com banheiro e água encanada (t_banagua); X₃ = população em "
        "domicílios com energia elétrica (t_luz). <b>Justificativa:</b> acrescentam-se ao modelo anterior dois "
        "indicadores de acesso a serviços básicos, que são o tipo de serviço sobre o qual o assistente orienta; "
        "a renda per capita foi deixada de fora de propósito, porque a pobreza é definida a partir da renda e a "
        "relação seria quase automática."),
      P("05A) Gráficos de dispersão", h2),
      figura("q05a_dispersao.png", 13.5,
             "Figura 6 - Matriz de gráficos de dispersão; na diagonal, o histograma de cada variável."),
      P("<b>Principais resultados:</b> (1) pobreza e analfabetismo crescem juntos; (2) pobreza cai de forma "
        "bem marcada conforme aumenta o acesso a banheiro e água encanada; (3) a energia elétrica está perto "
        "de 100% na grande maioria dos municípios, e os casos de cobertura baixa aparecem quase só entre os "
        "municípios mais pobres; (4) as explicativas também se relacionam entre si (municípios com mais "
        "analfabetismo têm menos saneamento)."),
      P("05B) Matriz de covariância e matriz de correlação de Pearson", h2),
      matriz_para_tabela(q5["matriz_cov"], 3),
      P("Tabela 8 - Matriz de covariância (diagonal = variância de cada variável).", legenda),
      matriz_para_tabela(mc, 3),
      P("Tabela 9 - Matriz de correlação linear de Pearson.", legenda),
      P("<b>Principais resultados:</b> os sinais das covariâncias mostram o sentido das relações: positiva "
        "entre pobreza e analfabetismo e negativa entre pobreza e os dois indicadores de serviços. Pela "
        "correlação, que permite comparar forças, a pobreza se associa mais com banheiro e água encanada "
        "(%s) e com analfabetismo (%s), e de forma moderada com energia elétrica (%s). As explicativas "
        "t_analf18m e t_banagua têm correlação de %s entre si, o que indica sobreposição de informação "
        "(multicolinearidade moderada) e pede cuidado ao ler cada coeficiente isoladamente."
        % (n(mc["t_banagua"]["pmpob"], 3), n(mc["t_analf18m"]["pmpob"], 3), n(mc["t_luz"]["pmpob"], 3),
           n(mc["t_banagua"]["t_analf18m"], 3))),
      P("05C) Gráfico de correlação linear de Pearson", h2),
      figura("q05c_correlacao.png", 9.5, "Figura 7 - Mapa de calor da matriz de correlação de Pearson."),
      P("<b>Principais resultados:</b> vermelho indica correlação positiva e azul, negativa; quanto mais "
        "escuro, mais forte. A primeira linha resume o que interessa: a pobreza tem vermelho forte com "
        "analfabetismo e azul forte com banheiro e água. A energia elétrica aparece em tons mais claros "
        "porque quase não varia entre os municípios."),
      P("05D) Equação da regressão linear múltipla", h2),
      P("pmpob = %s %s %s × t_analf18m %s %s × t_banagua %s %s × t_luz"
        % (n(c5["const"], 4),
           "+" if c5["t_analf18m"] >= 0 else "−", n(abs(c5["t_analf18m"]), 4),
           "+" if c5["t_banagua"] >= 0 else "−", n(abs(c5["t_banagua"]), 4),
           "+" if c5["t_luz"] >= 0 else "−", n(abs(c5["t_luz"]), 4)), formula),
      tabela([["Termo", "Coeficiente", "Erro padrão", "p-valor"]] +
             [[k if k != "const" else "Intercepto", n(c5[k], 4), n(q5["erros_padrao"][k], 4),
               pv(q5["p_valores"][k])] for k in ["const"] + q5["x"]],
             [5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]),
      P("Tabela 10 - Coeficientes da regressão linear múltipla.", legenda),
      P("<b>Interpretação:</b> mantendo as outras variáveis constantes, cada ponto percentual a mais de "
        "analfabetismo está associado a %s p.p. a mais de pobres; cada ponto a mais de população com banheiro e "
        "água, a %s p.p. a menos; e cada ponto a mais de população com energia elétrica, a %s p.p. a menos. O "
        "efeito do analfabetismo é menor do que no modelo simples (%s) porque parte daquela associação era, "
        "na verdade, compartilhada com a falta de saneamento."
        % (n(c5["t_analf18m"]), n(abs(c5["t_banagua"])), n(abs(c5["t_luz"])), n(q4["b1"]))),
      P("05E) Adequação do modelo: R² e teste F", h2),
      tabela([["Medida", "Valor"],
              ["Coeficiente de determinação (R²)", n(q5["r2"], 4)],
              ["R² ajustado", n(q5["r2_ajustado"], 4)],
              ["Estatística F (%d e %s graus de liberdade)" % (q5["gl_modelo"], n(q5["gl_residuo"], 0)),
               n(q5["f"], 2)],
              ["p-valor do teste F", pv(q5["f_p"])],
              ["Erro padrão dos resíduos", n(q5["erro_padrao_residuos"], 2) + " p.p."]],
             [9 * cm, 4 * cm]),
      P("Tabela 11 - Medidas de adequação da regressão linear múltipla.", legenda),
      figura("q05e_observado_previsto.png", 9.5,
             "Figura 8 - Valores observados contra valores previstos pelo modelo múltiplo."),
      P("<b>Interpretação:</b> as três variáveis juntas explicam %s%% da variação da pobreza entre os "
        "municípios, contra %s%% do modelo simples; o R² ajustado praticamente igual mostra que o ganho não vem "
        "apenas de ter mais variáveis. O teste F (H₀: todos os coeficientes são zero) tem p-valor %s, logo o "
        "modelo é significativo no conjunto, e cada coeficiente também é significativo individualmente. O erro "
        "típico de previsão cai para %s p.p. Na Figura 8 os pontos acompanham a diagonal, mas se abrem para "
        "valores altos: o modelo é menos preciso justamente nos municípios mais pobres."
        % (n(100 * q5["r2"], 1), n(100 * q4["r2"], 1), pv(q5["f_p"]), n(q5["erro_padrao_residuos"], 1))),
      P("05F) Previsão com três variáveis explicativas", h2),
      P("<b>Entradas declaradas:</b> analfabetismo = %s%%; banheiro e água encanada = %s%%; energia elétrica = "
        "%s%% (todas dentro dos intervalos observados na base)."
        % (n(q5["prev_entrada"]["t_analf18m"], 0), n(q5["prev_entrada"]["t_banagua"], 0),
           n(q5["prev_entrada"]["t_luz"], 0))),
      P("pmpob = %s %s %s × %s %s %s × %s %s %s × %s = <b>%s%%</b>"
        % (n(c5["const"], 4),
           "+" if c5["t_analf18m"] >= 0 else "−", n(abs(c5["t_analf18m"]), 4),
           n(q5["prev_entrada"]["t_analf18m"], 0),
           "+" if c5["t_banagua"] >= 0 else "−", n(abs(c5["t_banagua"]), 4),
           n(q5["prev_entrada"]["t_banagua"], 0),
           "+" if c5["t_luz"] >= 0 else "−", n(abs(c5["t_luz"]), 4), n(q5["prev_entrada"]["t_luz"], 0),
           n(q5["prev_y"])), formula),
      P("<b>Interpretação:</b> para um município com esse perfil, o modelo prevê cerca de %s%% de pobres. Com o "
        "mesmo analfabetismo de %s%%, o modelo simples previa %s%%: a informação de que o saneamento e a "
        "energia estão abaixo da média do país eleva a estimativa."
        % (n(q5["prev_y"], 1), n(q5["prev_entrada"]["t_analf18m"], 0), n(q4["prev_y"], 1))),
      PageBreak()]

# ---------------------------------------------------------------- Q06
total_teste = q6["vn"] + q6["fp"] + q6["fn"] + q6["vp"]
E += [P("7. Questão 06 - Regressão logística binária", h1),
      P("<b>Pergunta de negócio:</b> dá para apontar, a partir de poucos indicadores simples, os municípios "
        "onde o Citizen Assist AI deveria chegar primeiro?"),
      P("<b>Variável-alvo (binária):</b> <i>prioritario</i> = 1 se o IDHM do município é menor do que %s, isto "
        "é, se está nas faixas oficiais <b>Baixo</b> (0,500 a 0,599) ou <b>Muito Baixo</b> (0 a 0,499) do "
        "Atlas; 0 caso contrário (faixas Médio, Alto e Muito Alto). São %s municípios prioritários (%s%%) e "
        "%s não prioritários."
        % (n(q6["limiar_idhm"], 3), n(q6["n_classe1"], 0), n(pct_prior, 1), n(q6["n_classe0"], 0))),
      P("<b>Variáveis explicativas (3 quantitativas):</b> t_analf18m, t_banagua e t_luz. <b>Justificativa:</b> "
        "nenhuma delas entra na fórmula do IDHM (que usa esperança de vida, renda per capita, escolaridade "
        "adulta e frequência escolar), então o modelo não recebe o alvo \"de presente\". Ainda assim, "
        "analfabetismo e escolaridade são temas próximos, e isso ajuda o modelo a acertar."),
      P("<b>Treino e teste:</b> %s municípios (70%%) para ajustar o modelo e %s (30%%) reservados para testar, "
        "com sorteio estratificado (mesma proporção de prioritários nos dois grupos) e semente 561376."
        % (n(q6["n_treino"], 0), n(q6["n_teste"], 0))),
      P("06A) Equação da regressão logística binária", h2),
      P("logit(p) = %s %s %s × t_analf18m %s %s × t_banagua %s %s × t_luz"
        % (n(c6["const"], 4),
           "+" if c6["t_analf18m"] >= 0 else "−", n(abs(c6["t_analf18m"]), 4),
           "+" if c6["t_banagua"] >= 0 else "−", n(abs(c6["t_banagua"]), 4),
           "+" if c6["t_luz"] >= 0 else "−", n(abs(c6["t_luz"]), 4)), formula),
      P("em que logit(p) = ln( p / (1 − p) ) e, portanto, p = 1 / (1 + e<super>−logit(p)</super>); "
        "p é a probabilidade de o município ser prioritário (classe 1).", normal),
      tabela([["Termo", "Coeficiente", "Razão de chances (e^coef.)", "p-valor"],
              ["Intercepto", n(c6["const"], 4), "-", pv(q6["p_valores"]["const"])]] +
             [[k, n(c6[k], 4), n(q6["odds_ratio"][k], 4), pv(q6["p_valores"][k])] for k in q6["x"]],
             [4.5 * cm, 3.3 * cm, 5 * cm, 3 * cm]),
      P("Tabela 12 - Coeficientes da regressão logística (ajustada na base de treino).", legenda),
      P("<b>Interpretação:</b> mantidas as demais variáveis, cada ponto percentual a mais de analfabetismo "
        "multiplica a chance de o município ser prioritário por %s (aumento de %s%%). Cada ponto a mais de "
        "cobertura de banheiro e água multiplica a chance por %s (queda de %s%%) e cada ponto a mais de energia "
        "elétrica, por %s (queda de %s%%). Todos os coeficientes são estatisticamente significativos."
        % (n(q6["odds_ratio"]["t_analf18m"], 3), n(100 * (q6["odds_ratio"]["t_analf18m"] - 1), 1),
           n(q6["odds_ratio"]["t_banagua"], 3), n(100 * (1 - q6["odds_ratio"]["t_banagua"]), 1),
           n(q6["odds_ratio"]["t_luz"], 3), n(100 * (1 - q6["odds_ratio"]["t_luz"]), 1))),
      P("06B) Matriz de confusão e acurácia", h2),
      P("Regra de decisão: o município é classificado como prioritário quando p ≥ 0,5. Resultados na base de "
        "teste (%s municípios que o modelo não usou no ajuste):" % n(total_teste, 0)),
      tabela([["", "Previsto: não prioritário (0)", "Previsto: prioritário (1)"],
              ["Real: não prioritário (0)", "%s (verdadeiros negativos)" % n(q6["vn"], 0),
               "%s (falsos positivos)" % n(q6["fp"], 0)],
              ["Real: prioritário (1)", "%s (falsos negativos)" % n(q6["fn"], 0),
               "%s (verdadeiros positivos)" % n(q6["vp"], 0)]],
             [5 * cm, 5.5 * cm, 5.5 * cm]),
      P("Tabela 13 - Matriz de confusão na base de teste.", legenda),
      figura("q06b_matriz_confusao.png", 8, "Figura 9 - Matriz de confusão na base de teste."),
      tabela([["Medida", "Valor", "Significado"],
              ["Acurácia", n(100 * q6["acuracia"]) + "%", "(%s + %s) / %s: proporção de acertos no total"
               % (n(q6["vn"], 0), n(q6["vp"], 0), n(total_teste, 0))],
              ["Acurácia de referência", n(100 * q6["acuracia_base"]) + "%",
               "Acerto de quem respondesse sempre \"não prioritário\""],
              ["Sensibilidade", n(100 * q6["sensibilidade"]) + "%",
               "Dos municípios realmente prioritários, quantos o modelo encontrou"],
              ["Especificidade", n(100 * q6["especificidade"]) + "%",
               "Dos não prioritários, quantos o modelo classificou corretamente"],
              ["Precisão", n(100 * q6["precisao"]) + "%",
               "Dos apontados como prioritários, quantos realmente são"]],
             [4.2 * cm, 2.6 * cm, 10.2 * cm]),
      P("Tabela 14 - Medidas de desempenho da classificação.", legenda),
      P("<b>Interpretação:</b> o modelo acerta %s%% dos municípios de teste, bem acima dos %s%% que se obteria "
        "sem modelo algum, o que mostra que ele realmente aprendeu um padrão. Os erros são dos dois tipos: %s "
        "municípios prioritários não foram identificados (falsos negativos) e %s foram apontados sem ser "
        "(falsos positivos). Para o projeto, o falso negativo é o erro mais caro, porque deixa de fora um "
        "município que precisava da solução; se for preciso reduzi-lo, basta baixar o corte de 0,5, aceitando "
        "mais falsos positivos."
        % (n(100 * q6["acuracia"], 1), n(100 * q6["acuracia_base"], 1), n(q6["fn"], 0), n(q6["fp"], 0))),
      P("06C) Classificação de um caso com três variáveis explicativas", h2),
      P("<b>Entradas declaradas:</b> analfabetismo = %s%%; banheiro e água encanada = %s%%; energia elétrica = "
        "%s%%." % (n(q6["class_entrada"]["t_analf18m"], 0), n(q6["class_entrada"]["t_banagua"], 0),
                   n(q6["class_entrada"]["t_luz"], 0))),
      P("logit = %s %s %s × %s %s %s × %s %s %s × %s = %s<br/>p = 1 / (1 + e<super>−(%s)</super>) = <b>%s</b> "
        "(%s%%)"
        % (n(c6["const"], 4),
           "+" if c6["t_analf18m"] >= 0 else "−", n(abs(c6["t_analf18m"]), 4),
           n(q6["class_entrada"]["t_analf18m"], 0),
           "+" if c6["t_banagua"] >= 0 else "−", n(abs(c6["t_banagua"]), 4),
           n(q6["class_entrada"]["t_banagua"], 0),
           "+" if c6["t_luz"] >= 0 else "−", n(abs(c6["t_luz"]), 4), n(q6["class_entrada"]["t_luz"], 0),
           n(q6["class_logit"], 4), n(q6["class_logit"], 4), n(q6["class_prob"], 4),
           n(100 * q6["class_prob"])), formula),
      P("<b>Classificação: %s.</b> Como a probabilidade estimada (%s%%) é %s do que 50%%, um município com esse "
        "perfil %s tratado como prioritário para o Citizen Assist AI."
        % (q6["class_texto"], n(100 * q6["class_prob"], 1),
           "maior" if q6["class_classe"] == 1 else "menor",
           "seria" if q6["class_classe"] == 1 else "não seria")),
      PageBreak()]

# ---------------------------------------------------------------- Q07
E += [P("8. Questão 07 - Onde estão os municípios prioritários", h1),
      P("Para transformar os modelos em decisão, a tabela abaixo mostra os estados com mais municípios nas "
        "faixas Baixo e Muito Baixo do IDHM (alvo da questão 06)."),
      tabela([["Estado", "Municípios", "Prioritários", "% do estado", "População nos prioritários"]] +
             [[u["ufn"], n(u["municipios"], 0), n(u["prioritarios"], 0), n(u["percentual"], 1) + "%",
               n(u["populacao_prioritarios"], 0)] for u in top],
             [4.5 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm, 4.4 * cm]),
      P("Tabela 15 - Estados com mais municípios prioritários (IDHM &lt; 0,600).", legenda),
      tabela([["Indicador (média dos municípios)", "Prioritários", "Demais"],
              ["Taxa de analfabetismo, 18 anos ou mais", n(q7["media_analf_prioritarios"], 1) + "%",
               n(q7["media_analf_demais"], 1) + "%"],
              ["Proporção de pobres", n(q7["media_pobres_prioritarios"], 1) + "%",
               n(q7["media_pobres_demais"], 1) + "%"],
              ["População com energia elétrica", n(q7["media_luz_prioritarios"], 1) + "%",
               n(q7["media_luz_demais"], 1) + "%"]],
             [8 * cm, 3.5 * cm, 3.5 * cm]),
      P("Tabela 16 - Perfil médio dos municípios prioritários e dos demais.", legenda),
      P("Nos municípios prioritários, em média, cerca de %s em cada 10 adultos não sabem ler nem escrever um "
        "bilhete simples e %s em cada 10 pessoas são pobres. São %s milhões de pessoas vivendo nesses "
        "municípios."
        % (n(q7["media_analf_prioritarios"] / 10, 0), n(q7["media_pobres_prioritarios"] / 10, 0),
           n(q7["pop_prioritarios"] / 1e6, 1))),

      P("9. Conclusão e recomendações para o Citizen Assist AI", h1),
      P("9.1 O que os dados mostram", h2),
      P("As quatro análises contam a mesma história por caminhos diferentes: os municípios onde há mais "
        "pobreza, e portanto mais dependência de serviços públicos, benefícios e documentos, são os mesmos onde "
        "há mais adultos que não leem e menos infraestrutura básica. Quem mais precisa de orientação é quem "
        "tem mais dificuldade de usar um canal digital comum."),
      P("9.2 Insights acionáveis", h2),
      P("<b>Projetar para quem lê pouco.</b> Com analfabetismo adulto médio de %s%% nos municípios "
        "prioritários, o assistente deve usar frases curtas, menus com opções numeradas, ícones e, quando "
        "possível, leitura das respostas em voz alta. Isso atende diretamente ao requisito de acessibilidade "
        "básica do desafio." % n(q7["media_analf_prioritarios"], 0), item, "1."),
      P("<b>Priorizar conteúdo de documentos básicos e programas sociais.</b> A previsão das questões 04 e 05 "
        "indica entre %s%% e %s%% de pobres em um município típico de analfabetismo alto. O primeiro conjunto "
        "de informações verificáveis deve cobrir RG, CPF, certidões, cadastro em programas sociais e tarifa "
        "social de energia." % (n(q4["prev_y"], 0), n(q5["prev_y"], 0)), item, "2."),
      P("<b>Funcionar com pouca infraestrutura.</b> A energia elétrica está quase universalizada, mas os "
        "municípios prioritários ainda têm cobertura média de %s%% contra %s%% nos demais, e a falta de "
        "banheiro e água encanada é o indicador mais ligado à pobreza (correlação de %s). A solução deve ser "
        "leve, rodar em celulares simples e ter versão para uso assistido em pontos de atendimento "
        "comunitário." % (n(q7["media_luz_prioritarios"], 1), n(q7["media_luz_demais"], 1),
                          n(mc["t_banagua"]["pmpob"], 2)), item, "3."),
      P("<b>Começar pelos lugares certos.</b> O modelo logístico (acurácia de %s%% no teste) e a Tabela 15 "
        "permitem ordenar os municípios para pilotos e parcerias, começando por %s, %s e %s."
        % (n(100 * q6["acuracia"], 1), top[0]["ufn"], top[1]["ufn"], top[2]["ufn"]), item, "4."),
      P("<b>Medir o piloto com o mesmo rigor.</b> O teste de hipótese da questão 03 pode ser reaplicado aos "
        "indicadores do protótipo (acerto das orientações, tempo para encontrar a informação) para saber se "
        "uma melhora observada é real ou apenas variação de amostra.", item, "5."),
      P("9.3 Limitações", h2),
      P("<b>Dados de 2010.</b> São os dados municipais mais completos disponíveis na base escolhida, mas a "
        "realidade mudou desde então; os valores absolutos devem ser atualizados quando houver indicadores "
        "municipais equivalentes mais recentes. As relações entre as variáveis tendem a ser mais estáveis do "
        "que os níveis.", item, "•"),
      P("<b>Nível municipal.</b> Os resultados descrevem municípios, não pessoas. Não se pode concluir que um "
        "indivíduo analfabeto é pobre; dentro de cada município há grande variação.", item, "•"),
      P("<b>Correlação não é causalidade.</b> Os modelos descrevem associações. Reduzir o analfabetismo não "
        "garante, por si só, a queda da pobreza prevista pelas equações.", item, "•"),
      P("<b>Suposição de normalidade.</b> Foi adotada por exigência do enunciado nas questões 02 e 03. A taxa "
        "de analfabetismo é assimétrica, e por isso as probabilidades da questão 02 diferem das proporções "
        "observadas, como mostrado na seção 3.", item, "•"),
      P("<b>Pressupostos da regressão.</b> A dispersão dos resíduos aumenta nos municípios mais pobres e as "
        "explicativas são correlacionadas entre si; os coeficientes devem ser lidos como tendências médias. "
        "Municípios vizinhos se parecem, o que torna os p-valores otimistas.", item, "•"),
      P("<b>Municípios com peso igual.</b> Cada município conta como uma observação, independentemente da "
        "população.", item, "•"),
      P("9.4 Referências", h2),
      P("PNUD; IPEA; FJP. <i>Atlas do Desenvolvimento Humano no Brasil 2013</i>. Dados dos Censos Demográficos "
        "do IBGE de 1991, 2000 e 2010.", item, "•"),
      P("ASSOCIAÇÃO BRASILEIRA DE JURIMETRIA. <i>abjData</i>: tabelas pnud_muni e pnud_siglas. Disponível em: "
        "https://github.com/abjur/abjData. Acesso em: 16 nov. 2026.", item, "•"),
      P("RIO GRANDE DO SUL. Atlas Socioeconômico do RS. <i>Mapa IDHM Brasil 2010</i> (faixas de desenvolvimento "
        "humano: Muito Baixo 0,000-0,499; Baixo 0,500-0,599; Médio 0,600-0,699; Alto 0,700-0,799; Muito Alto "
        "0,800-1,000). Disponível em: https://atlassocioeconomico.rs.gov.br/upload/arquivos/201611/"
        "24162649-mapa-idh-brasil-2010.pdf. Acesso em: 17 nov. 2026.", item, "•"),
      P("Código-fonte e reprodução: analise_estatistica.py (análises e gráficos), preparar_base.py (geração do "
        "CSV) e gerar_relatorio.py (este PDF). Todos os números deste relatório foram lidos de "
        "resultados.json, gerado pela execução do código.", item, "•")]

# Mantém "Entradas declaradas" na mesma página da conta que vem logo depois
for elemento in E:
    if isinstance(elemento, Paragraph) and elemento.text.startswith("<b>Entrada"):
        elemento.keepWithNext = True

doc = SimpleDocTemplate("Relatorio_Estatistico.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Relatório Estatístico - Citizen Assist AI",
                        author="Gustavo Zibini Belizario - RM 561376")
doc.build(E, onFirstPage=lambda c, d_: None, onLaterPages=rodape)
print("Relatório gerado: Relatorio_Estatistico.pdf")
