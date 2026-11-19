# -*- coding: utf-8 -*-
"""
Citizen Assist AI - módulo de Energia (banho quente e conta de luz)
Aluno: Gustavo Zibini Belizario - RM 561376 (FIAP, 1CC, Global Solution 2026.2)

Integração da análise de energia ao assistente.
- responder(pergunta): recebe texto livre e responde por palavras-chave (sem IA generativa).
- executar_menu(): menu numerado, usado só com o teclado.
Todos os números das respostas vêm de calculos_energia.py (nenhum é digitado no texto).
O assistente não pede e não guarda dados pessoais.
Uso:  python3 assistente_energia.py
"""

import re
import unicodedata

try:  # rodando de dentro da pasta energia/
    from calculos_energia import (analise_sensibilidade, buscar, carregar_premissas,
                                  comparar_alternativas, fmt, fmt_payback, fmt_reais,
                                  tarifa_baixa_renda, tarifa_convencional)
except ImportError:  # importado da raiz do repositório: from energia.assistente_energia import responder
    from .calculos_energia import (analise_sensibilidade, buscar, carregar_premissas,
                                   comparar_alternativas, fmt, fmt_payback, fmt_reais,
                                   tarifa_baixa_renda, tarifa_convencional)

P = carregar_premissas()  # premissas lidas de dados/premissas.csv

AVISO = ("Atenção: são estimativas. Elas dependem das premissas do projeto "
         "(dados/premissas.csv). Não há garantia de economia. "
         "Este assistente é um protótipo educacional. Não é canal oficial "
         "da Enel, da ANEEL ou do governo.")

TAMANHO_MAXIMO = 300  # caracteres aceitos em uma pergunta

# Limites aceitos na calculadora (fora disso o valor é considerado absurdo)
LIMITE_MORADORES = (1, 15)
LIMITE_MINUTOS = (1, 60)
LIMITE_POTENCIA = (1000, 9000)  # W; chuveiros comuns vão de cerca de 2000 a 7800 W


# ---------------------------------------------------------------------------
# Funções de apoio
# ---------------------------------------------------------------------------

def normalizar(texto):
    """Minúsculas e sem acentos, para comparar palavras-chave."""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def parece_dado_pessoal(texto):
    """True se o texto parece ter CPF, telefone, e-mail ou outro número longo."""
    if re.search(r"[\w.\-]+@[\w\-]+\.[\w.]+", texto):
        return True  # e-mail
    for trecho in re.findall(r"\d[\d.\-\s()/]*\d", texto):
        if len(re.sub(r"\D", "", trecho)) >= 8:
            return True  # CPF, telefone, número de conta ou instalação
    return bool(re.search(r"\b(cpf|rg)\b", normalizar(texto)))


def com_aviso(texto, fontes):
    """Junta a resposta, a fonte e o aviso padrão."""
    return f"{texto}\nFonte: {fontes} (lista em dados/FONTES.md).\n{AVISO}"


def ler_numero(texto, minimo, maximo):
    """Converte o texto em número e confere os limites.
    Devolve (numero, None) se estiver certo ou (None, mensagem) se não estiver."""
    limpo = texto.strip().replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", limpo):
        limpo = limpo.replace(".", "")  # "5.500" vira "5500"
    limpo = limpo.replace(",", ".")
    try:
        numero = float(limpo)
    except ValueError:
        return None, "Não entendi. Digite só o número, por exemplo 4."
    if numero != numero or numero in (float("inf"), float("-inf")):
        return None, "Não entendi. Digite só o número, por exemplo 4."
    if numero < minimo or numero > maximo:
        return None, f"Digite um número entre {fmt(minimo, 0)} e {fmt(maximo, 0)}."
    return numero, None


# ---------------------------------------------------------------------------
# Respostas das perguntas frequentes (números calculados na hora)
# ---------------------------------------------------------------------------

