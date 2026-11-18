# Gera Relatorio_Computer_Science.pdf a partir do código e da execução real dos testes.
# Gustavo Zibini Belizario - RM 561376
import glob
import os
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether, Preformatted)
from decisao_logica import regra_original, expressao_canonica, expressao_simplificada, orientacao

est = getSampleStyleSheet()
T = ParagraphStyle("T", parent=est["Title"], fontSize=20, leading=24)
H1 = ParagraphStyle("H1", parent=est["Heading1"], fontSize=15, spaceBefore=10, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=est["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=4)
N = ParagraphStyle("N", parent=est["BodyText"], fontSize=10.5, leading=14.5, spaceAfter=5)
C = ParagraphStyle("C", parent=N, alignment=1)
MONO = ParagraphStyle("M", parent=est["Code"], fontSize=8, leading=10)
PEQ = ParagraphStyle("P", parent=N, fontSize=8.5, leading=11)

ESTILO_TAB = TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE6F0")),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
])


def tabela(dados, larguras, destaque_s=None):
    t = Table(dados, colWidths=larguras, repeatRows=1)
    estilo = TableStyle(ESTILO_TAB.getCommands())
    if destaque_s:
        for linha in destaque_s:
            estilo.add("BACKGROUND", (0, linha), (-1, linha), colors.HexColor("#E3F4E1"))
    t.setStyle(estilo)
    return t


def figura(caminho, largura_cm):
    img = Image(caminho)
    escala = (largura_cm * cm) / img.imageWidth
    img.drawWidth = img.imageWidth * escala
    img.drawHeight = img.imageHeight * escala
    return img


# Executa os testes de verdade e guarda a saída
saida_testes = subprocess.run(["python3", "testes_decisao.py"], capture_output=True, text=True).stdout
with open("evidencias/saida_testes.txt", "w") as f:
    f.write(saida_testes)
passou = "TODOS OS TESTES PASSARAM" in saida_testes

E = []
# ---------------- Capa ----------------
E += [Spacer(1, 4 * cm),
      Paragraph("Citizen Assist AI", T),
      Paragraph("Módulo de decisão lógica", ParagraphStyle("st", parent=T, fontSize=15)),
      Spacer(1, 1 * cm),
      Paragraph("Global Solution 2026.2 — Disciplina: Computer Science", C),
      Paragraph("Ciência da Computação — 1º ano — Turma 1CC", C),
      Spacer(1, 1.5 * cm),
      Paragraph("<b>Gustavo Zibini Belizario — RM 561376</b>", C),
      Spacer(1, 0.5 * cm),
      Paragraph("São Paulo, novembro de 2026", C),
      PageBreak()]

# ---------------- 1. Problema ----------------
E += [Paragraph("1. Descrição do problema", H1),
      Paragraph("Situação de atendimento escolhida: <b>“O cidadão pode ser atendido no balcão da Central do "
                "Cidadão agora?”</b>. Muitas pessoas vão ao balcão fora do horário, em fim de semana ou sem o "
                "agendamento obrigatório e perdem a viagem. O módulo responde com SIM ou NÃO e, quando é NÃO, "
                "explica o motivo e o que fazer.", N),
      Paragraph("O módulo é uma parte do Citizen Assist AI e pode ser executado e testado separadamente "
                "(pasta <font face='Courier'>computer-science/</font> do repositório).", N),

      Paragraph("2. Regras e referências", H1),
      Paragraph("As regras vêm da ficha <b>FC-07 — Regras gerais de atendimento</b> da Central do Cidadão de "
                "Aurora, versão de 01/10/2026, consultada em 18/11/2026. As fichas são o material de "
                "referência oficial do desafio Citizen Assist AI (material didático fictício fornecido pela "
                "FIAP) e a única fonte de verdade do assistente.", N),
      tabela([["Regra", "Texto da ficha FC-07"],
              ["R1", Paragraph("Atendimento presencial de segunda a sexta, das 8h às 17h. Não há atendimento "
                               "aos sábados, domingos e feriados.", PEQ)],
              ["R2", Paragraph("Agendamento é obrigatório para RG (FC-01) e CNH (FC-06). CPF, Carteira de "
                               "Trabalho digital, certidões e título de eleitor não exigem agendamento.", PEQ)]],
             [1.5 * cm, 14.5 * cm]),
      Spacer(1, 6),
      Paragraph("Regra em linguagem natural: <b>pode ser atendido</b> se for dia útil <b>e</b> estiver no "
                "horário <b>e</b> (o serviço não exigir agendamento <b>ou</b> a pessoa tiver agendamento).", N),

      Paragraph("3. Definição das variáveis", H1),
      tabela([["Var.", "Significado", "Valor 1", "Valor 0"],
              ["A", "Dia da semana", "Dia útil (seg. a sex.)", "Sábado, domingo ou feriado"],
              ["B", "Horário", "Entre 8h e 17h", "Fora do horário"],
              ["C", "Tipo de serviço", "Exige agendamento (RG, CNH)", "Não exige"],
              ["D", "Agendamento", "Tem agendamento marcado", "Não tem"],
              ["S", "Saída (orientação)", "Pode ser atendido agora", "Não pode (mostra o motivo)"]],
             [1.3 * cm, 3.4 * cm, 5.4 * cm, 5.9 * cm]),
      PageBreak()]

