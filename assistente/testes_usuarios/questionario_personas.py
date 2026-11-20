# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Completa o teste com personas com os dois indicadores que faltavam:
tempo para encontrar a informação e facilidade de uso (questionário q1-q5, 1 a 5).

Entrada: testes_usuarios/resultado_simulado.csv (perguntas e respostas reais do agente).
Saída:   testes_usuarios/registro_personas.csv, no mesmo formato de registro.csv,
         e o resumo calculado por avaliacao.indicadores_usuarios().

Tempo para encontrar = orientação na tela + digitação da pergunta + resposta do
sistema (medida) + leitura da resposta. Quando a resposta não trouxe a informação,
a persona reformula e tenta mais uma vez (o tempo dobra e a tarefa fica como erro).

Facilidade: o mesmo modelo local faz o papel de cada persona, lê as 3 perguntas que
ela fez e as respostas que recebeu, e responde ao questionário do roteiro.

Uso (pasta assistente/, Ollama aberto):
    .venv/bin/python testes_usuarios/questionario_personas.py
"""

import csv
import json
import os
import re
import sys

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA)
os.chdir(PASTA)
os.environ.setdefault("CITIZEN_PROVEDOR", "ollama")

# Perfil de cada persona: descrição para o questionário e parâmetros de tempo.
# digitacao = caracteres por segundo no celular; leitura = palavras por minuto;
# orientacao = segundos para achar onde digitar e começar.
PERFIS = {
    "P1": {"descricao": "pessoa idosa, 68 anos, usa pouco o celular, lê devagar e se confunde com textos longos",
           "digitacao": 1.0, "leitura": 120, "orientacao": 12},
    "P2": {"descricao": "jovem de 19 anos, escreve abreviado, impaciente, quer a resposta rápida e direta",
           "digitacao": 4.0, "leitura": 250, "orientacao": 3},
    "P3": {"descricao": "adulto de 45 anos, escreve de forma formal, lê com atenção e valoriza a fonte da informação",
           "digitacao": 2.5, "leitura": 220, "orientacao": 5},
    "P4": {"descricao": "adulta de 34 anos que trabalha a semana toda, conta a situação antes de perguntar e quer resolver logo",
           "digitacao": 3.0, "leitura": 200, "orientacao": 5},
    "P5": {"descricao": "adulto de 27 anos, digita rápido e às vezes coloca dados pessoais sem perceber",
           "digitacao": 3.5, "leitura": 230, "orientacao": 4},
}

QUESTOES = {
    "q1": "Foi fácil encontrar a informação que eu procurava.",
    "q2": "As respostas foram claras e fáceis de entender.",
    "q3": "Ficou claro de onde veio a informação (ficha e data).",
    "q4": "O menu e as mensagens de erro me ajudaram a seguir em frente.",
    "q5": "Eu usaria este assistente de novo.",
}

PROMPT = """Você vai fazer o papel de uma pessoa que acabou de testar um assistente digital sobre documentos.
Quem você é: {descricao}.

Você fez 3 perguntas ao assistente. Veja o que perguntou, o que recebeu e se encontrou o que precisava:
{interacoes}

Agora responda ao questionário como essa pessoa responderia, com sinceridade, considerando o seu jeito de ser.
Notas de 1 (discordo totalmente) a 5 (concordo totalmente):
{questoes}

Responda somente com JSON neste formato:
{{"q1": nota, "q2": nota, "q3": nota, "q4": nota, "q5": nota, "comentario": "uma frase curta da pessoa"}}"""


def contar_palavras(texto):
    return len(re.findall(r"\w+", texto))


def tempo_para_encontrar(perfil, pergunta, tempo_sistema, resposta, acertou):
    uma_tentativa = (perfil["orientacao"]
                     + len(pergunta) / perfil["digitacao"]
                     + tempo_sistema
                     + contar_palavras(resposta) / perfil["leitura"] * 60)
    total = uma_tentativa if acertou else 2 * uma_tentativa
    return round(min(total, 180))           # limite do roteiro: 180 s


def ler_notas(texto):
    try:
        dados = json.loads(re.search(r"\{.*\}", texto, re.S).group(0))
        notas = {q: int(dados[q]) for q in QUESTOES}
        if all(1 <= n <= 5 for n in notas.values()):
            return notas, str(dados.get("comentario", "")).strip()
    except Exception:
        pass
    return None, ""


def questionario(llm, perfil, linhas):
    interacoes = "\n\n".join(
        f"Pergunta {i}: {l['pergunta_mascarada']}\nResposta recebida: {l['resposta']}\n"
        f"Encontrou a informação? {'sim' if l['acertou'] == 'sim' else 'não'}"
        for i, l in enumerate(linhas, start=1))
    questoes = "\n".join(f"{q}: {t}" for q, t in QUESTOES.items())
    prompt = PROMPT.format(descricao=perfil["descricao"], interacoes=interacoes, questoes=questoes)
    for _ in range(3):                       # até 3 tentativas de obter JSON válido
        notas, comentario = ler_notas(llm.invoke(prompt).content)
        if notas:
            return notas, comentario
    raise RuntimeError("O modelo não devolveu notas válidas.")


def principal(llm):
    origem = os.path.join("testes_usuarios", "resultado_simulado.csv")
    with open(origem, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    registro, comentarios = [], {}
    for codigo, perfil in PERFIS.items():
        da_persona = [l for l in linhas if l["persona"].startswith(codigo)]
        notas, comentarios[codigo] = questionario(llm, perfil, da_persona)
        for l in da_persona:
            tempo = tempo_para_encontrar(perfil, l["pergunta_mascarada"], float(l["tempo_s"]),
                                         l["resposta"], l["acertou"] == "sim")
            linha = {"participante": codigo, "tarefa": l["tarefa"], "tempo_s": tempo,
                     "acertou": l["acertou"], **{q: "" for q in QUESTOES}}
            if l["tarefa"] == "T3":
                linha.update(notas)
            registro.append(linha)
        print(f"{codigo}: notas {notas} | {comentarios[codigo]}")

    destino = os.path.join("testes_usuarios", "registro_personas.csv")
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["participante", "tarefa", "tempo_s", "acertou", *QUESTOES])
        w.writeheader()
        w.writerows(registro)
    with open(os.path.join("testes_usuarios", "comentarios_personas.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participante", "comentario"])
        w.writerows(comentarios.items())

    import avaliacao
    ind = avaliacao.indicadores_usuarios(destino)
    print("\n=== Indicadores (5 personas x 3 tarefas) ===")
    print("Tempo para encontrar (s):\n", ind["tempo_por_tarefa_s"].to_string())
    print("Acerto por tarefa (%):\n", ind["acerto_por_tarefa_%"].to_string())
    print("Acerto geral (%):", ind["acerto_geral_%"])
    print("Facilidade média (1 a 5):", ind["facilidade_media_1a5"])
    print("Facilidade por pergunta:\n", ind["facilidade_por_pergunta"].to_string())
    print("\nSalvo em", destino)
    return ind


if __name__ == "__main__":
    import modelos
    from rodar_local import checar_ollama
    if not checar_ollama():
        sys.exit(1)
    principal(modelos.criar_llm_juiz())