def resposta_gasto():
    a = buscar(comparar_alternativas(P), "A")
    texto = (
        f"Um chuveiro elétrico de {fmt(P['potencia_chuveiro_w'], 0)} W é um dos aparelhos que mais gastam.\n"
        f"Exemplo: família de {fmt(P['moradores'], 0)} pessoas, 1 banho por dia, "
        f"{fmt(P['minutos_banho_base'], 0)} minutos cada.\n"
        f"Consumo: {fmt(a['consumo_kwh_mes'])} kWh por mês ({fmt(a['consumo_kwh_ano'])} kWh por ano).\n"
        f"Custo: {fmt_reais(a['custo_mes'])} por mês ({fmt_reais(a['custo_ano'])} por ano), "
        f"na tarifa da Enel SP de {fmt(tarifa_convencional(P), 5)} R$/kWh sem impostos.\n"
        "Conta: energia (kWh) = potência (kW) x horas de uso.\n"
        "Use a calculadora (opção 7) para ver o seu caso.")
    return com_aviso(texto, "F1 (tarifa ANEEL/Enel SP), F4 (potência Lorenzetti)")


def resposta_economizar():
    lista = comparar_alternativas(P)
    a, b = buscar(lista, "A"), buscar(lista, "B")
    reducao = (1 - b["consumo_kwh_mes"] / a["consumo_kwh_mes"]) * 100
    texto = (
        "Dá para economizar sem gastar nada:\n"
        f"1. Banho de {fmt(P['minutos_banho_eficiente'], 0)} minutos em vez de "
        f"{fmt(P['minutos_banho_base'], 0)}.\n"
        f"2. Chave na posição verão nos {fmt(P['meses_quentes_ano'], 0)} meses mais quentes "
        f"(economia de até {fmt(P['reducao_posicao_verao'] * 100, 0)}% enquanto estiver nela).\n"
        "3. Desligue o chuveiro enquanto se ensaboa.\n"
        f"Resultado estimado para {fmt(P['moradores'], 0)} pessoas: o consumo cai de "
        f"{fmt(a['consumo_kwh_mes'])} para {fmt(b['consumo_kwh_mes'])} kWh por mês "
        f"(menos {fmt(reducao, 0)}%).\n"
        f"Economia: {fmt_reais(b['economia_mes'])} por mês, ou {fmt_reais(b['economia_ano'])} por ano.\n"
        "Cuidado: nunca mexa na chave com o chuveiro ligado ou com o corpo molhado.")
    return com_aviso(texto, "F5 (dicas Cemig), F4 (potências Lorenzetti), F1 (tarifa)")


def resposta_solar():
    lista = comparar_alternativas(P)
    c1, c2 = buscar(lista, "C1"), buscar(lista, "C2")
    s = analise_sensibilidade(P)
    texto = (
        "O aquecedor solar esquenta a água com o sol. O chuveiro fica de apoio nos dias sem sol.\n"
        f"Aquecedor comercial (placa de {fmt(P['solar_comercial_area_m2'], 1)} m² e caixa de 200 L):\n"
        f"- custa cerca de {fmt_reais(c1['investimento'])} instalado;\n"
        f"- economiza cerca de {fmt_reais(c1['economia_mes'])} por mês;\n"
        f"- se paga em {fmt_payback(c1)}.\n"
        "Aquecedor de baixo custo (ASBC, montado com tubos de plástico):\n"
        f"- custa cerca de {fmt_reais(c2['investimento'])} em material;\n"
        f"- economiza cerca de {fmt_reais(c2['economia_mes'])} por mês;\n"
        f"- se paga em {fmt_payback(c2)}.\n"
        "Vale a pena se você mora em casa própria, com telhado ou laje com sol e caixa d'água.\n"
        "Em casa alugada, converse antes com o dono do imóvel.\n"
        f"No inverno o sol rende menos: o comercial cobre no máximo {fmt(s['fracao_maxima_inverno'] * 100, 0)}% "
        "do banho nessa época.\n"
        f"Se o sistema render só o mínimo da Lei Solar de SP, o retorno passa para "
        f"{fmt_payback(s['c1_fracao_minima'])}.")
    return com_aviso(texto, "F7 (preço SINAPI), F8 (Lei Solar SP), F9 (estudo de desempenho), "
                            "F10 (ASBC), F6 (irradiação em SP)")