# ---------------- 4. Tabela-verdade ----------------
linhas = [["m", "A", "B", "C", "D", "S", "Orientação apresentada"]]
verdes = []
for m in range(16):
    a, b, c, d = (m >> 3) & 1, (m >> 2) & 1, (m >> 1) & 1, m & 1
    s = regra_original(a, b, c, d)
    if s:
        verdes.append(m + 1)
    texto = orientacao(a, b, c, d).replace("Não pode ser atendido agora. ", "NÃO: ").replace(
        "Pode ser atendido agora. ", "SIM: ")
    linhas.append([str(m), a, b, c, d, s, Paragraph(texto, PEQ)])
E += [Paragraph("4. Tabela-verdade", H1),
      Paragraph("Todas as 2<super>4</super> = 16 combinações das entradas. As linhas em verde são as que "
                "têm S = 1.", N),
      tabela(linhas, [0.8 * cm, 0.8 * cm, 0.8 * cm, 0.8 * cm, 0.8 * cm, 0.8 * cm, 11.2 * cm], verdes),
      PageBreak()]

# ---------------- 5. Forma canônica e álgebra ----------------
E += [Paragraph("5. Expressão na forma canônica (soma de mintermos)", H1),
      Paragraph("S = 1 apenas nas linhas 12 (1100), 13 (1101) e 15 (1111):", N),
      Paragraph("<b>S = Σm(12, 13, 15) = A·B·C'·D' + A·B·C'·D + A·B·C·D</b>", C),
      Paragraph("6. Simplificação por álgebra booleana", H1),
      tabela([["Passo", "Expressão", "Propriedade usada"],
              ["0", "S = ABC'D' + ABC'D + ABCD", "Forma canônica"],
              ["1", "S = ABC'D' + ABC'D + ABC'D + ABCD", Paragraph("Idempotência: X = X + X (ABC'D repetido "
                                                                   "para ser usado em dois pares)", PEQ)],
              ["2", "S = ABC'(D' + D) + ABD(C' + C)", "Distributiva: XY + XZ = X(Y + Z)"],
              ["3", "S = ABC'·1 + ABD·1", "Complemento: X + X' = 1"],
              ["4", "S = ABC' + ABD", "Identidade: X·1 = X"],
              ["5", "S = AB(C' + D)", "Distributiva (fator comum AB)"]],
             [1.4 * cm, 7.2 * cm, 7.4 * cm]),
      Spacer(1, 8),
      Paragraph("<b>Expressão simplificada: S = A·B·(C' + D)</b>", C),
      Paragraph("7. Transformação equivalente com De Morgan", H1),
      Paragraph("Aplicando De Morgan, (X·Y)' = X' + Y', com X = C e Y = D':", N),
      Paragraph("C' + D = C' + (D')' = (C·D')'  →  <b>S = A·B·(C·D')'</b>", C),
      Paragraph("A forma com De Morgan deixa a regra mais legível: o cidadão pode ser atendido em dia útil, "
                "no horário, desde que <b>não</b> seja o caso de “o serviço exigir agendamento <b>e</b> ele não "
                "ter agendamento”. O termo (C·D')' corresponde a uma porta NAND. O resultado é equivalente "
                "ao do passo 5 e foi conferido nas 16 combinações (seção 11).", N),
      PageBreak()]

