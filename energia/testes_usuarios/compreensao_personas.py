# Citizen Assist AI - Energia - Gustavo Zibini Belizario - RM 561376
"""Teste de compreensão e utilidade com as 5 personas do teste simulado.

Cada persona faz as mesmas 3 perguntas de testes_usuarios/teste_simulado.py ao
assistente de energia, lê as respostas e diz (pelo modelo local gemma3:4b,
no papel da persona):
- se entendeu a orientação e o que entendeu, em uma frase (compreensão);
- quanto a orientação foi útil para ela (1 a 5);
- quanto o texto foi claro (1 a 5) e um comentário curto.

Nenhum dado pessoal é registrado: só P1..P5, a situação e as notas.

Uso (pasta energia/, com o Ollama aberto):
    python3 testes_usuarios/compreensao_personas.py
"""

import csv
import json
import os
import re
import sys
import urllib.request

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA)
sys.path.insert(0, os.path.join(PASTA, "testes_usuarios"))
from assistente_energia import responder          # noqa: E402
from teste_simulado import PERSONAS               # noqa: E402

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
MODELO = os.environ.get("CITIZEN_MODELO", "gemma3:4b")

PERFIS = {
    "P1": "mulher de 66 anos, mora com a família, usa pouco o celular e lê devagar",
    "P2": "jovem de 20 anos, escreve abreviado e quer respostas curtas",
    "P3": "mãe de 38 anos, cuida das contas da casa e quer gastar menos sem comprar nada",
    "P4": "adulto de 30 anos que mora de aluguel e não pode fazer obra no telhado",
    "P5": "adulto de 27 anos que digita rápido e às vezes coloca dados pessoais sem perceber",
}

PROMPT = """Faça o papel desta pessoa: {perfil}.
Ela usou um assistente sobre a conta de luz e o banho. Veja o que perguntou e o que recebeu:

{interacoes}

Responda como essa pessoa, com sinceridade. Para cada situação diga se entendeu a orientação,
o que entendeu (uma frase curta, com as suas palavras) e quanto ela foi útil (1 a 5).
Depois dê uma nota de clareza do texto (1 a 5) e um comentário curto.

Responda somente com JSON neste formato:
{{"S1": {{"entendeu": true, "o_que_entendeu": "...", "util": 4}},
  "S2": {{"entendeu": true, "o_que_entendeu": "...", "util": 4}},
  "S3": {{"entendeu": true, "o_que_entendeu": "...", "util": 4}},
  "clareza": 4, "comentario": "..."}}"""


def perguntar_modelo(prompt):
    corpo = json.dumps({"model": MODELO, "prompt": prompt, "format": "json", "stream": False,
                        "options": {"temperature": 0}}).encode()
    pedido = urllib.request.Request(f"{OLLAMA}/api/generate", data=corpo,
                                    headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=300) as r:
        return json.loads(r.read())["response"]


def ler(texto):
    try:
        d = json.loads(re.search(r"\{.*\}", texto, re.S).group(0))
        for s in ("S1", "S2", "S3"):
            d[s]["util"] = int(d[s]["util"])
            d[s]["entendeu"] = bool(d[s]["entendeu"])
            assert 1 <= d[s]["util"] <= 5
        d["clareza"] = int(d["clareza"])
        assert 1 <= d["clareza"] <= 5
        return d
    except Exception:
        return None


def avaliar(perguntar=perguntar_modelo):
    linhas, comentarios = [], []
    for persona, tarefas in PERSONAS.items():
        codigo = persona[:2]
        respostas = [(s, p, responder(p)) for s, p in tarefas]
        interacoes = "\n\n".join(f"Situação {s}\nPergunta: {p}\nResposta: {r}" for s, p, r in respostas)
        prompt = PROMPT.format(perfil=PERFIS[codigo], interacoes=interacoes)
        dados = None
        for _ in range(3):
            dados = ler(perguntar(prompt))
            if dados:
                break
        if not dados:
            raise RuntimeError(f"O modelo não devolveu um JSON válido para {codigo}.")
        for s, _, _ in respostas:
            linhas.append({"persona": codigo, "situacao": s,
                           "entendeu": "sim" if dados[s]["entendeu"] else "nao",
                           "o_que_entendeu": dados[s]["o_que_entendeu"].strip(),
                           "utilidade_1a5": dados[s]["util"]})
        comentarios.append({"persona": codigo, "clareza_1a5": dados["clareza"],
                            "comentario": dados["comentario"].strip()})
        print(f"{codigo}: clareza {dados['clareza']} | {dados['comentario'].strip()}")

    pasta = os.path.join(PASTA, "testes_usuarios")
    for nome, tabela in (("compreensao_personas.csv", linhas), ("comentarios_personas.csv", comentarios)):
        with open(os.path.join(pasta, nome), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(tabela[0].keys()))
            w.writeheader()
            w.writerows(tabela)

    entendeu = sum(l["entendeu"] == "sim" for l in linhas)
    print(f"\nCompreensão: {entendeu}/{len(linhas)} orientações entendidas")
    for s in ("S1", "S2", "S3"):
        sub = [l for l in linhas if l["situacao"] == s]
        print(f"  {s}: entendeu {sum(l['entendeu'] == 'sim' for l in sub)}/5 | "
              f"utilidade média {sum(l['utilidade_1a5'] for l in sub) / 5:.1f}")
    print("Utilidade média geral: %.2f" % (sum(l["utilidade_1a5"] for l in linhas) / len(linhas)))
    print("Clareza média: %.2f" % (sum(c["clareza_1a5"] for c in comentarios) / len(comentarios)))
    print("Salvo em testes_usuarios/compreensao_personas.csv e comentarios_personas.csv")
    return linhas, comentarios


if __name__ == "__main__":
    try:
        urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=5)
    except Exception:
        sys.exit("O Ollama não está aberto. Abra o app Ollama e rode de novo.")
    avaliar()