def resposta_fotovoltaica():
    lista = comparar_alternativas(P)
    d, c2 = buscar(lista, "D"), buscar(lista, "C2")
    s = analise_sensibilidade(P)
    texto = (
        "Placa fotovoltaica gera eletricidade. A energia que sobra vira crédito na conta (compensação).\n"
        f"Para cobrir só o banho do exemplo seriam cerca de {fmt(s['fv_kwp'], 2)} kWp.\n"
        f"Com preço de sistema pequeno, custaria cerca de {fmt_reais(d['investimento'])} "
        f"e se pagaria em {fmt_payback(d)}.\n"
        f"Na conta mais otimista (preço de sistema maior) seria {fmt_reais(s['fv_investimento_otimista'])}.\n"
        f"Mas quase não se vende sistema tão pequeno. Um de {fmt(P['fv_potencia_sistema_pequeno_kwp'], 0)} kWp "
        f"custa cerca de {fmt_reais(P['fv_preco_sistema_pequeno'])}.\n"
        f"Pago só com a economia do banho, levaria {fmt(s['fv_pequeno_payback_meses'] / 12, 1)} anos.\n"
        "Precisa de telhado próprio, projeto, pedido à Enel e manutenção.\n"
        "A conta ainda tem cobranças mínimas que os créditos não zeram.\n"
        "Para quem tem Tarifa Social, os primeiros 80 kWh já são gratuitos, então o crédito vale menos.\n"
        f"Para o banho, o aquecedor solar de água costuma ser mais barato: o ASBC custa "
        f"{fmt_reais(c2['investimento'])}.")
    return com_aviso(texto, "F11 e F12 (preços de sistemas), F6 (irradiação), F1 (tarifa e Tarifa Social)")


def resposta_tarifa_social():
    social = comparar_alternativas(P, tarifa_social=True)
    a = buscar(social, "A")
    texto = (
        "A Tarifa Social dá desconto na conta de luz para famílias de baixa renda.\n"
        f"Regra atual: os primeiros {fmt(P['franquia_tarifa_social_kwh'], 0)} kWh do mês são gratuitos. "
        "O que passar disso é pago.\n"
        "Quem tem direito à gratuidade:\n"
        "- família no CadÚnico com renda de até meio salário mínimo por pessoa;\n"
        "- idoso (65+) ou pessoa com deficiência que recebe o BPC;\n"
        "- famílias indígenas e quilombolas no CadÚnico.\n"
        "Renda entre meio e 1 salário mínimo por pessoa, com consumo até 120 kWh: "
        "desconto social menor (cerca de 11,8%).\n"
        "O desconto é automático se o CadÚnico estiver atualizado.\n"
        "A conta de luz precisa estar no nome de alguém da família, no endereço do cadastro.\n"
        "Procure o CRAS da sua região para se cadastrar ou atualizar.\n"
        f"Atenção: o banho de {fmt(P['moradores'], 0)} pessoas gasta {fmt(a['consumo_kwh_mes'])} kWh por mês, "
        f"mais do que os {fmt(P['franquia_tarifa_social_kwh'], 0)} kWh gratuitos.\n"
        f"Com a Tarifa Social, o banho ainda pode custar cerca de {fmt_reais(a['custo_mes'])} por mês "
        f"(excedente a {fmt(tarifa_baixa_renda(P), 5)} R$/kWh sem impostos).\n"
        "Por isso economizar no banho continua valendo a pena.")
    return com_aviso(texto, "F1 (ANEEL, REH 3.596/2026), F2 (governo federal), F14 (Lei 15.235/2025)")


