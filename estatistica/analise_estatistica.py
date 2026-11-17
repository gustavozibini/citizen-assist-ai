# -*- coding: utf-8 -*-
"""
FIAP - Global Solution 2026.2 - Desafio CitizenTech
Projeto: Citizen Assist AI
Avaliação de Estatística com Python

Aluno: Gustavo Zibini Belizario
Matrícula (RM): 561376

Base de dados: base_dados.csv
  Atlas do Desenvolvimento Humano no Brasil 2013 (PNUD, Ipea e FJP),
  indicadores municipais do Censo Demográfico 2010 (IBGE) - 5.565 municípios.

Como executar:
  pip install pandas numpy scipy statsmodels scikit-learn matplotlib seaborn
  python analise_estatistica.py

O script responde às questões 02 a 06 na ordem do enunciado, imprime os
resultados no terminal, salva os gráficos na pasta figuras/ e grava todos
os números em resultados.json (usado para montar o relatório em PDF).
"""

import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # salva os gráficos em arquivo, sem abrir janela
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

# ----------------------------------------------------------------------
# Configurações gerais
# ----------------------------------------------------------------------
SEMENTE = 561376          # semente aleatória fixa (o RM do aluno)
PASTA_FIGURAS = "figuras"
os.makedirs(PASTA_FIGURAS, exist_ok=True)

AZUL = "#2a78d6"
LARANJA = "#eb6834"
CINZA = "#52514e"
sns.set_theme(style="whitegrid")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 150

# Nome "legível" de cada variável usada (para títulos e eixos dos gráficos)
ROTULOS = {
    "t_analf18m": "Taxa de analfabetismo, 18 anos ou mais (%)",
    "e_anosestudo": "Expectativa de anos de estudo (anos)",
    "pmpob": "Proporção de pobres (%)",
    "t_banagua": "População com banheiro e água encanada (%)",
    "t_luz": "População com energia elétrica (%)",
    "idhm": "IDHM",
}

# Nomes curtos (para gráficos com pouco espaço)
ROTULOS_CURTOS = {
    "t_analf18m": "Analfabetismo (%)",
    "pmpob": "Pobres (%)",
    "t_banagua": "Banheiro e água (%)",
    "t_luz": "Energia elétrica (%)",
}

resultados = {}  # dicionário com todos os números, salvo em JSON no final


def titulo(texto):
    """Imprime um título de seção no terminal."""
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def texto_p(p):
    """Formata um p-valor (valores minúsculos aparecem como '< 0,001')."""
    if p < 0.001:
        return "< 0,001"
    return "%.4f" % p


def classificar_evento(p):
    """Classifica um evento pela sua probabilidade (escala usada no relatório)."""
    p = round(p, 4)
    if p == 0:
        return "evento impossível"
    if p == 1:
        return "evento certo"
    if p == 0.5:
        return "evento equiprovável (tão provável quanto não ocorrer)"
    if p < 0.5:
        return "evento pouco provável"
    return "evento provável"


def forca_correlacao(r):
    """Descreve em palavras a força e o sentido de uma correlação de Pearson."""
    a = abs(r)
    if a < 0.3:
        forca = "fraca"
    elif a < 0.7:
        forca = "moderada"
    elif a < 0.9:
        forca = "forte"
    else:
        forca = "muito forte"
    sentido = "positiva" if r > 0 else "negativa"
    return forca + " e " + sentido


# ----------------------------------------------------------------------
# QUESTÃO 01 - Leitura da base de dados
# ----------------------------------------------------------------------
titulo("QUESTÃO 01 - BASE DE DADOS")
df = pd.read_csv("base_dados.csv")
print("Linhas (municípios):", df.shape[0], "| Colunas:", df.shape[1])
print("Valores ausentes na base:", int(df.isna().sum().sum()))

colunas_numericas = ["pop", "espvida", "e_anosestudo", "t_analf18m", "rdpc", "gini",
                     "pmpob", "t_agua", "t_banagua", "t_lixo", "t_luz", "t_des", "idhm"]
descritivas = df[colunas_numericas].describe().T
descritivas["mediana"] = df[colunas_numericas].median()
descritivas["assimetria"] = df[colunas_numericas].skew()
print("\nEstatísticas descritivas:")
print(descritivas[["mean", "std", "min", "mediana", "max", "assimetria"]].round(3))

