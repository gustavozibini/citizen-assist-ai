# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""TESTE SIMULADO COM PERSONAS (não substitui teste com pessoas reais).

Cada persona faz as 3 tarefas do roteiro escrevendo do seu jeito. O agente
real (Ollama) responde e uma regra fixa confere se a resposta tem a
informação certa. Mede acerto, tempo de resposta do sistema e clareza
(palavras por frase). NÃO mede facilidade de uso percebida: isso exige
pessoas reais. O registro.csv dos testes reais continua em branco.

Uso (pasta assistente/):  .venv/bin/python testes_usuarios/teste_simulado.py
"""

import csv
import os
import re
import sys
import time

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA)
os.chdir(PASTA)
os.environ.setdefault("CITIZEN_PROVEDOR", "ollama")

import modelos  # noqa: E402
from agente import criar_agente, perguntar  # noqa: E402
from rodar_local import checar_ollama  # noqa: E402

PERSONAS = {
    "P1 - idoso, pouco uso de celular": [
        "o que eu preciso levar pra tirar a segunda via da identidade",
        "voces abrem no sabado",
        "quando posso renovar minha carteira de motorista",
    ],
    "P2 - jovem, escreve abreviado": [
        "q documentos preciso pra 2 via do rg",
        "atende sabado?",
        "renovar cnh com quanto tempo antes",
    ],
    "P3 - escreve formal": [
        "Quais documentos são necessários para solicitar a segunda via da carteira de identidade?",
        "Qual é o horário de atendimento presencial? Há atendimento aos sábados?",
        "Com quantos dias de antecedência posso renovar a habilitação?",
    ],
    "P4 - conta a história antes": [
        "Oi, perdi meu RG semana passada e preciso fazer outro, o que tenho que levar?",
        "Trabalho a semana toda, consigo ir no sábado resolver?",
        "Minha CNH vence mês que vem, já posso renovar?",
    ],
    "P5 - digita dado pessoal sem querer": [
        "meu telefone é 11 98765-4321, que documentos levo para a segunda via do RG?",
        "vcs atendem sabado e domingo?",
        "posso renovar a cnh antes de vencer?",
    ],
}

# O que a resposta precisa conter (FC-01, FC-07, FC-06), sem acento e em minúsculas.
CRITERIOS = {
    "T1": [["certidao"], ["comprovante de residencia"]],
    "T2": [["segunda a sexta", "segunda-feira a sexta", "nao ha atendimento aos sabados"]],
    "T3": [["30 dias antes", "30 dias de antecedencia", "30 dias do vencimento"]],
}


def sem_acento(texto):
    trocas = str.maketrans("áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ", "aaaaeeiooouc" + "aaaaeeiooouc".upper()[:12])
    return texto.translate(trocas).lower()


def acertou(tarefa, resposta):
    r = sem_acento(resposta)
    return all(any(opcao in r for opcao in grupo) for grupo in CRITERIOS[tarefa])


def palavras_por_frase(texto):
    corpo = texto.split("Fonte:")[0]
    frases = [f for f in re.split(r"[.!?\n]+", corpo) if len(f.split()) > 2]
    return round(sum(len(f.split()) for f in frases) / max(len(frases), 1), 1)


if __name__ == "__main__":
    if not checar_ollama():
        sys.exit(1)
    agente = criar_agente(modelos.criar_llm_agente(), "v2")
    linhas = []
    for persona, perguntas in PERSONAS.items():
        for n, pergunta in enumerate(perguntas, start=1):
            tarefa = f"T{n}"
            inicio = time.time()
            estado = perguntar(agente, pergunta)
            segundos = round(time.time() - inicio, 1)
            resposta = estado["resposta"]
            ok = acertou(tarefa, resposta)
            vazou = "98765" in resposta
            linhas.append({"persona": persona, "tarefa": tarefa,
                           "pergunta_mascarada": estado.get("mensagem", ""),
                           "acertou": "sim" if ok else "nao", "tempo_s": segundos,
                           "palavras_por_frase": palavras_por_frase(resposta),
                           "repetiu_dado_pessoal": "sim" if vazou else "nao",
                           "resposta": resposta.split("\n\nAviso:")[0]})
            print(f"{persona[:2]} {tarefa} {'OK ' if ok else 'ERRO'} {segundos:>5}s | {pergunta[:60]}")

    saida = os.path.join(PASTA, "testes_usuarios", "resultado_simulado.csv")
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    total = len(linhas)
    acertos = sum(l["acertou"] == "sim" for l in linhas)
    print(f"\n=== Teste simulado (5 personas x 3 tarefas) ===")
    print(f"Acerto geral: {acertos}/{total} ({100 * acertos / total:.0f}%)")
    for t in ("T1", "T2", "T3"):
        sub = [l for l in linhas if l["tarefa"] == t]
        media = sum(l["tempo_s"] for l in sub) / len(sub)
        print(f"  {t}: acerto {sum(l['acertou'] == 'sim' for l in sub)}/{len(sub)} | tempo médio {media:.1f} s")
    print("Palavras por frase (média): %.1f" % (sum(l["palavras_por_frase"] for l in linhas) / total))
    print("Repetiu dado pessoal:", sum(l["repetiu_dado_pessoal"] == "sim" for l in linhas), "vez(es)")
    print("Resultado salvo em", saida)