def resposta_co2():
    lista = comparar_alternativas(P)
    a = buscar(lista, "A")
    linhas = [
        "A energia do Brasil é quase toda renovável, então o banho emite pouco CO2.\n"
        f"Fator usado: {fmt(P['fator_emissao_kg_kwh'] * 1000, 1)} kg de CO2 por MWh (MCTI).\n"
        f"Banho do exemplo: {fmt(a['co2_ano'])} kg de CO2 por ano.\n"
        "CO2 evitado por ano:"]
    for codigo in ("B", "C1", "C2", "D"):
        alt = buscar(lista, codigo)
        linhas.append(f"- {alt['nome']}: {fmt(alt['co2_evitado_ano'])} kg")
    linhas.append("O maior ganho é no bolso. Mas economizar também alivia a rede no horário de pico.")
    return com_aviso("\n".join(linhas), "F3 (fator de emissão do SIN, MCTI)")


def resposta_fontes():
    texto = (
        "Principais fontes:\n"
        "- Tarifa: ANEEL, Resolução Homologatória 3.596/2026 da Enel SP (F1).\n"
        "- Tarifa Social: governo federal (F2) e ANEEL (F1).\n"
        "- CO2: fator de emissão do MCTI (F3).\n"
        "- Sol em São Paulo: Atlas Brasileiro de Energia Solar, INPE (F6).\n"
        "- Preços de aquecedor: SINAPI (F7) e Fundação Banco do Brasil (F10).\n"
        "Limitações:\n"
        "- Valores sem impostos e sem bandeira tarifária. A conta real é maior.\n"
        "- Tempo de banho, número de banhos e parte do sol aproveitada são estimativas.\n"
        "- Os preços mudam com o tempo e com a loja.")
    return com_aviso(texto, "dados/premissas.csv")


def resposta_ajuda():
    return ("Olá! Eu explico o gasto do banho quente na conta de luz.\n"
            "Pergunte, por exemplo:\n"
            "- Quanto gasta o chuveiro?\n"
            "- Como economizar no banho?\n"
            "- Vale a pena aquecedor solar?\n"
            "- O que é a Tarifa Social?\n"
            "- Quanto CO2 eu evito?\n"
            "- Calcular 4 pessoas 8 minutos 5500 W")


FORA_DO_ESCOPO = ("Desculpe, não entendi ou esse assunto está fora do que eu sei.\n"
                  "Eu falo sobre: gasto do chuveiro, como economizar, aquecedor solar, "
                  "energia fotovoltaica, Tarifa Social e CO2.\n"
                  "Digite 'ajuda' para ver exemplos.")

AVISO_DADOS_PESSOAIS = ("Por segurança, não digite CPF, telefone, e-mail, endereço "
                        "ou número da conta de luz. Eu não preciso desses dados e não guardo nada.\n"
                        "Faça a pergunta de novo sem eles.")

# Palavras-chave de cada assunto (sem acento e em minúsculas)
ASSUNTOS = [
    ("tarifa_social", ["tarifa social", "cadunico", "cad unico", "baixa renda", "luz do povo",
                       "gratuidade", "gratis", "desconto", "bpc", "direito"], resposta_tarifa_social),
    ("fotovoltaica", ["fotovoltaic", "painel solar", "paineis", "placa solar", "placas",
                      "gerar energia", "energia solar", "compensacao"], resposta_fotovoltaica),
    ("solar", ["aquecedor", "aquecimento solar", "solar", "asbc", "boiler", "baixo custo"],
     resposta_solar),
    ("economizar", ["economizar", "economia", "economizo", "reduzir", "diminuir", "dica",
                    "posicao verao", "verao", "menos", "poupar"], resposta_economizar),
    ("co2", ["co2", "carbono", "emiss", "meio ambiente", "poluic", "planeta", "sustentav"],
     resposta_co2),
    ("gasto", ["quanto gasta", "gasta", "gasto", "consumo", "consome", "kwh", "custa", "chuveiro",
               "conta de luz"], resposta_gasto),
    ("fontes", ["fonte", "referencia", "limitac", "de onde"], resposta_fontes),
    ("ajuda", ["ajuda", "oi", "ola", "bom dia", "boa tarde", "boa noite", "menu", "help"],
     resposta_ajuda),
]


