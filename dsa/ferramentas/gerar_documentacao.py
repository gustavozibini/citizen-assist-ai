# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# ferramentas/gerar_documentacao.py
# NÃO FAZ PARTE DO SISTEMA. É só uma ferramenta de apoio que:
#   1. copia para dentro de DOCUMENTACAO.md a tabela de evidências
#      (lida de evidencias/saida_testes.txt) e a sessão do menu
#      (lida de evidencias/sessao_menu.txt);
#   2. transforma o DOCUMENTACAO.md em Documentacao_DSA.pdf.
#
# Único arquivo do projeto que usa biblioteca externa (reportlab):
#   pip install reportlab
#
# Como executar (dentro da pasta dsa), depois de gerar as evidências:
#   python3 ferramentas/gerar_documentacao.py
# ==============================================================

import os
import re
import textwrap
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (ListFlowable, ListItem, PageBreak, Paragraph,
                                Preformatted, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ_MD = os.path.join(PASTA, "DOCUMENTACAO.md")
ARQ_PDF = os.path.join(PASTA, "Documentacao_DSA.pdf")
ARQ_TESTES = os.path.join(PASTA, "evidencias", "saida_testes.txt")
ARQ_SESSAO = os.path.join(PASTA, "evidencias", "sessao_menu.txt")

ALUNO = "Gustavo Zibini Belizario — RM 561376"
RODAPE = "Citizen Assist AI — DSA — " + ALUNO

# Fontes com todos os acentos e símbolos usados no documento.
PASTA_FONTES = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Texto", PASTA_FONTES + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Texto-Negrito", PASTA_FONTES + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", PASTA_FONTES + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrito",
                              italic="Texto", boldItalic="Texto-Negrito")

AZUL = colors.HexColor("#1F3A5F")
CINZA_CLARO = colors.HexColor("#F3F5F8")
CINZA_LINHA = colors.HexColor("#B8C0CC")
VERDE = colors.HexColor("#1B7F3B")
VERMELHO = colors.HexColor("#B3261E")

MARGEM = 20 * mm
LARGURA_UTIL = A4[0] - 2 * MARGEM
COLUNAS_CODIGO = 98        # caracteres por linha nos blocos de código do PDF


# ==============================================================
# PARTE 1 - COPIAR AS EVIDÊNCIAS PARA O DOCUMENTACAO.md
# ==============================================================