# ---------------- 8. Karnaugh ----------------
E += [Paragraph("8. Mapa de Karnaugh", H1),
      Paragraph("Mapa 4×4 com AB nas linhas e CD nas colunas, na ordem do código de Gray (00, 01, 11, 10), "
                "para que células vizinhas difiram em apenas uma variável.", N),
      figura("figuras/mapa_karnaugh.png", 11),
      tabela([["Grupo", "Células", "O que se mantém", "Termo"],
              ["Azul (par)", "m12 + m13", "A = 1, B = 1, C = 0 (D varia)", "A·B·C'"],
              ["Vermelho (par)", "m13 + m15", "A = 1, B = 1, D = 1 (C varia)", "A·B·D"]],
             [3 * cm, 3 * cm, 6 * cm, 3 * cm]),
      Spacer(1, 6),
      Paragraph("Resultado do mapa: <b>S = A·B·C' + A·B·D = A·B·(C' + D)</b>. É o mesmo resultado do passo 4 "
                "da álgebra: o mapa faz visualmente o que a idempotência fez (m13 entra nos dois grupos). "
                "Não existe grupo de 4 células com 1, então dois pares é a cobertura mínima.", N),
      PageBreak()]

# ---------------- 9. Circuitos ----------------
E += [Paragraph("9. Circuitos lógicos", H1),
      Paragraph("<b>Circuito original</b> (forma canônica): um inversor por variável complementada (C' e D', "
                "compartilhados), uma porta AND por mintermo e uma porta OR. Os sinais com o mesmo nome estão "
                "ligados entre si.", N),
      figura("figuras/circuito_original.png", 15),
      Spacer(1, 8),
      Paragraph("<b>Circuito simplificado</b>: S = A·B·(C' + D).", N),
      figura("figuras/circuito_simplificado.png", 12),
      Spacer(1, 8),
      Paragraph("Comparação pelo mesmo critério: cada porta conta 1, qualquer que seja o número de entradas, e "
                "cada inversor é compartilhado por todas as portas que usam o mesmo sinal.", N),
      tabela([["", "Original", "Simplificado"],
              ["NOT", "2", "1"],
              ["AND", "3 (4 entradas cada)", "1 (3 entradas)"],
              ["OR", "1 (3 entradas)", "1 (2 entradas)"],
              ["Total de portas", "6", "3"],
              ["Total de entradas de portas", "17", "6"]],
             [5.5 * cm, 5 * cm, 5 * cm]),
      Paragraph("O circuito simplificado usa metade das portas e cerca de um terço das ligações, com o mesmo "
                "comportamento.", N),
      PageBreak()]

# ---------------- 10. Implementação ----------------
E += [Paragraph("10. Implementação e instruções de execução", H1),
      Paragraph("<b>Programa:</b> <font face='Courier'>decisao_logica.py</font> (Python 3, só biblioteca "
                "padrão). Pergunta A, B, C e D (D só quando o serviço exige agendamento), calcula "
                "S = A·B·(C' + D) e mostra a orientação em frases curtas.", N),
      Preformatted("cd computer-science\npython3 decisao_logica.py     # programa interativo\n"
                   "python3 testes_decisao.py     # validação das 16 combinações", MONO),
      Paragraph("<b>Tratamento de entradas:</b> aceita apenas 0 ou 1 (com ou sem espaços). Entrada vazia, "
                "texto, números diferentes de 0/1 e negativos geram mensagem e a pergunta é repetida. "
                "“s” encerra; Ctrl+C e Ctrl+D encerram sem erro técnico.", N),
      Paragraph("<b>Privacidade:</b> o programa não pede nome, documento, endereço nem telefone; só respostas "
                "sim/não.", N),
      Paragraph("<b>Simulador:</b> o circuito simplificado " + ("foi montado" if glob.glob("prints/*") else "é montado") + " no logic.ly (logic.ly/demo) com quatro "
                "chaves (A, B, C, D), uma porta NOT, uma OR de 2 entradas, uma AND de 3 entradas e uma "
                "lâmpada em S. Para reproduzir: arraste os componentes, ligue C → NOT → OR (entrada 1), "
                "D → OR (entrada 2), A, B e a saída da OR → AND, AND → lâmpada; clique nas chaves para "
                "mudar as entradas.", N)]