def identificar_assunto(pergunta):
    """Conta as palavras-chave de cada assunto e devolve o que tiver mais acertos.
    Em empate vale a ordem da lista. Devolve None se nada combinar."""
    texto = " " + re.sub(r"[^a-z0-9 ]", " ", normalizar(pergunta)) + " "
    melhor, melhor_pontos = None, 0
    for nome, palavras, _ in ASSUNTOS:
        pontos = 0
        for palavra in palavras:
            # palavras curtas (como "oi") só valem como palavra inteira
            alvo = f" {palavra} " if len(palavra) <= 3 else palavra
            if alvo in texto:
                pontos += 1
        if pontos > melhor_pontos:
            melhor, melhor_pontos = nome, pontos
    return melhor


# ---------------------------------------------------------------------------
# Calculadora do caso da pessoa
# ---------------------------------------------------------------------------

def calcular_caso(moradores, minutos, potencia_w, ja_usa_verao=False, tarifa_social=False):
    """Monta a resposta da calculadora com as alternativas para o caso informado."""
    lista = comparar_alternativas(P, moradores=moradores, minutos=minutos, potencia_w=potencia_w,
                                  ja_usa_verao=ja_usa_verao, tarifa_social=tarifa_social)
    a = buscar(lista, "A")
    tarifa = "Tarifa Social (só o que passa de 80 kWh)" if tarifa_social else "tarifa residencial comum"
    linhas = [
        f"Seu caso: {fmt(moradores, 0)} pessoa(s), banho de {fmt(minutos, 0)} min, "
        f"chuveiro de {fmt(potencia_w, 0)} W, {tarifa}.",
        f"Hoje o banho gasta cerca de {fmt(a['consumo_kwh_mes'])} kWh por mês.",
        f"Custo estimado: {fmt_reais(a['custo_mes'])} por mês ({fmt_reais(a['custo_ano'])} por ano).",
        "",
        "Comparação das alternativas:",
    ]
    for codigo in ("B", "C1", "C2", "D"):
        alt = buscar(lista, codigo)
        linhas.append(
            f"- {alt['nome']}: economia de {fmt_reais(alt['economia_mes'])}/mês; "
            f"investimento {fmt_reais(alt['investimento'])}; retorno: {fmt_payback(alt)}; "
            f"CO2 evitado {fmt(alt['co2_evitado_ano'])} kg/ano.")
    linhas += [
        "",
        "Recomendação:",
        "1. Comece pelos hábitos (B): não custa nada.",
        "2. Casa própria com sol no telhado e caixa d'água: avalie o aquecedor solar (C2 ou C1).",
        "3. Placa fotovoltaica (D) pede telhado próprio e mais dinheiro. O valor acima supõe "
        "comprar só a parte que o banho usa.",
        f"   Na prática o menor sistema comum ({fmt(P['fv_potencia_sistema_pequeno_kwp'], 0)} kWp) "
        f"custa cerca de {fmt_reais(P['fv_preco_sistema_pequeno'])}. Veja a opção 4 do menu.",
    ]
    limite = P["horizonte_anos"] * 12
    for codigo in ("C1", "C2", "D"):
        alt = buscar(lista, codigo)
        if alt["payback_meses"] is None or alt["payback_meses"] > limite:
            linhas.append(f"Neste caso, '{alt['nome']}' leva mais de "
                          f"{fmt(P['horizonte_anos'], 0)} anos para se pagar. Não compensa.")
    if tarifa_social:
        linhas.append(f"Premissa: o resto da casa já usa {fmt(P['outros_consumos_casa_kwh'], 0)} kWh "
                      "por mês, então os 80 kWh gratuitos já foram usados.")
    if a["custo_mes"] <= 0:
        linhas.append("Neste caso o banho cabe na parte gratuita, então não há economia em reais.")
    return com_aviso("\n".join(linhas), "F1 (tarifa), F4 e F5 (chuveiro), F6 a F12 (alternativas)")


