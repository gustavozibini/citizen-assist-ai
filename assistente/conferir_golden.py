# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Confere o golden_dataset.csv contra o texto do PDF do enunciado (pdftotext).

Uso: python conferir_golden.py caminho/do/enunciado.txt
Compara mensagem e resposta esperada, palavra por palavra (espaços e quebras
de linha do PDF são ignorados). Também confere se as fichas citadas batem.
"""
import csv
import re
import sys


def juntar(texto):
    return " ".join(texto.split())


def main(caminho_txt):
    pdf = juntar(open(caminho_txt, encoding="utf-8").read())
    erros = 0
    with open("golden_dataset.csv", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for l in linhas:
        msg_ok = f"“{l['mensagem']}”" in pdf
        resp_ok = l["resposta_esperada"] in pdf
        fichas_txt = sorted(set(re.findall(r"FC-\d\d", l["resposta_esperada"])))
        fichas_ok = fichas_txt == sorted(filter(None, l["fichas_esperadas"].split(";")))
        tipo_ok = l["tipo"] in pdf
        ok = msg_ok and resp_ok and fichas_ok and tipo_ok
        erros += not ok
        print(f"#{l['id']:>2} mensagem={'OK' if msg_ok else 'ERRO'} resposta={'OK' if resp_ok else 'ERRO'} "
              f"fichas={'OK' if fichas_ok else 'ERRO'} tipo={'OK' if tipo_ok else 'ERRO'}")
    print(f"\nTotal: {len(linhas)} linhas, {erros} com divergência.")


if __name__ == "__main__":
    main(sys.argv[1])
