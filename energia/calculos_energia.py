# -*- coding: utf-8 -*-
"""
Citizen Assist AI - Soluções em Energias Renováveis e Sustentáveis
Aluno: Gustavo Zibini Belizario - RM 561376 (FIAP, 1CC, Global Solution 2026.2)

Cálculos de energia do banho quente para uma família de São Paulo.
Compara, para a MESMA necessidade (os mesmos banhos), as alternativas:
  A  - chuveiro elétrico usado sem cuidado (caso-base)
  B  - hábitos: banho mais curto e chave na posição verão nos meses quentes
  C1 - aquecedor solar comercial, com o chuveiro como apoio
  C2 - aquecedor solar de baixo custo (ASBC), com o chuveiro como apoio
  D  - energia solar fotovoltaica (compensação de energia)

Todos os números vêm de dados/premissas.csv. Nada é digitado à mão aqui.
Uso:  python3 calculos_energia.py   (gera a pasta resultados/)
"""

import csv
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQUIVO_PREMISSAS = PASTA / "dados" / "premissas.csv"
PASTA_RESULTADOS = PASTA / "resultados"


# ---------------------------------------------------------------------------
# 1. Leitura das premissas
# ---------------------------------------------------------------------------

def carregar_detalhes(caminho=ARQUIVO_PREMISSAS):
    """Lê o CSV e devolve uma lista com todas as colunas de cada premissa."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def carregar_premissas(caminho=ARQUIVO_PREMISSAS):
    """Devolve um dicionário {chave: valor numérico} com as premissas."""
    return {linha["chave"]: float(linha["valor"]) for linha in carregar_detalhes(caminho)}


# ---------------------------------------------------------------------------
# 2. Fórmulas básicas (funções puras: só recebem números e devolvem números)
# ---------------------------------------------------------------------------

def energia_kwh(potencia_w, horas):
    """E = P x t.  Potência em W, tempo em horas, resultado em kWh."""
    return (potencia_w / 1000) * horas


def consumo_banho_kwh_mes(moradores, banhos_por_dia, minutos, potencia_w, dias_mes):
    """Energia do banho em um mês (kWh/mês).
    horas de chuveiro no mês = moradores x banhos x (minutos / 60) x dias."""
    horas_no_mes = moradores * banhos_por_dia * (minutos / 60) * dias_mes
    return energia_kwh(potencia_w, horas_no_mes)


def tarifa_convencional(p):
    """Tarifa residencial B1 da Enel SP, sem impostos (R$/kWh) = TUSD + TE."""
    return p["tarifa_tusd"] + p["tarifa_te"]


def tarifa_baixa_renda(p):
    """Tarifa da parcela acima de 80 kWh na Tarifa Social, sem impostos (R$/kWh)."""
    return p["tarifa_social_tusd"] + p["tarifa_social_te"]


def custo_reais(consumo_kwh, tarifa_reais_kwh):
    """Custo = consumo (kWh) x tarifa (R$/kWh)."""
    return consumo_kwh * tarifa_reais_kwh


def conta_tarifa_social(consumo_total_kwh, p):
    """Conta de energia (R$/mês) de quem tem Tarifa Social.
    Os primeiros 80 kWh do mês são gratuitos. Só o que passa disso é pago."""
    kwh_pagos = max(0.0, consumo_total_kwh - p["franquia_tarifa_social_kwh"])
    return custo_reais(kwh_pagos, tarifa_baixa_renda(p))


def custo_banho_mes(consumo_banho_kwh, p, tarifa_social=False):
    """Custo mensal do banho (R$/mês).
    Convencional: consumo x tarifa.
    Tarifa Social: diferença entre a conta da casa com banho e sem banho."""
    if not tarifa_social:
        return custo_reais(consumo_banho_kwh, tarifa_convencional(p))
    outros = p["outros_consumos_casa_kwh"]
    return conta_tarifa_social(outros + consumo_banho_kwh, p) - conta_tarifa_social(outros, p)


def payback_meses(investimento, economia_mensal):
    """Payback simples (meses) = investimento / economia mensal.
    Devolve 0 se não há investimento e None se não há economia."""
    if investimento <= 0:
        return 0.0
    if economia_mensal <= 0:
        return None
    return investimento / economia_mensal


def emissoes_kg(consumo_kwh, fator_kg_por_kwh):
    """Emissões de CO2 (kg) = energia da rede (kWh) x fator de emissão (kg CO2/kWh)."""
    return consumo_kwh * fator_kg_por_kwh


def potencia_media_habitos(potencia_w, p, ja_usa_verao=False):
    """Potência média do ano na alternativa de hábitos (W).
    Nos meses quentes a chave fica na posição verão (potência menor)."""
    if ja_usa_verao:
        return potencia_w  # quem já usa a posição verão não tem mais o que reduzir
    meses_quentes = p["meses_quentes_ano"]
    potencia_verao = potencia_w * (1 - p["reducao_posicao_verao"])
    return (potencia_verao * meses_quentes + potencia_w * (12 - meses_quentes)) / 12


def energia_solar_util_kwh_mes(demanda_kwh, fracao_solar, area_m2, irradiacao, eficiencia, dias_mes):
    """Energia do banho atendida pelo sol (kWh/mês).
    É a fração solar x demanda, limitada ao que o coletor consegue captar:
    teto = área (m2) x irradiação (kWh/m2/dia) x eficiência x dias."""
    teto = area_m2 * irradiacao * eficiencia * dias_mes
    return min(fracao_solar * demanda_kwh, teto)


def potencia_fotovoltaica_kwp(energia_kwh_mes, irradiacao, taxa_desempenho, dias_mes):
    """Potência do sistema fotovoltaico (kWp) para gerar a energia do banho.
    geração por kWp no mês = irradiação (kWh/m2/dia) x dias x taxa de desempenho."""
    geracao_por_kwp = irradiacao * dias_mes * taxa_desempenho
    return energia_kwh_mes / geracao_por_kwp


# ---------------------------------------------------------------------------
# 3. Comparação das alternativas para a mesma necessidade
# ---------------------------------------------------------------------------

def comparar_alternativas(p, moradores=None, minutos=None, potencia_w=None,
                          ja_usa_verao=False, tarifa_social=False):
    """Calcula as alternativas A, B, C1, C2 e D e devolve uma lista de dicionários.
    Sem argumentos, usa o caso-base de premissas.csv."""
    moradores = p["moradores"] if moradores is None else moradores
    minutos = p["minutos_banho_base"] if minutos is None else minutos
    potencia_w = p["potencia_chuveiro_w"] if potencia_w is None else potencia_w
    banhos = p["banhos_por_pessoa_dia"]
    dias = p["dias_mes"]
    irradiacao = p["irradiacao_kwh_m2_dia"]

    # A - caso-base: é a necessidade de energia que todas as alternativas atendem
    consumo_a = consumo_banho_kwh_mes(moradores, banhos, minutos, potencia_w, dias)

    # B - hábitos: banho mais curto e posição verão nos meses quentes
    minutos_b = min(minutos, p["minutos_banho_eficiente"])
    potencia_b = potencia_media_habitos(potencia_w, p, ja_usa_verao)
    consumo_b = consumo_banho_kwh_mes(moradores, banhos, minutos_b, potencia_b, dias)

    # C1 - aquecedor solar comercial: o sol atende parte; o chuveiro completa
    solar_c1 = energia_solar_util_kwh_mes(
        consumo_a, p["solar_comercial_fracao_solar"], p["solar_comercial_area_m2"],
        irradiacao, p["solar_comercial_eficiencia"], dias)
    consumo_c1 = consumo_a - solar_c1

    # C2 - aquecedor solar de baixo custo (ASBC)
    solar_c2 = energia_solar_util_kwh_mes(
        consumo_a, p["asbc_fracao_solar"], p["asbc_area_m2"],
        irradiacao, p["asbc_eficiencia"], dias)
    consumo_c2 = consumo_a - solar_c2

    # D - fotovoltaica: gera a mesma energia que o banho consome (compensação)
    # Preço por kWp de um sistema pequeno (2 kWp), mais próximo da realidade da família.
    # O preço de sistema maior (4 kWp, mais barato por kWp) fica na análise de sensibilidade.
    kwp = potencia_fotovoltaica_kwp(consumo_a, irradiacao, p["fv_taxa_desempenho"], dias)
    preco_por_kwp = p["fv_preco_sistema_pequeno"] / p["fv_potencia_sistema_pequeno_kwp"]
    investimento_d = kwp * preco_por_kwp
    consumo_d = 0.0  # consumo líquido da rede depois da compensação (simplificação)

    lista = [
        ("A", "Chuveiro elétrico sem cuidado (caso-base)", consumo_a, 0.0),
        ("B", "Hábitos: banho curto e posição verão", consumo_b, 0.0),
        ("C1", "Aquecedor solar comercial + chuveiro de apoio", consumo_c1,
         p["solar_comercial_investimento"]),
        ("C2", "Aquecedor solar de baixo custo (ASBC) + apoio", consumo_c2,
         p["asbc_investimento"]),
        ("D", "Solar fotovoltaica (compensação de energia)", consumo_d, investimento_d),
    ]

    custo_a = custo_banho_mes(consumo_a, p, tarifa_social)
    meses_horizonte = p["horizonte_anos"] * 12
    fator = p["fator_emissao_kg_kwh"]

    resultado = []
    for codigo, nome, consumo, investimento in lista:
        custo = custo_banho_mes(consumo, p, tarifa_social)
        economia = custo_a - custo
        meses = payback_meses(investimento, economia)
        resultado.append({
            "codigo": codigo,
            "nome": nome,
            "consumo_kwh_mes": consumo,
            "consumo_kwh_ano": consumo * 12,
            "custo_mes": custo,
            "custo_ano": custo * 12,
            "investimento": investimento,
            "economia_mes": economia,
            "economia_ano": economia * 12,
            "payback_meses": meses,
            "payback_anos": None if meses is None else meses / 12,
            "co2_ano": emissoes_kg(consumo * 12, fator),
            "co2_evitado_ano": emissoes_kg((consumo_a - consumo) * 12, fator),
            "custo_total_horizonte": investimento + custo * meses_horizonte,
            "economia_liquida_horizonte": economia * meses_horizonte - investimento,
        })
    return resultado


def buscar(alternativas, codigo):
    """Devolve a alternativa com o código pedido (A, B, C1, C2 ou D)."""
    for alternativa in alternativas:
        if alternativa["codigo"] == codigo:
            return alternativa
    raise KeyError(codigo)


def analise_sensibilidade(p):
    """Refaz contas trocando uma premissa por vez. Devolve um dicionário."""
    base = comparar_alternativas(p)
    consumo_a = buscar(base, "A")["consumo_kwh_mes"]

    # C1 com a fração solar mínima da Lei Solar de São Paulo (cenário pessimista)
    p_min = dict(p)
    p_min["solar_comercial_fracao_solar"] = p["solar_comercial_fracao_minima"]
    c1_min = buscar(comparar_alternativas(p_min), "C1")

    # Teto de energia solar do coletor comercial no inverno (menos sol)
    teto_inverno = (p["solar_comercial_area_m2"] * p["irradiacao_inverno_kwh_m2_dia"]
                    * p["solar_comercial_eficiencia"] * p["dias_mes"])

    # Emissões do caso-base com o fator alternativo (meses de 2025)
    co2_alternativo = emissoes_kg(consumo_a * 12, p["fator_emissao_alternativo_kg_kwh"])

    # D otimista: preço por kWp de um sistema de 4 kWp (pesquisa Greener)
    economia_d = buscar(base, "D")["economia_mes"]
    kwp = potencia_fotovoltaica_kwp(
        consumo_a, p["irradiacao_kwh_m2_dia"], p["fv_taxa_desempenho"], p["dias_mes"])
    investimento_otimista = kwp * p["fv_preco_sistema_ref"] / p["fv_potencia_sistema_ref_kwp"]

    # D com um sistema pequeno inteiro (2 kWp), pago só com a economia do banho
    payback_fv_pequeno = payback_meses(p["fv_preco_sistema_pequeno"], economia_d)

    return {
        "fv_pequeno_payback_meses": payback_fv_pequeno,
        "fv_investimento_otimista": investimento_otimista,
        "fv_payback_otimista_meses": payback_meses(investimento_otimista, economia_d),
        "c1_fracao_minima": c1_min,
        "teto_solar_inverno_kwh_mes": teto_inverno,
        "fracao_maxima_inverno": min(1.0, teto_inverno / consumo_a),
        "co2_base_ano_fator_alternativo": co2_alternativo,
        "fv_kwp": kwp,
        "fv_preco_por_wp": p["fv_preco_sistema_pequeno"] / (p["fv_potencia_sistema_pequeno_kwp"] * 1000),
        "fv_preco_por_wp_otimista": p["fv_preco_sistema_ref"] / (p["fv_potencia_sistema_ref_kwp"] * 1000),
    }


# ---------------------------------------------------------------------------
# 4. Formatação (padrão brasileiro: vírgula decimal)
# ---------------------------------------------------------------------------

def fmt(valor, casas=1):
    """Número com vírgula decimal e ponto de milhar. Ex.: 1234.5 -> '1.234,5'."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "#").replace(".", ",").replace("#", ".")