def calcular_do_texto(pergunta):
    """Tenta achar moradores, minutos e watts no texto livre.
    Ex.: 'calcular 4 pessoas 8 minutos 5500 W'. Devolve None se faltar algo."""
    texto = normalizar(pergunta)
    # "4 pessoas", "4 moradores", "somos 4", "4 em casa" (ajuste após o teste simulado)
    achou_pessoas = (re.search(r"(-?\d+)\s*(pessoas?|moradores?)", texto)
                     or re.search(r"somos\s*(-?\d+)", texto)
                     or re.search(r"(-?\d+)\s*em casa", texto))
    achou_minutos = re.search(r"(-?\d+)\s*(min|minutos?)\b", texto)
    achou_watts = re.search(r"(-?\d[\d.]*)\s*(w|watts?)\b", texto)
    if not (achou_pessoas and achou_minutos):
        return None
    moradores, erro1 = ler_numero(achou_pessoas.group(1), *LIMITE_MORADORES)
    minutos, erro2 = ler_numero(achou_minutos.group(1), *LIMITE_MINUTOS)
    potencia = P["potencia_chuveiro_w"]
    erro3 = None
    if achou_watts:
        potencia, erro3 = ler_numero(achou_watts.group(1), *LIMITE_POTENCIA)
    if erro1 or erro2 or erro3:
        return ("Algum número ficou fora do esperado. Use de 1 a 15 pessoas, "
                "de 1 a 60 minutos e de 1.000 a 9.000 W.")
    return calcular_caso(moradores, minutos, potencia)


# ---------------------------------------------------------------------------
# Entrada principal por texto livre
# ---------------------------------------------------------------------------

def responder(pergunta):
    """Responde uma pergunta em texto livre. Nunca levanta erro para o usuário."""
    if pergunta is None or not str(pergunta).strip():
        return "Você não digitou nada. Escreva sua pergunta, por exemplo: quanto gasta o chuveiro?"
    pergunta = str(pergunta)
    if len(pergunta) > TAMANHO_MAXIMO:
        return (f"Sua mensagem é muito longa. Escreva em até {TAMANHO_MAXIMO} caracteres, "
                "com uma pergunta por vez.")
    if parece_dado_pessoal(pergunta):
        return AVISO_DADOS_PESSOAIS
    # Pergunta com número de pessoas e minutos vai direto para a calculadora,
    # mesmo sem a palavra "calcular" (ajuste após o teste simulado com personas).
    if re.search(r"\d", pergunta):
        resultado = calcular_do_texto(pergunta)
        if resultado:
            return resultado
    if re.search(r"calcul|simul|meu caso", normalizar(pergunta)):
        resultado = calcular_do_texto(pergunta)
        if resultado:
            return resultado
        return ("Para calcular, use a opção 7 do menu ou escreva assim: "
                "calcular 4 pessoas 8 minutos 5500 W.")
    # Pergunta sobre CO2 vai para CO2 mesmo citando o aquecedor solar
    # (ajuste após o teste simulado com personas).
    if re.search(r"co2|carbono|emiss", normalizar(pergunta)):
        return resposta_co2()
    assunto = identificar_assunto(pergunta)
    for nome, _, funcao in ASSUNTOS:
        if nome == assunto:
            return funcao()
    return FORA_DO_ESCOPO


# ---------------------------------------------------------------------------
# Menu por teclado
# ---------------------------------------------------------------------------

MENU = """
===== Citizen Assist AI - Energia: banho quente e conta de luz =====
1 - Quanto gasta o chuveiro elétrico?
2 - Como economizar sem gastar nada?
3 - Vale a pena aquecedor solar de água?
4 - E a energia solar fotovoltaica (placas de luz)?
5 - O que é a Tarifa Social e quem tem direito?
6 - Quanto CO2 dá para evitar?
7 - Calculadora: o meu caso
8 - Fazer uma pergunta com minhas palavras
9 - Fontes e limitações
0 - Sair"""

TENTATIVAS = 3