prints = sorted(glob.glob("prints/*.png") + glob.glob("prints/*.jpg") + glob.glob("prints/*.jpeg"))
if prints:
    E += [Paragraph("Prints de tela da simulação", H2)]
    for p in prints:
        nome = os.path.splitext(os.path.basename(p))[0].replace("_", " ")
        E += [KeepTogether([figura(p, 14), Paragraph(nome, C), Spacer(1, 6)])]
else:
    E += [Paragraph("<i>[Prints de tela da simulação no logic.ly: inserir na pasta prints/ e gerar o "
                    "relatório novamente.]</i>", N)]
E += [PageBreak()]

# ---------------- 11. Testes ----------------
linhas = [["m", "ABCD", "Regra original", "Canônica", "Simplificada", "Resultado"]]
for m in range(16):
    a, b, c, d = (m >> 3) & 1, (m >> 2) & 1, (m >> 1) & 1, m & 1
    r, k, s = regra_original(a, b, c, d), expressao_canonica(a, b, c, d), expressao_simplificada(a, b, c, d)
    linhas.append([str(m), "%d%d%d%d" % (a, b, c, d), r, k, s, "OK" if r == k == s else "ERRO"])
E += [Paragraph("11. Resultados dos testes", H1),
      Paragraph("O script <font face='Courier'>testes_decisao.py</font> executa as 16 combinações e compara a "
                "regra original (escrita como na ficha), a forma canônica e a expressão simplificada usada pelo "
                "programa. A tabela abaixo foi gerada a partir da execução real.", N),
      tabela(linhas, [1.2 * cm, 2 * cm, 3.2 * cm, 2.6 * cm, 3 * cm, 2.6 * cm]),
      Spacer(1, 6),
      Paragraph("Resultado: <b>%s</b>. As três representações são equivalentes em todas as combinações. "
                "Também passaram os testes de entrada inválida (vazio, “2”, “abc”, “-1”, “sim”, fim de "
                "entrada). Saída completa em <font face='Courier'>evidencias/saida_testes.txt</font>."
                % ("todos os testes passaram" if passou else "há falhas — ver evidências"), N),

      Paragraph("12. Limitações", H1)]
for t in ["As regras vêm de uma ficha didática fictícia; não valem como informação real de órgão público.",
          "O programa não confere a data e a hora sozinho: confia na resposta do usuário (A e B).",
          "Feriados não são verificados automaticamente.",
          "Não cobre exceções como atendimento prioritário, intérprete de Libras ou atendimento por terceiros.",
          "É um protótipo educacional: não é canal oficial e não confirma atendimento, concessão de serviços ou "
          "direitos."]:
    E.append(Paragraph("• " + t, N))


def rodape(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.2 * cm, "Citizen Assist AI — Computer Science — Gustavo Zibini Belizario — RM 561376")
    canvas.drawRightString(19 * cm, 1.2 * cm, "Página %d" % doc.page)


doc = SimpleDocTemplate("Relatorio_Computer_Science.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm, title="Citizen Assist AI - Computer Science",
                        author="Gustavo Zibini Belizario - RM 561376")
doc.build(E, onFirstPage=lambda c, d: None, onLaterPages=rodape)
print("Relatório gerado:", "OK" if passou else "COM FALHAS NOS TESTES")