def ler(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return arquivo.read()


def celula_md(texto):
    """Dentro de tabela markdown, a barra vertical precisa de escape."""
    return texto.replace("|", "\\|")


def tabela_de_evidencias():
    """Lê a saída real dos testes e monta as tabelas em markdown."""
    linhas = ler(ARQ_TESTES).split("\n")
    md = []
    resumo = ""
    cenario = None
    aberta = False      # já existe uma tabela aberta no grupo atual?

    for i, linha in enumerate(linhas):
        # Título de grupo: fica entre duas linhas de traços.
        if (re.match(r"^\d+\. ", linha) and i > 0
                and linhas[i - 1].startswith("-----")):
            md.append("")
            md.append("**Grupo " + linha.strip() + "**")
            md.append("")
            md.append("<!-- evidencias -->")
            md.append("| Nº | Cenário | Entrada | Esperado | Observado | Situação |")
            md.append("|---|---|---|---|---|---|")
            aberta = True
        elif linha.startswith("[T"):
            codigo, descricao = linha.split("] ", 1)
            cenario = {"codigo": codigo[1:], "descricao": descricao}
        elif linha.startswith("  Entrada  : "):
            cenario["entrada"] = linha[len("  Entrada  : "):]
        elif linha.startswith("  Esperado : "):
            cenario["esperado"] = linha[len("  Esperado : "):]
        elif linha.startswith("  Observado: "):
            cenario["observado"] = linha[len("  Observado: "):]
        elif linha.startswith("  Situação : "):
            cenario["situacao"] = linha[len("  Situação : "):]
            assert aberta
            md.append("| " + " | ".join(celula_md(cenario[c]) for c in (
                "codigo", "descricao", "entrada", "esperado", "observado",
                "situacao")) + " |")
        elif linha.startswith("RESUMO: "):
            resumo = linha[len("RESUMO: "):]

    partes = [p.strip() for p in resumo.split("|")]
    cabecalho = ("**Resumo da execução:** " + ", ".join(partes) +
                 ". Linha final do arquivo `evidencias/saida_testes.txt`.")
    return [cabecalho] + md, resumo


def substituir_trecho(texto, marcador, novo):
    inicio = "<!-- " + marcador + ":INICIO -->"
    fim = "<!-- " + marcador + ":FIM -->"
    antes = texto[:texto.index(inicio) + len(inicio)]
    depois = texto[texto.index(fim):]
    return antes + "\n" + novo + "\n" + depois


def atualizar_markdown():
    md = ler(ARQ_MD)
    tabela, resumo = tabela_de_evidencias()
    md = substituir_trecho(md, "EVIDENCIAS", "\n".join(tabela))
    sessao = ler(ARQ_SESSAO).rstrip("\n")
    md = substituir_trecho(md, "SESSAO", "```text\n" + sessao + "\n```")
    with open(ARQ_MD, "w", encoding="utf-8") as arquivo:
        arquivo.write(md)
    return md, resumo


# ==============================================================
# PARTE 2 - MARKDOWN -> PDF
# ==============================================================

E_CORPO = ParagraphStyle("corpo", fontName="Texto", fontSize=9.6, leading=14,
                         spaceAfter=6, alignment=TA_LEFT)
E_ITEM = ParagraphStyle("item", parent=E_CORPO, spaceAfter=2)
E_H2 = ParagraphStyle("h2", fontName="Texto-Negrito", fontSize=14.5, leading=18,
                      textColor=AZUL, spaceBefore=14, spaceAfter=7,
                      keepWithNext=1)
E_H3 = ParagraphStyle("h3", fontName="Texto-Negrito", fontSize=11.2, leading=15,
                      textColor=AZUL, spaceBefore=9, spaceAfter=5,
                      keepWithNext=1)
E_CODIGO = ParagraphStyle("codigo", fontName="Mono", fontSize=7.4, leading=9.3,
                          backColor=CINZA_CLARO, borderPadding=5,
                          leftIndent=5, rightIndent=5, spaceBefore=6,
                          spaceAfter=11)
E_CELULA = ParagraphStyle("celula", fontName="Texto", fontSize=8, leading=10.6)
E_CELULA_CAB = ParagraphStyle("celula_cab", parent=E_CELULA,
                              fontName="Texto-Negrito", textColor=colors.white)
E_EVID = ParagraphStyle("evid", fontName="Texto", fontSize=6.7, leading=8.6)
E_EVID_CAB = ParagraphStyle("evid_cab", parent=E_EVID,
                            fontName="Texto-Negrito", textColor=colors.white)

# Larguras (em %) das colunas das tabelas de evidências.
LARGURAS_EVIDENCIAS = [5.5, 18.5, 18, 24, 24, 10]


def formatar(texto, tamanho_codigo):
    """Converte **negrito** e `código` do markdown para o reportlab.

    O negrito é tratado primeiro porque pode envolver um trecho de
    código (exemplo: **`No`**).
    """
    saida = ""
    for i, trecho in enumerate(texto.split("**")):
        convertido = ""
        for j, parte in enumerate(trecho.split("`")):
            parte = escape(parte)
            if j % 2 == 1:
                convertido += (f'<font face="Mono" size="{tamanho_codigo}">'
                               f'{parte}</font>')
            else:
                convertido += parte
        if i % 2 == 1:
            convertido = "<b>" + convertido + "</b>"
        saida += convertido
    return saida


def quebrar_codigo(linhas):
    """Quebra linhas longas dos blocos de código para caberem na página."""
    saida = []
    for linha in linhas:
        if len(linha) <= COLUNAS_CODIGO:
            saida.append(linha)
        else:
            saida.extend(textwrap.wrap(linha, COLUNAS_CODIGO,
                                       subsequent_indent="        ",
                                       break_long_words=True,
                                       replace_whitespace=False,
                                       drop_whitespace=False))
    return saida


def celulas_da_linha(linha):
    linha = linha.strip()
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|") and not linha.endswith("\\|"):
        linha = linha[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", linha)]


def montar_tabela(linhas, larguras, evidencias):
    cabecalho = celulas_da_linha(linhas[0])
    corpo = [celulas_da_linha(l) for l in linhas[2:]]

    if evidencias:
        est, est_cab, tam_cod = E_EVID, E_EVID_CAB, 6.3
        larguras = LARGURAS_EVIDENCIAS
    else:
        est, est_cab, tam_cod = E_CELULA, E_CELULA_CAB, 7.4
    if larguras is None:
        larguras = [100 / len(cabecalho)] * len(cabecalho)
    total = sum(larguras)
    col = [LARGURA_UTIL * p / total for p in larguras]

    dados = [[Paragraph(formatar(c, tam_cod), est_cab) for c in cabecalho]]
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, CINZA_LINHA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    for n, linha in enumerate(corpo, start=1):
        celulas = []
        for j, c in enumerate(linha):
            texto = formatar(c, tam_cod)
            if evidencias and j == len(linha) - 1:
                cor = "#1B7F3B" if c == "OK" else "#B3261E"
                texto = f'<font color="{cor}"><b>{texto}</b></font>'
            celulas.append(Paragraph(texto, est))
        dados.append(celulas)
        if n % 2 == 0:
            estilo.append(("BACKGROUND", (0, n), (-1, n), CINZA_CLARO))

    tabela = Table(dados, colWidths=col, repeatRows=1)
    tabela.setStyle(TableStyle(estilo))
    return tabela


def markdown_para_story(md):
    """Lê o markdown linha a linha e devolve a lista de blocos do PDF."""
    linhas = md.split("\n")
    # A capa do PDF já traz a identificação: pula até o primeiro "## ".
    i = 0
    while not linhas[i].startswith("## "):
        i += 1

    story = []
    larguras = None
    evidencias = False
    while i < len(linhas):
        linha = linhas[i]

        if linha.strip() == "":
            i += 1
        elif linha.startswith("<!-- larguras:"):
            larguras = [float(x) for x in linha[14:-3].split()]
            i += 1
        elif linha.startswith("<!-- evidencias"):
            evidencias = True
            i += 1
        elif linha.startswith("<!--"):
            i += 1
        elif linha.startswith("## "):
            if linha.startswith("## Apêndice"):
                story.append(PageBreak())
            story.append(Paragraph(formatar(linha[3:], 13), E_H2))
            i += 1
        elif linha.startswith("### "):
            story.append(Paragraph(formatar(linha[4:], 10.2), E_H3))
            i += 1
        elif linha.startswith("```"):
            bloco = []
            i += 1
            while not linhas[i].startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1
            story.append(Preformatted("\n".join(quebrar_codigo(bloco)), E_CODIGO))
        elif linha.startswith("|"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith("|"):
                bloco.append(linhas[i])
                i += 1
            story.append(montar_tabela(bloco, larguras, evidencias))
            story.append(Spacer(1, 9))
            larguras = None
            evidencias = False
        elif linha.startswith("- ") or re.match(r"^\d+\. ", linha):
            numerada = not linha.startswith("- ")
            itens = []
            while i < len(linhas) and (linhas[i].startswith("- ")
                                       or re.match(r"^\d+\. ", linhas[i])):
                texto = re.sub(r"^(- |\d+\. )", "", linhas[i])
                itens.append(ListItem(Paragraph(formatar(texto, 8.8), E_ITEM),
                                      leftIndent=16))
                i += 1
            story.append(ListFlowable(
                itens, bulletType="1" if numerada else "bullet",
                bulletFontName="Texto", bulletFontSize=9 if numerada else 7,
                start=None if numerada else "•", leftIndent=16,
                bulletFormat="%s." if numerada else None))
            story.append(Spacer(1, 5))
        else:
            # Parágrafo: junta as linhas até a próxima linha em branco.
            bloco = []
            while i < len(linhas) and linhas[i].strip() != "" \
                    and not re.match(r"^(#|\||```|- |<!--|\d+\. )", linhas[i]):
                bloco.append(linhas[i].strip())
                i += 1
            texto = " ".join(bloco)
            # O título de cada grupo de testes fica grudado na sua tabela.
            if texto.startswith("**Grupo "):
                estilo = ParagraphStyle("grupo", parent=E_CORPO, keepWithNext=1)
            else:
                estilo = E_CORPO
            story.append(Paragraph(formatar(texto, 8.8), estilo))
    return story


def desenhar_capa(canvas, doc):
    largura, altura = A4
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, altura - 62 * mm, largura, 62 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Texto", 11)
    canvas.drawString(MARGEM, altura - 24 * mm,
                      "FIAP — Global Solution 2026.2 — Citizen Tech")
    canvas.setFont("Texto-Negrito", 30)
    canvas.drawString(MARGEM, altura - 44 * mm, "Citizen Assist AI")

    canvas.setFillColor(AZUL)
    canvas.setFont("Texto-Negrito", 17)
    canvas.drawString(MARGEM, altura - 86 * mm, "Documentação técnica")
    canvas.setFont("Texto", 13)
    canvas.drawString(MARGEM, altura - 96 * mm,
                      "Disciplina: Data Structures and Algorithms (DSA)")
    canvas.setFillColor(colors.black)
    canvas.setFont("Texto", 11)
    canvas.drawString(MARGEM, altura - 110 * mm,
                      "Sistema de gerenciamento e consulta de serviços e orientações ao")
    canvas.drawString(MARGEM, altura - 116 * mm,
                      "cidadão, com lista encadeada, busca linear e merge sort em Python.")

    canvas.setStrokeColor(CINZA_LINHA)
    canvas.line(MARGEM, altura - 150 * mm, largura - MARGEM, altura - 150 * mm)
    canvas.setFont("Texto-Negrito", 14)
    canvas.drawString(MARGEM, altura - 162 * mm, ALUNO)
    canvas.setFont("Texto", 11)
    canvas.drawString(MARGEM, altura - 171 * mm,
                      "Ciência da Computação — 1º ano — entrega individual")
    canvas.drawString(MARGEM, altura - 178 * mm, "Novembro de 2026")

    canvas.setFont("Texto", 8.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(MARGEM, 22 * mm,
                      "Protótipo educacional com dados fictícios. Não é canal "
                      "oficial de atendimento e não coleta dados pessoais.")
    canvas.restoreState()


def desenhar_rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Texto", 7.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setStrokeColor(CINZA_LINHA)
    canvas.line(MARGEM, 14 * mm, A4[0] - MARGEM, 14 * mm)
    canvas.drawString(MARGEM, 10 * mm, RODAPE)
    canvas.drawRightString(A4[0] - MARGEM, 10 * mm, f"Página {doc.page}")
    canvas.restoreState()


def gerar_pdf(md):
    doc = SimpleDocTemplate(
        ARQ_PDF, pagesize=A4, leftMargin=MARGEM, rightMargin=MARGEM,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="Citizen Assist AI — Documentação técnica (DSA)",
        author="Gustavo Zibini Belizario — RM 561376",
        subject="Global Solution 2026.2 — Data Structures and Algorithms")
    story = [Spacer(1, 10), PageBreak()] + markdown_para_story(md)
    doc.build(story, onFirstPage=desenhar_capa, onLaterPages=desenhar_rodape)


if __name__ == "__main__":
    texto_md, resumo_testes = atualizar_markdown()
    gerar_pdf(texto_md)
    print("Evidências copiadas para DOCUMENTACAO.md")
    print("Resumo dos testes:", resumo_testes)
    print("PDF gerado em", ARQ_PDF)
