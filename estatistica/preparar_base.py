# -*- coding: utf-8 -*-
"""
Global Solution 2026.2 - CitizenTech - Projeto Citizen Assist AI
Aluno: Gustavo Zibini Belizario - RM 561376

preparar_base.py
Gera o arquivo base_dados.csv a partir do arquivo original do
Atlas do Desenvolvimento Humano no Brasil 2013 (PNUD, Ipea e FJP),
redistribuído no pacote abjData (https://github.com/abjur/abjData).

O script NÃO altera nenhum valor: apenas filtra o ano de 2010 e
seleciona as colunas usadas na análise.

Uso:  python preparar_base.py
Requer: pip install pyreadr pandas
"""

import pyreadr

ARQUIVO_ORIGINAL = "dados_brutos/pnud_muni.rda"
ARQUIVO_SAIDA = "base_dados.csv"

# Colunas mantidas (nomes originais do Atlas)
COLUNAS = [
    "codmun7",       # código IBGE do município (7 dígitos)
    "municipio",     # nome do município
    "ufn",           # nome da unidade da federação
    "pop",           # população em domicílios particulares permanentes
    "espvida",       # esperança de vida ao nascer (anos)
    "e_anosestudo",  # expectativa de anos de estudo aos 18 anos (anos)
    "t_analf18m",    # taxa de analfabetismo, 18 anos ou mais (%)
    "rdpc",          # renda per capita média (R$ de ago/2010)
    "gini",          # índice de Gini (0 a 1)
    "pmpob",         # % de pobres (renda per capita <= R$ 140)
    "t_agua",        # % da população em domicílios com água encanada
    "t_banagua",     # % em domicílios com banheiro e água encanada
    "t_lixo",        # % em domicílios urbanos com coleta de lixo
    "t_luz",         # % em domicílios com energia elétrica
    "t_des",         # taxa de desocupação, 10 anos ou mais (%)
    "idhm",          # Índice de Desenvolvimento Humano Municipal (0 a 1)
]

# 1) Lê o arquivo original (16.695 linhas = 5.565 municípios x 3 censos)
dados = pyreadr.read_r(ARQUIVO_ORIGINAL)["pnud_muni"]
print("Arquivo original:", dados.shape[0], "linhas x", dados.shape[1], "colunas")

# 2) Mantém só o Censo de 2010 e as colunas escolhidas
base = dados[dados["ano"] == 2010][COLUNAS]
print("Após filtrar ano == 2010:", base.shape[0], "municípios")

# 3) Valores ausentes: se existirem, as linhas são removidas (nada é preenchido)
ausentes = int(base.isna().sum().sum())
linhas_antes = len(base)
base = base.dropna()
print("Valores ausentes encontrados:", ausentes)
print("Linhas removidas por valor ausente:", linhas_antes - len(base))

# 4) Salva em CSV (separador vírgula, UTF-8)
base.to_csv(ARQUIVO_SAIDA, index=False, sep=",", encoding="utf-8")
print("Arquivo gerado:", ARQUIVO_SAIDA, "-", base.shape[0], "linhas x", base.shape[1], "colunas")