def perguntar_numero(entrada, saida, mensagem, minimo, maximo, padrao):
    """Pede um número até 3 vezes. Enter vazio usa o valor padrão."""
    for _ in range(TENTATIVAS):
        texto = entrada(mensagem)
        if not texto.strip():
            return padrao
        if parece_dado_pessoal(texto):
            saida(AVISO_DADOS_PESSOAIS)
            continue
        numero, erro = ler_numero(texto, minimo, maximo)
        if erro is None:
            return numero
        saida(erro)
    saida(f"Vou usar o valor padrão: {fmt(padrao, 0)}.")
    return padrao


def perguntar_opcao(entrada, saida, mensagem, opcoes, padrao):
    """Pede uma opção da lista até 3 vezes. Enter vazio usa o padrão."""
    for _ in range(TENTATIVAS):
        texto = normalizar(entrada(mensagem))
        if not texto:
            return padrao
        if texto in opcoes:
            return texto
        saida("Opção inválida. Digite um dos números mostrados.")
    saida("Vou usar a opção padrão.")
    return padrao


def executar_calculadora(entrada, saida):
    """Fluxo da calculadora, passo a passo."""
    saida("\nCalculadora do banho. Não precisa informar nome nem dados pessoais.")
    saida("Aperte Enter para usar o valor do exemplo.")
    moradores = perguntar_numero(entrada, saida, "Quantas pessoas tomam banho na casa? [4] ",
                                 *LIMITE_MORADORES, P["moradores"])
    minutos = perguntar_numero(entrada, saida, "Quantos minutos dura cada banho, em média? [10] ",
                               *LIMITE_MINUTOS, P["minutos_banho_base"])
    saida("Como o chuveiro costuma ficar?")
    saida("1 - Posição inverno / mais quente")
    saida("2 - Posição verão / morno")
    saida("3 - Sei a potência em watts (está na embalagem ou na etiqueta)")
    saida("4 - Não sei")
    opcao = perguntar_opcao(entrada, saida, "Escolha [4]: ", ["1", "2", "3", "4"], "4")
    potencia = P["potencia_chuveiro_w"]
    ja_usa_verao = False
    if opcao == "2":
        potencia = P["potencia_chuveiro_w"] * (1 - P["reducao_posicao_verao"])
        ja_usa_verao = True
    elif opcao == "3":
        potencia = perguntar_numero(entrada, saida, "Potência em W (ex.: 5500): ",
                                    *LIMITE_POTENCIA, P["potencia_chuveiro_w"])
    social = perguntar_opcao(entrada, saida,
                             "A família recebe a Tarifa Social? 1 - sim, 2 - não, 3 - não sei [3]: ",
                             ["1", "2", "3"], "3")
    saida("")
    saida(calcular_caso(moradores, minutos, potencia, ja_usa_verao, tarifa_social=(social == "1")))
    if social == "3":
        saida("Dica: veja a opção 5 para saber se a família tem direito à Tarifa Social.")


def executar_menu(entrada=input, saida=print):
    """Laço principal do menu. 'entrada' e 'saida' podem ser trocadas nos testes."""
    respostas = {"1": resposta_gasto, "2": resposta_economizar, "3": resposta_solar,
                 "4": resposta_fotovoltaica, "5": resposta_tarifa_social, "6": resposta_co2,
                 "9": resposta_fontes}
    saida(AVISO)
    while True:
        saida(MENU)
        try:
            opcao = entrada("Digite o número da opção: ").strip()
            if opcao == "0":
                saida("Até logo! Lembre: um banho mais curto já ajuda.")
                return
            if opcao in respostas:
                saida("\n" + respostas[opcao]())
            elif opcao == "7":
                executar_calculadora(entrada, saida)
            elif opcao == "8":
                saida("\n" + responder(entrada("Escreva sua pergunta: ")))
            else:
                saida("Opção inválida. Digite um número de 0 a 9.")
        except (EOFError, KeyboardInterrupt):
            saida("\nEncerrando o assistente. Até logo!")
            return


if __name__ == "__main__":
    executar_menu()