def fmt_reais(valor):
    return "R$ " + fmt(valor, 2)


def fmt_payback(alternativa):
    """Texto do tempo de retorno de uma alternativa."""
    meses = alternativa["payback_meses"]
    if alternativa["investimento"] <= 0:
        return "sem investimento"
    if meses is None:
        return "não se paga"
    return f"{fmt(meses, 0)} meses ({fmt(meses / 12, 1)} anos)"


# ---------------------------------------------------------------------------
# 5. Geração dos arquivos de resultado
# ---------------------------------------------------------------------------

COLUNAS_CSV = ["cenario", "codigo", "nome", "consumo_kwh_mes", "consumo_kwh_ano", "custo_mes",
               "custo_ano", "investimento", "economia_mes", "economia_ano", "payback_meses",
               "payback_anos", "co2_ano", "co2_evitado_ano", "custo_total_horizonte",
               "economia_liquida_horizonte"]


def salvar_csv(cenarios, caminho):
    """Grava a comparação em CSV (ponto decimal, separador ponto e vírgula)."""
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(COLUNAS_CSV)
        for nome_cenario, alternativas in cenarios:
            for a in alternativas:
                linha = [nome_cenario]
                for coluna in COLUNAS_CSV[1:]:
                    valor = a[coluna]
                    if isinstance(valor, float):
                        valor = round(valor, 2)
                    linha.append("" if valor is None else valor)
                escritor.writerow(linha)


