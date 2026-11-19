# Citizen Assist AI - Energia - Gustavo Zibini Belizario - RM 561376
"""TESTE SIMULADO COM PERSONAS (não substitui teste com pessoas reais).

Cada persona faz as 3 situações do roteiro escrevendo do seu jeito
(informal, com abreviação, sem acento...). O assistente real responde e o
script confere se a resposta traz a informação esperada.

Mede: acerto (regra fixa), tempo de resposta do sistema e clareza do texto
(palavras por frase). NÃO mede satisfação: isso só pessoas reais podem dizer.

Uso: python3 testes_usuarios/teste_simulado.py   (a partir da pasta energia/)
"""

import csv
import os
import re
import sys
import time

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA)
from assistente_energia import responder  # noqa: E402

PERSONAS = {
    "P1 - idosa, pouco uso de celular": [
        ("S1", "quanto o chuveiro gasta por mes"),
        ("S2", "aqui em casa somos 3 e cada um demora uns 12 minutos no banho, quanto da?"),
        ("S3", "tenho cadunico, tenho desconto na luz?"),
    ],
    "P2 - jovem, escreve abreviado": [
        ("S1", "qnto custa o banho"),
        ("S2", "calcular 4 pessoas 8 minutos"),
        ("S3", "vale a pena aquecedor solar?"),
    ],
    "P3 - mãe, quer economizar": [
        ("S1", "como gastar menos com banho sem comprar nada"),
        ("S2", "somos 5 e o banho dura 15 minutos, quanto gasto?"),
        ("S3", "o que é tarifa social e quem tem direito"),
    ],
    "P4 - mora de aluguel": [
        ("S1", "o chuveiro pesa muito na conta?"),
        ("S2", "2 pessoas, banho de 20 minutos, chuveiro 7500 W"),
        ("S3", "moro de aluguel, compensa colocar placa solar?"),
    ],
    "P5 - digita dado pessoal sem querer": [
        ("S1", "meu cpf é 123.456.789-00, quanto gasto de banho?"),
        ("S2", "calcular meu caso"),
        ("S3", "quanto co2 eu evito com aquecedor solar"),
    ],
}


def acertou(situacao, pergunta, resposta):
    """Regra fixa do que a resposta precisa conter em cada situação."""
    r = resposta.lower()
    if "cpf" in pergunta.lower():          # deve recusar o dado e não usá-lo
        return "não digite" in r and "123.456" not in r
    if situacao == "S1":
        return "kwh" in r and "r$" in r
    if situacao == "S2":
        numeros = re.findall(r"\d+", pergunta)
        if not numeros:          # pediu cálculo sem números: deve explicar como fazer
            return "opção 7" in r or "calcular" in r
        return r.startswith(f"seu caso: {numeros[0]} pessoa") and f"banho de {numeros[1]} min" in r
    if situacao == "S3":
        return any(t in r for t in ("80 kwh", "telhado", "co2", "aluguel", "casa própria"))
    return False


def palavras_por_frase(texto):
    frases = [f for f in re.split(r"[.!?\n]+", texto) if len(f.split()) > 2]
    return round(sum(len(f.split()) for f in frases) / max(len(frases), 1), 1)


if __name__ == "__main__":
    linhas = []
    for persona, tarefas in PERSONAS.items():
        for situacao, pergunta in tarefas:
            inicio = time.perf_counter()
            resposta = responder(pergunta)
            ms = round((time.perf_counter() - inicio) * 1000, 1)
            ok = acertou(situacao, pergunta, resposta)
            linhas.append({"persona": persona, "situacao": situacao, "pergunta": pergunta,
                           "acertou": "sim" if ok else "nao", "tempo_ms": ms,
                           "palavras_por_frase": palavras_por_frase(resposta),
                           "inicio_resposta": resposta.split("\n")[0][:90]})
            print(f"{persona[:3]} {situacao} {'OK ' if ok else 'ERRO'} {ms:>6} ms | {pergunta[:55]}")

    saida = os.path.join(PASTA, "testes_usuarios", "resultado_simulado.csv")
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    total = len(linhas)
    acertos = sum(l["acertou"] == "sim" for l in linhas)
    print(f"\nAcerto: {acertos}/{total} ({100 * acertos / total:.0f}%)")
    for s in ("S1", "S2", "S3"):
        sub = [l for l in linhas if l["situacao"] == s]
        print(f"  {s}: {sum(l['acertou'] == 'sim' for l in sub)}/{len(sub)}")
    print("Tempo médio de resposta: %.1f ms" % (sum(l["tempo_ms"] for l in linhas) / total))
    print("Palavras por frase (média): %.1f" % (sum(l["palavras_por_frase"] for l in linhas) / total))
    print("Resultado salvo em", saida)