resultados["q01"] = {
    "n_linhas": int(df.shape[0]),
    "n_colunas": int(df.shape[1]),
    "ausentes": int(df.isna().sum().sum()),
    "descritivas": {
        col: {
            "media": float(descritivas.loc[col, "mean"]),
            "desvio": float(descritivas.loc[col, "std"]),
            "minimo": float(descritivas.loc[col, "min"]),
            "mediana": float(descritivas.loc[col, "mediana"]),
            "maximo": float(descritivas.loc[col, "max"]),
            "assimetria": float(descritivas.loc[col, "assimetria"]),
        }
        for col in colunas_numericas
    },
}

# ----------------------------------------------------------------------
# QUESTÃO 02 - Probabilidades com a distribuição normal
# Variável: taxa de analfabetismo (18 anos ou mais)
# ----------------------------------------------------------------------
titulo("QUESTÃO 02 - PROBABILIDADE (DISTRIBUIÇÃO NORMAL)")
var2 = "t_analf18m"
x2 = df[var2]

media2 = x2.mean()
mediana2 = x2.median()
desvio2 = x2.std(ddof=0)   # desvio padrão populacional (todos os municípios)

print("Variável:", var2, "-", ROTULOS[var2])
print("Média = %.4f | Mediana = %.4f | Desvio padrão = %.4f" % (media2, mediana2, desvio2))

# 02A) P(X < média), com X ~ Normal(média, desvio)
p_2a = stats.norm.cdf(media2, loc=media2, scale=desvio2)
class_2a = classificar_evento(p_2a)
print("\n02A) P(X < média) = P(X < %.4f) = %.4f (%.2f%%)" % (media2, p_2a, 100 * p_2a))
print("     Classificação:", class_2a)

# 02B) P(X > mediana) = 1 - P(X <= mediana)
z_2b = (mediana2 - media2) / desvio2
p_2b = 1 - stats.norm.cdf(mediana2, loc=media2, scale=desvio2)
class_2b = classificar_evento(p_2b)
print("\n02B) z da mediana = (%.4f - %.4f) / %.4f = %.4f" % (mediana2, media2, desvio2, z_2b))
print("     P(X > mediana) = P(X > %.4f) = %.4f (%.2f%%)" % (mediana2, p_2b, 100 * p_2b))
print("     Classificação:", class_2b)

# Proporção realmente observada nos dados (só para comparar com o modelo normal)
obs_menor_media = (x2 < media2).mean()
obs_maior_mediana = (x2 > mediana2).mean()
print("\nComparação com os dados reais (sem supor normalidade):")
print("     Proporção de municípios abaixo da média  = %.4f" % obs_menor_media)
print("     Proporção de municípios acima da mediana = %.4f" % obs_maior_mediana)

# Gráfico: histograma + curva normal, com as duas áreas pintadas
eixo = np.linspace(media2 - 4 * desvio2, media2 + 4 * desvio2, 400)
curva = stats.norm.pdf(eixo, media2, desvio2)
fig, eixos = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
for ax, limite, lado, prob, nome in [
    (eixos[0], media2, "menor", p_2a, "02A) P(X < média)"),
    (eixos[1], mediana2, "maior", p_2b, "02B) P(X > mediana)"),
]:
    ax.hist(x2, bins=40, density=True, color="#c9c8c2", edgecolor="white", label="Dados (histograma)")
    ax.plot(eixo, curva, color=AZUL, linewidth=2, label="Curva normal")
    if lado == "menor":
        area = eixo <= limite
    else:
        area = eixo >= limite
    ax.fill_between(eixo[area], curva[area], color=AZUL, alpha=0.35, label="Área = %.4f" % prob)
    ax.axvline(limite, color=LARANJA, linestyle="--", linewidth=2, label="Limite = %.2f" % limite)
    ax.set_title(nome + " = %.4f" % prob)
    ax.set_xlabel(ROTULOS[var2])
    ax.legend(fontsize=9)