def tabela_markdown(alternativas, p):
    """Monta a tabela comparativa em Markdown."""
    anos = fmt(p["horizonte_anos"], 0)
    linhas = [
        "| Alt. | Alternativa | Consumo da rede (kWh/mês) | Consumo (kWh/ano) | Custo (R$/mês) "
        "| Custo (R$/ano) | Investimento (R$) | Economia (R$/mês) | Economia (R$/ano) "
        f"| Payback simples | CO2 evitado (kg/ano) | Saldo em {anos} anos (R$) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for a in alternativas:
        linhas.append(
            f"| {a['codigo']} | {a['nome']} | {fmt(a['consumo_kwh_mes'])} "
            f"| {fmt(a['consumo_kwh_ano'])} | {fmt(a['custo_mes'], 2)} | {fmt(a['custo_ano'], 2)} "
            f"| {fmt(a['investimento'], 2)} | {fmt(a['economia_mes'], 2)} "
            f"| {fmt(a['economia_ano'], 2)} | {fmt_payback(a)} | {fmt(a['co2_evitado_ano'])} "
            f"| {fmt(a['economia_liquida_horizonte'], 2)} |")
    return "\n".join(linhas)


def texto_comparacao_md(p):
    """Monta o arquivo resultados/comparacao.md completo."""
    convencional = comparar_alternativas(p)
    social = comparar_alternativas(p, tarifa_social=True)
    s = analise_sensibilidade(p)
    a = buscar(convencional, "A")
    c1 = buscar(convencional, "C1")
    anos = fmt(p["horizonte_anos"], 0)

    partes = [
        "# Comparação das alternativas para o banho quente",
        "",
        "Arquivo gerado por `calculos_energia.py`. Não edite à mão: rode o script de novo.",
        "",
        f"Necessidade comparada: banho quente de {fmt(p['moradores'], 0)} pessoas, "
        f"{fmt(p['banhos_por_pessoa_dia'], 0)} banho por pessoa por dia, "
        f"{fmt(p['minutos_banho_base'], 0)} minutos, chuveiro de {fmt(p['potencia_chuveiro_w'], 0)} W, "
        f"em São Paulo (SP). Período: mês de {fmt(p['dias_mes'], 0)} dias, ano de 12 meses "
        f"e horizonte de {anos} anos.",
        "",
        f"## Tabela 1 - Tarifa residencial convencional ({fmt(tarifa_convencional(p), 5)} R$/kWh, sem impostos)",
        "",
        tabela_markdown(convencional, p),
        "",
        f"## Tabela 2 - Família com Tarifa Social (80 kWh gratuitos; excedente a "
        f"{fmt(tarifa_baixa_renda(p), 5)} R$/kWh, sem impostos)",
        "",
        f"Premissa estimada: o resto da casa consome {fmt(p['outros_consumos_casa_kwh'], 0)} kWh/mês. "
        "Assim a gratuidade já é usada pelos outros aparelhos e o banho é todo pago na tarifa do excedente.",
        "",
        tabela_markdown(social, p),
        "",
        "## Análise de sensibilidade",
        "",
        f"- Aquecedor solar comercial com a fração solar mínima da Lei Solar de São Paulo "
        f"({fmt(p['solar_comercial_fracao_minima'] * 100, 0)}%): economia de "
        f"{fmt_reais(s['c1_fracao_minima']['economia_mes'])} por mês e payback de "
        f"{fmt_payback(s['c1_fracao_minima'])} (no caso-base: {fmt_payback(c1)}).",
        f"- No inverno a irradiação cai para {fmt(p['irradiacao_inverno_kwh_m2_dia'], 3)} kWh/m2/dia. "
        f"O coletor comercial de {fmt(p['solar_comercial_area_m2'], 1)} m2 capta no máximo "
        f"{fmt(s['teto_solar_inverno_kwh_mes'])} kWh/mês de calor útil, "
        f"ou {fmt(s['fracao_maxima_inverno'] * 100, 0)}% do caso-base. O apoio elétrico é mais usado no inverno.",
        f"- Emissões do caso-base: {fmt(a['co2_ano'])} kg CO2/ano com o fator de "
        f"{fmt(p['fator_emissao_kg_kwh'], 4)} kg CO2/kWh. Com o fator alternativo de "
        f"{fmt(p['fator_emissao_alternativo_kg_kwh'], 4)} kg CO2/kWh seriam "
        f"{fmt(s['co2_base_ano_fator_alternativo'])} kg CO2/ano.",
        f"- Fotovoltaica: o banho do caso-base pede cerca de {fmt(s['fv_kwp'], 2)} kWp. Na tabela usamos "
        f"{fmt(s['fv_preco_por_wp'], 2)} R$/Wp (sistema pequeno, estimado). Com o preço médio de um sistema "
        f"de {fmt(p['fv_potencia_sistema_ref_kwp'], 0)} kWp ({fmt(s['fv_preco_por_wp_otimista'], 2)} R$/Wp), "
        f"o investimento cairia para {fmt_reais(s['fv_investimento_otimista'])} e o retorno para "
        f"{fmt(s['fv_payback_otimista_meses'], 0)} meses ({fmt(s['fv_payback_otimista_meses'] / 12, 1)} anos). "
        "Nos dois casos a compensação tem cobranças mínimas que não entraram no cálculo.",
        f"- Fotovoltaica comprando um sistema inteiro de {fmt(p['fv_potencia_sistema_pequeno_kwp'], 0)} kWp "
        f"(cerca de {fmt_reais(p['fv_preco_sistema_pequeno'])}, estimado) e pagando só com a economia do banho: "
        f"retorno em {fmt(s['fv_pequeno_payback_meses'], 0)} meses "
        f"({fmt(s['fv_pequeno_payback_meses'] / 12, 1)} anos).",
        "",
        "## Observações",
        "",
        "- Valores sem ICMS, PIS/Cofins, bandeira tarifária e iluminação pública.",
        "- Tarifa mantida constante no horizonte. Sem custo de manutenção.",
        "- Na alternativa D, o consumo da rede é o líquido depois da compensação (simplificação).",
        "- São estimativas. O resultado real depende do uso, do clima e da instalação.",
        "- Origem de cada número: `dados/premissas.csv` e `dados/FONTES.md`.",
        "",
    ]
    return "\n".join(partes)


def gerar_grafico(p, caminho):
    """Gráfico do custo acumulado em 10 anos (investimento + contas). Opcional."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    alternativas = comparar_alternativas(p)
    anos = list(range(int(p["horizonte_anos"]) + 1))
    cores = {"A": "#2a78d6", "B": "#eb6834", "C1": "#1baf7a", "C2": "#eda100", "D": "#e87ba4"}
    tracos = {"A": "-", "B": "--", "C1": "-.", "C2": ":", "D": (0, (5, 1, 1, 1, 1, 1))}

    figura, eixo = plt.subplots(figsize=(10, 5.6))
    finais = []
    for a in alternativas:
        acumulado = [a["investimento"] + a["custo_ano"] * ano for ano in anos]
        eixo.plot(anos, acumulado, color=cores[a["codigo"]], linestyle=tracos[a["codigo"]],
                  linewidth=2, label=f"{a['codigo']} - {a['nome']}")
        finais.append([acumulado[-1], a["codigo"]])

    # Rótulos no fim das linhas, afastados para não se sobreporem
    finais.sort()
    distancia_minima = max(v for v, _ in finais) * 0.045
    for i in range(1, len(finais)):
        if finais[i][0] - finais[i - 1][0] < distancia_minima:
            finais[i][0] = finais[i - 1][0] + distancia_minima
    for posicao, codigo in finais:
        eixo.annotate(codigo, (anos[-1], posicao), xytext=(6, 0),
                      textcoords="offset points", va="center", color="#333333", fontsize=10)
    eixo.set_title("Custo acumulado do banho quente (investimento + conta de luz)", loc="left")
    eixo.set_xlabel("Anos")
    eixo.set_ylabel("R$ acumulados (tarifa convencional, sem impostos)")
    eixo.set_xlim(0, anos[-1] + 0.6)
    eixo.set_ylim(bottom=0)
    eixo.grid(axis="y", color="#dddddd", linewidth=0.8)
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    eixo.legend(frameon=False, fontsize=9, loc="upper left")
    figura.text(0.01, 0.01, "Estimativa. Fonte dos dados: dados/premissas.csv. "
                "Gerado por calculos_energia.py.", fontsize=8, color="#666666")
    figura.tight_layout(rect=(0, 0.03, 1, 1))
    figura.savefig(caminho, dpi=130)
    plt.close(figura)
    return True


MARCA_INICIO = "<!-- TABELA_GERADA_INICIO (não edite: gerado por calculos_energia.py) -->"
MARCA_FIM = "<!-- TABELA_GERADA_FIM -->"


def atualizar_readme(p, caminho=PASTA / "README.md"):
    """Copia a comparação para dentro do README, entre as duas marcas.
    Assim os números do README são sempre os mesmos do código."""
    if not caminho.exists():
        return False
    texto = caminho.read_text(encoding="utf-8")
    if MARCA_INICIO not in texto or MARCA_FIM not in texto:
        return False
    corpo = texto_comparacao_md(p).split("\n", 4)[4]  # tira o título e a linha de aviso
    corpo = corpo.replace("## ", "#### ")
    antes = texto.split(MARCA_INICIO)[0]
    depois = texto.split(MARCA_FIM)[1]
    caminho.write_text(antes + MARCA_INICIO + "\n\n" + corpo.strip() + "\n\n" + MARCA_FIM + depois,
                       encoding="utf-8")
    return True


def gerar_resultados():
    """Gera resultados/comparacao.csv, comparacao.md, o gráfico e a tabela do README."""
    p = carregar_premissas()
    PASTA_RESULTADOS.mkdir(exist_ok=True)
    cenarios = [
        ("tarifa_convencional", comparar_alternativas(p)),
        ("tarifa_social", comparar_alternativas(p, tarifa_social=True)),
    ]
    salvar_csv(cenarios, PASTA_RESULTADOS / "comparacao.csv")
    (PASTA_RESULTADOS / "comparacao.md").write_text(texto_comparacao_md(p), encoding="utf-8")
    tem_grafico = gerar_grafico(p, PASTA_RESULTADOS / "grafico_custo_acumulado.png")
    atualizar_readme(p)
    return tem_grafico


if __name__ == "__main__":
    fez_grafico = gerar_resultados()
    print(texto_comparacao_md(carregar_premissas()))
    print("Arquivos gravados em:", PASTA_RESULTADOS)
    if not fez_grafico:
        print("Gráfico não gerado: matplotlib não está instalado (é opcional).")