eixos[0].set_ylabel("Densidade de probabilidade")
fig.suptitle("Questão 02 - Distribuição normal ajustada à taxa de analfabetismo", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q02_distribuicao_normal.png"))
plt.close(fig)

resultados["q02"] = {
    "variavel": var2, "rotulo": ROTULOS[var2],
    "media": float(media2), "mediana": float(mediana2), "desvio_pop": float(desvio2),
    "assimetria": float(x2.skew()),
    "a_prob": float(p_2a), "a_classificacao": class_2a,
    "b_z": float(z_2b), "b_prob": float(p_2b), "b_classificacao": class_2b,
    "obs_menor_media": float(obs_menor_media), "obs_maior_mediana": float(obs_maior_mediana),
}

# ----------------------------------------------------------------------
# QUESTÃO 03 - Teste de hipótese para a média (teste z)
# Variável: expectativa de anos de estudo
# ----------------------------------------------------------------------
titulo("QUESTÃO 03 - TESTE DE HIPÓTESE PARA A MÉDIA (TESTE Z)")
var3 = "e_anosestudo"
x3 = df[var3]

mu0 = x3.mean()            # média populacional de referência (todos os municípios)
sigma = x3.std(ddof=0)     # desvio padrão populacional dos dados
print("Variável:", var3, "-", ROTULOS[var3])
print("Média populacional de referência (mu0) = %.4f" % mu0)
print("Desvio padrão populacional (sigma)     = %.4f" % sigma)


def teste_z(amostra, mu0, sigma, alfa, lado):
    """Teste z unilateral para a média. lado = 'esquerda' ou 'direita'."""
    n = len(amostra)
    media_amostral = amostra.mean()
    erro_padrao = sigma / np.sqrt(n)
    z = (media_amostral - mu0) / erro_padrao
    if lado == "esquerda":
        z_critico = stats.norm.ppf(alfa)        # valor negativo
        p_valor = stats.norm.cdf(z)
        rejeita = z < z_critico
    else:
        z_critico = stats.norm.ppf(1 - alfa)    # valor positivo
        p_valor = 1 - stats.norm.cdf(z)
        rejeita = z > z_critico
    return {
        "n": int(n), "alfa": alfa, "lado": lado,
        "media_amostral": float(media_amostral), "erro_padrao": float(erro_padrao),
        "z": float(z), "z_critico": float(z_critico), "p_valor": float(p_valor),
        "rejeita_h0": bool(rejeita),
    }


# 03A) H1: média < mu0 | alfa = 6% | n = 20
amostra_a = x3.sample(n=20, random_state=SEMENTE)
t3a = teste_z(amostra_a, mu0, sigma, alfa=0.06, lado="esquerda")
print("\n03A) Teste unilateral à esquerda | alfa = 6% | n = 20")
print("     H0: mu = %.4f   contra   H1: mu < %.4f" % (mu0, mu0))
print("     Média amostral = %.4f | Erro padrão = %.4f" % (t3a["media_amostral"], t3a["erro_padrao"]))
print("     z calculado = %.4f | z crítico = %.4f | p-valor = %.4f"
      % (t3a["z"], t3a["z_critico"], t3a["p_valor"]))
if t3a["rejeita_h0"]:
    t3a["decisao"] = "Rejeita-se H0"
    t3a["conclusao"] = ("ao nível de 6%, há evidência de que a média do grupo amostrado "
                        "é menor do que a média de referência.")
else:
    t3a["decisao"] = "Não se rejeita H0"
    t3a["conclusao"] = ("ao nível de 6%, não há evidência suficiente de que a média do grupo "
                        "amostrado seja menor do que a média de referência.")
print("     Decisão:", t3a["decisao"], "-", t3a["conclusao"])

# 03B) H1: média > mu0 | alfa = 9% | n = 25
amostra_b = x3.sample(n=25, random_state=SEMENTE + 1)
t3b = teste_z(amostra_b, mu0, sigma, alfa=0.09, lado="direita")
print("\n03B) Teste unilateral à direita | alfa = 9% | n = 25")
print("     H0: mu = %.4f   contra   H1: mu > %.4f" % (mu0, mu0))
print("     Média amostral = %.4f | Erro padrão = %.4f" % (t3b["media_amostral"], t3b["erro_padrao"]))
print("     z calculado = %.4f | z crítico = %.4f | p-valor = %.4f"
      % (t3b["z"], t3b["z_critico"], t3b["p_valor"]))
if t3b["rejeita_h0"]:
    t3b["decisao"] = "Rejeita-se H0"
    t3b["conclusao"] = ("ao nível de 9%, há evidência de que a média do grupo amostrado "
                        "é maior do que a média de referência.")
else:
    t3b["decisao"] = "Não se rejeita H0"
    t3b["conclusao"] = ("ao nível de 9%, não há evidência suficiente de que a média do grupo "
                        "amostrado seja maior do que a média de referência.")
print("     Decisão:", t3b["decisao"], "-", t3b["conclusao"])

# Gráfico: curva normal padrão com a região crítica e o z calculado
eixo_z = np.linspace(-4, 4, 400)
curva_z = stats.norm.pdf(eixo_z)
fig, eixos = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
for ax, t, nome in [(eixos[0], t3a, "03A) Unilateral à esquerda (alfa = 6%, n = 20)"),
                    (eixos[1], t3b, "03B) Unilateral à direita (alfa = 9%, n = 25)")]:
    ax.plot(eixo_z, curva_z, color=CINZA, linewidth=2)
    if t["lado"] == "esquerda":
        regiao = eixo_z <= t["z_critico"]
    else:
        regiao = eixo_z >= t["z_critico"]
    ax.fill_between(eixo_z[regiao], curva_z[regiao], color=LARANJA, alpha=0.5,
                    label="Região crítica (z crítico = %.3f)" % t["z_critico"])
    ax.axvline(t["z"], color=AZUL, linewidth=2.5, label="z calculado = %.3f" % t["z"])
    ax.set_title(nome, fontsize=11)
    ax.set_xlabel("Estatística z")
    ax.legend(fontsize=9, loc="upper left")
eixos[0].set_ylabel("Densidade (normal padrão)")
fig.suptitle("Questão 03 - Teste z para a média da expectativa de anos de estudo", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q03_teste_hipotese.png"))
plt.close(fig)

resultados["q03"] = {
    "variavel": var3, "rotulo": ROTULOS[var3],
    "mu0": float(mu0), "sigma": float(sigma), "assimetria": float(x3.skew()),
    "a": t3a, "b": t3b,
    "amostra_a_municipios": (df.loc[amostra_a.index, "municipio"] + " ("
                             + df.loc[amostra_a.index, "ufn"] + ")").tolist(),
    "amostra_b_municipios": (df.loc[amostra_b.index, "municipio"] + " ("
                             + df.loc[amostra_b.index, "ufn"] + ")").tolist(),
}

# ----------------------------------------------------------------------
# QUESTÃO 04 - Análise bivariada
# X = taxa de analfabetismo | Y = proporção de pobres
# ----------------------------------------------------------------------
titulo("QUESTÃO 04 - ANÁLISE BIVARIADA")
x4_nome, y4_nome = "t_analf18m", "pmpob"
x4 = df[x4_nome]
y4 = df[y4_nome]
print("X =", x4_nome, "-", ROTULOS[x4_nome])
print("Y =", y4_nome, "-", ROTULOS[y4_nome])

# 04A) Gráfico de dispersão
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(x4, y4, s=8, alpha=0.3, color=AZUL)
ax.set_title("Questão 04A - Dispersão: analfabetismo x pobreza\n(5.565 municípios, Censo 2010)")
ax.set_xlabel(ROTULOS[x4_nome])
ax.set_ylabel(ROTULOS[y4_nome])
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q04a_dispersao.png"))
plt.close(fig)
print("\n04A) Gráfico salvo em figuras/q04a_dispersao.png")

# 04B) Covariância e correlação de Pearson
cov4 = np.cov(x4, y4, ddof=1)[0, 1]          # covariância amostral
r4, p_r4 = stats.pearsonr(x4, y4)
print("\n04B) Covariância(X, Y) = %.4f" % cov4)
print("     Correlação de Pearson r = %.4f (p-valor %s) -> correlação %s"
      % (r4, texto_p(p_r4), forca_correlacao(r4)))

# 04C) Gráfico de correlação (mapa de calor da matriz de correlação)
matriz_corr4 = df[[x4_nome, y4_nome]].corr(method="pearson")
fig, ax = plt.subplots(figsize=(5.5, 4.5))
sns.heatmap(matriz_corr4.rename(index=ROTULOS_CURTOS, columns=ROTULOS_CURTOS), annot=True, fmt=".3f", cmap="RdBu_r", vmin=-1, vmax=1,
            square=True, linewidths=2, annot_kws={"size": 14}, ax=ax,
            cbar_kws={"label": "Correlação de Pearson"})
ax.set_title("Questão 04C - Correlação linear de Pearson")
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q04c_correlacao.png"))
plt.close(fig)
print("\n04C) Gráfico salvo em figuras/q04c_correlacao.png")

# 04D) Regressão linear simples: Y = b0 + b1 * X
modelo4 = sm.OLS(y4, sm.add_constant(x4)).fit()
b0_4 = modelo4.params["const"]
b1_4 = modelo4.params[x4_nome]
print("\n04D) Equação: pmpob = %.4f + %.4f * t_analf18m" % (b0_4, b1_4))

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(x4, y4, s=8, alpha=0.3, color=AZUL, label="Municípios")
linha_x = np.array([x4.min(), x4.max()])
ax.plot(linha_x, b0_4 + b1_4 * linha_x, color=LARANJA, linewidth=2.5,
        label="Reta: y = %.3f + %.3f x" % (b0_4, b1_4))
ax.set_title("Questão 04D - Reta de regressão linear simples")
ax.set_xlabel(ROTULOS[x4_nome])
ax.set_ylabel(ROTULOS[y4_nome])
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q04d_regressao.png"))
plt.close(fig)

# 04E) Adequação do modelo: R² e teste F
print("\n04E) R² = %.4f | F = %.2f | p-valor do teste F %s"
      % (modelo4.rsquared, modelo4.fvalue, texto_p(modelo4.f_pvalue)))
print("     O modelo explica %.1f%% da variação da proporção de pobres." % (100 * modelo4.rsquared))
if modelo4.f_pvalue < 0.05:
    print("     p-valor < 0,05: o modelo é estatisticamente significativo.")
else:
    print("     p-valor >= 0,05: o modelo não é estatisticamente significativo.")

# 04F) Previsão para um município com 20% de analfabetismo
x4_novo = 20.0
prev4 = b0_4 + b1_4 * x4_novo
print("\n04F) Previsão: se t_analf18m = %.1f%%, pmpob previsto = %.2f%%" % (x4_novo, prev4))

resultados["q04"] = {
    "x": x4_nome, "y": y4_nome, "rotulo_x": ROTULOS[x4_nome], "rotulo_y": ROTULOS[y4_nome],
    "covariancia": float(cov4), "pearson": float(r4), "pearson_p": float(p_r4),
    "forca": forca_correlacao(r4),
    "b0": float(b0_4), "b1": float(b1_4),
    "r2": float(modelo4.rsquared), "f": float(modelo4.fvalue), "f_p": float(modelo4.f_pvalue),
    "gl_modelo": int(modelo4.df_model), "gl_residuo": int(modelo4.df_resid),
    "erro_padrao_residuos": float(np.sqrt(modelo4.mse_resid)),
    "x_min": float(x4.min()), "x_max": float(x4.max()),
    "prev_x": x4_novo, "prev_y": float(prev4),
}

# ----------------------------------------------------------------------
# QUESTÃO 05 - Análise multivariada (regressão linear múltipla)
# Y = proporção de pobres
# X = analfabetismo, banheiro e água encanada, energia elétrica
# ----------------------------------------------------------------------
titulo("QUESTÃO 05 - ANÁLISE MULTIVARIADA (REGRESSÃO LINEAR MÚLTIPLA)")
y5_nome = "pmpob"
x5_nomes = ["t_analf18m", "t_banagua", "t_luz"]
vars5 = [y5_nome] + x5_nomes
print("Y =", y5_nome, "| X =", ", ".join(x5_nomes))

# 05A) Gráficos de dispersão entre todos os pares de variáveis
grade = sns.pairplot(df[vars5].rename(columns=ROTULOS_CURTOS), corner=True, height=2.4,
                     plot_kws={"s": 6, "alpha": 0.25, "color": AZUL},
                     diag_kws={"color": AZUL})
grade.fig.suptitle("Questão 05A - Matriz de gráficos de dispersão", y=1.01, fontsize=13)
grade.savefig(os.path.join(PASTA_FIGURAS, "q05a_dispersao.png"))
plt.close(grade.fig)
print("\n05A) Gráfico salvo em figuras/q05a_dispersao.png")

# 05B) Matriz de covariância e matriz de correlação
matriz_cov5 = df[vars5].cov()
matriz_corr5 = df[vars5].corr(method="pearson")
print("\n05B) Matriz de covariância:")
print(matriz_cov5.round(3))
print("\n     Matriz de correlação de Pearson:")
print(matriz_corr5.round(3))

# 05C) Gráfico de correlação (mapa de calor)
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(matriz_corr5.rename(index=ROTULOS_CURTOS, columns=ROTULOS_CURTOS), annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
            square=True, linewidths=2, annot_kws={"size": 12}, ax=ax,
            cbar_kws={"label": "Correlação de Pearson"})
ax.set_title("Questão 05C - Matriz de correlação linear de Pearson")
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q05c_correlacao.png"))
plt.close(fig)
print("\n05C) Gráfico salvo em figuras/q05c_correlacao.png")

# 05D) Regressão linear múltipla
modelo5 = sm.OLS(df[y5_nome], sm.add_constant(df[x5_nomes])).fit()
coef5 = modelo5.params
equacao5 = "pmpob = %.4f" % coef5["const"]
for nome in x5_nomes:
    equacao5 += " %s %.4f * %s" % ("+" if coef5[nome] >= 0 else "-", abs(coef5[nome]), nome)
print("\n05D) Equação:", equacao5)
print("     p-valores dos coeficientes:")
print(modelo5.pvalues.apply(texto_p).to_string())

# 05E) Adequação do modelo: R², R² ajustado e teste F
print("\n05E) R² = %.4f | R² ajustado = %.4f | F = %.2f | p-valor do teste F %s"
      % (modelo5.rsquared, modelo5.rsquared_adj, modelo5.fvalue, texto_p(modelo5.f_pvalue)))
if modelo5.f_pvalue < 0.05:
    print("     p-valor < 0,05: o modelo é estatisticamente significativo.")
else:
    print("     p-valor >= 0,05: o modelo não é estatisticamente significativo.")
print("     O modelo explica %.1f%% da variação da proporção de pobres." % (100 * modelo5.rsquared))

# Gráfico de apoio: valores observados x valores previstos
fig, ax = plt.subplots(figsize=(6.5, 5.5))
ax.scatter(modelo5.fittedvalues, df[y5_nome], s=8, alpha=0.3, color=AZUL, label="Municípios")
limites = [0, df[y5_nome].max()]
ax.plot(limites, limites, color=LARANJA, linewidth=2, label="Previsão perfeita (y = x)")
ax.set_title("Questão 05E - Observado x previsto pelo modelo múltiplo")
ax.set_xlabel("Proporção de pobres prevista (%)")
ax.set_ylabel("Proporção de pobres observada (%)")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q05e_observado_previsto.png"))
plt.close(fig)

# 05F) Previsão com as três variáveis explicativas
entrada5 = {"t_analf18m": 20.0, "t_banagua": 70.0, "t_luz": 95.0}
prev5 = coef5["const"]
for nome in x5_nomes:
    prev5 += coef5[nome] * entrada5[nome]
print("\n05F) Previsão para", entrada5)
print("     pmpob previsto = %.2f%%" % prev5)

resultados["q05"] = {
    "y": y5_nome, "x": x5_nomes, "rotulos": {v: ROTULOS[v] for v in vars5},
    "matriz_cov": matriz_cov5.to_dict(), "matriz_corr": matriz_corr5.to_dict(),
    "coeficientes": {k: float(v) for k, v in coef5.items()},
    "p_valores": {k: float(v) for k, v in modelo5.pvalues.items()},
    "erros_padrao": {k: float(v) for k, v in modelo5.bse.items()},
    "equacao": equacao5,
    "r2": float(modelo5.rsquared), "r2_ajustado": float(modelo5.rsquared_adj),
    "f": float(modelo5.fvalue), "f_p": float(modelo5.f_pvalue),
    "gl_modelo": int(modelo5.df_model), "gl_residuo": int(modelo5.df_resid),
    "erro_padrao_residuos": float(np.sqrt(modelo5.mse_resid)),
    "prev_entrada": entrada5, "prev_y": float(prev5),
}

# ----------------------------------------------------------------------
# QUESTÃO 06 - Regressão logística binária
# Alvo: município com IDHM "Baixo" ou "Muito Baixo" (IDHM < 0,600) = 1
# X = analfabetismo, banheiro e água encanada, energia elétrica
# ----------------------------------------------------------------------
titulo("QUESTÃO 06 - REGRESSÃO LOGÍSTICA BINÁRIA")
LIMIAR_IDHM = 0.600   # abaixo disso o Atlas classifica o IDHM como Baixo ou Muito Baixo
x6_nomes = ["t_analf18m", "t_banagua", "t_luz"]

df["prioritario"] = (df["idhm"] < LIMIAR_IDHM).astype(int)
print("Alvo: prioritario = 1 se IDHM < %.3f (faixas Baixo e Muito Baixo do Atlas)" % LIMIAR_IDHM)
print("Municípios prioritários (1): %d | demais (0): %d"
      % (df["prioritario"].sum(), (df["prioritario"] == 0).sum()))
print("X =", ", ".join(x6_nomes))

# Separa 70% dos municípios para treino e 30% para teste
X_treino, X_teste, y_treino, y_teste = train_test_split(
    df[x6_nomes], df["prioritario"], test_size=0.30,
    random_state=SEMENTE, stratify=df["prioritario"])
print("Treino: %d municípios | Teste: %d municípios" % (len(X_treino), len(X_teste)))

# 06A) Ajuste do modelo e equação
modelo6 = sm.Logit(y_treino, sm.add_constant(X_treino)).fit(disp=0)
coef6 = modelo6.params
equacao6 = "logit(p) = ln(p / (1 - p)) = %.4f" % coef6["const"]
for nome in x6_nomes:
    equacao6 += " %s %.4f * %s" % ("+" if coef6[nome] >= 0 else "-", abs(coef6[nome]), nome)
print("\n06A) Equação:", equacao6)
print("     p = 1 / (1 + e^(-logit)), onde p = probabilidade de o município ser prioritário")
print("     Razões de chances (odds ratio = e^coeficiente):")
for nome in x6_nomes:
    print("       %-11s coef = %8.4f | odds ratio = %.4f | p-valor %s"
          % (nome, coef6[nome], np.exp(coef6[nome]), texto_p(modelo6.pvalues[nome])))

# 06B) Matriz de confusão e acurácia na base de teste (corte de 0,5)
prob_teste = modelo6.predict(sm.add_constant(X_teste))
prev_teste = (prob_teste >= 0.5).astype(int)
matriz6 = confusion_matrix(y_teste, prev_teste)
vn, fp, fn, vp = matriz6.ravel()
acuracia6 = accuracy_score(y_teste, prev_teste)
sensibilidade6 = vp / (vp + fn)
especificidade6 = vn / (vn + fp)
precisao6 = vp / (vp + fp)
acuracia_base6 = max(y_teste.mean(), 1 - y_teste.mean())  # chutar sempre a classe mais comum
print("\n06B) Matriz de confusão (linhas = real, colunas = previsto):")
print("                       Previsto 0   Previsto 1")
print("     Real 0 (demais)      %6d       %6d" % (vn, fp))
print("     Real 1 (priorit.)    %6d       %6d" % (fn, vp))
print("     Acurácia = %.4f (%.2f%%)" % (acuracia6, 100 * acuracia6))
print("     Acurácia de referência (prever sempre 0) = %.4f" % acuracia_base6)
print("     Sensibilidade = %.4f | Especificidade = %.4f | Precisão = %.4f"
      % (sensibilidade6, especificidade6, precisao6))

fig, ax = plt.subplots(figsize=(5.8, 4.8))
sns.heatmap(matriz6, annot=True, fmt="d", cmap="Blues", cbar=False, square=True,
            linewidths=2, annot_kws={"size": 16}, ax=ax,
            xticklabels=["Não prioritário (0)", "Prioritário (1)"],
            yticklabels=["Não prioritário (0)", "Prioritário (1)"])
ax.set_title("Questão 06B - Matriz de confusão (base de teste)\nAcurácia = %.2f%%" % (100 * acuracia6))
ax.set_xlabel("Classe prevista pelo modelo")
ax.set_ylabel("Classe real")
fig.tight_layout()
fig.savefig(os.path.join(PASTA_FIGURAS, "q06b_matriz_confusao.png"))
plt.close(fig)

# 06C) Classificação de um caso novo
entrada6 = {"t_analf18m": 25.0, "t_banagua": 60.0, "t_luz": 90.0}
logit6 = coef6["const"]
for nome in x6_nomes:
    logit6 += coef6[nome] * entrada6[nome]
prob6 = 1 / (1 + np.exp(-logit6))
classe6 = 1 if prob6 >= 0.5 else 0
texto_classe6 = "PRIORITÁRIO (classe 1)" if classe6 == 1 else "NÃO PRIORITÁRIO (classe 0)"
print("\n06C) Classificação para", entrada6)
print("     logit = %.4f | probabilidade = %.4f (%.2f%%) -> %s"
      % (logit6, prob6, 100 * prob6, texto_classe6))

resultados["q06"] = {
    "limiar_idhm": LIMIAR_IDHM, "x": x6_nomes,
    "n_classe1": int(df["prioritario"].sum()), "n_classe0": int((df["prioritario"] == 0).sum()),
    "n_treino": int(len(X_treino)), "n_teste": int(len(X_teste)),
    "coeficientes": {k: float(v) for k, v in coef6.items()},
    "p_valores": {k: float(v) for k, v in modelo6.pvalues.items()},
    "odds_ratio": {k: float(np.exp(coef6[k])) for k in x6_nomes},
    "equacao": equacao6,
    "vn": int(vn), "fp": int(fp), "fn": int(fn), "vp": int(vp),
    "acuracia": float(acuracia6), "acuracia_base": float(acuracia_base6),
    "sensibilidade": float(sensibilidade6), "especificidade": float(especificidade6),
    "precisao": float(precisao6),
    "class_entrada": entrada6, "class_logit": float(logit6), "class_prob": float(prob6),
    "class_classe": int(classe6), "class_texto": texto_classe6,
}

# ----------------------------------------------------------------------
# Apoio ao relatório (Questão 07): municípios prioritários por estado
# ----------------------------------------------------------------------
por_uf = df.groupby("ufn").agg(
    municipios=("prioritario", "size"),
    prioritarios=("prioritario", "sum"),
    populacao_prioritarios=("pop", lambda s: int(s[df.loc[s.index, "prioritario"] == 1].sum())),
).reset_index()
por_uf["percentual"] = 100 * por_uf["prioritarios"] / por_uf["municipios"]
por_uf = por_uf.sort_values("prioritarios", ascending=False)

resultados["q07"] = {
    "por_uf": por_uf.to_dict(orient="records"),
    "pop_total": int(df["pop"].sum()),
    "pop_prioritarios": int(df.loc[df["prioritario"] == 1, "pop"].sum()),
    "media_analf_prioritarios": float(df.loc[df["prioritario"] == 1, "t_analf18m"].mean()),
    "media_analf_demais": float(df.loc[df["prioritario"] == 0, "t_analf18m"].mean()),
    "media_pobres_prioritarios": float(df.loc[df["prioritario"] == 1, "pmpob"].mean()),
    "media_pobres_demais": float(df.loc[df["prioritario"] == 0, "pmpob"].mean()),
    "media_luz_prioritarios": float(df.loc[df["prioritario"] == 1, "t_luz"].mean()),
    "media_luz_demais": float(df.loc[df["prioritario"] == 0, "t_luz"].mean()),
}

titulo("APOIO À QUESTÃO 07 - ESTADOS COM MAIS MUNICÍPIOS PRIORITÁRIOS")
print(por_uf.head(10).round(1).to_string(index=False))

# Salva todos os resultados para o relatório
with open("resultados.json", "w", encoding="utf-8") as arquivo:
    json.dump(resultados, arquivo, ensure_ascii=False, indent=2)

titulo("FIM - gráficos em figuras/ e números em resultados.json")
