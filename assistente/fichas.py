# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Carrega as fichas .md, divide em seções e faz a busca por palavras-chave.

Por que palavras-chave e não embeddings?
- São só 7 fichas curtas; uma busca simples é suficiente e explicável.
- Cada trecho guarda o código da ficha (FC-xx) e a data: a fonte é rastreável.
- Não depende de rede nem de outro modelo; o resultado é sempre o mesmo.
"""

import os
import re
import unicodedata
from dataclasses import dataclass, field

import config

# ---------------------------------------------------------------- texto


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação e com plural simples removido."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    palavras = [p[:-1] if len(p) > 3 and p.endswith("s") else p for p in texto.split()]
    return " ".join(palavras)


def contem_termo(texto_normalizado, termo):
    """True se o termo (uma ou mais palavras) aparece inteiro no texto."""
    return f" {normalizar(termo)} " in f" {texto_normalizado} "


# Palavras que não ajudam a escolher a ficha.
STOPWORDS = set(normalizar(
    "a o as os um uma de da do das dos e em no na nos nas para pra por com sem "
    "que se ao aos meu minha seu sua eu voce voces ele ela isso esse essa este "
    "esta ha tem ter tenho como qual quais quanto quando onde preciso posso "
    "pode fazer faco tirar quero ser e ou mais muito"
).split())

# ---------------------------------------------------------------- estrutura


@dataclass
class Secao:
    codigo: str      # ex.: "FC-01"
    rotulo: str      # ex.: "Custo"
    texto: str       # conteúdo da seção


@dataclass
class Ficha:
    codigo: str
    titulo: str
    palavras_chave: list
    data_verificacao: str
    secoes: list = field(default_factory=list)

    def texto_completo(self):
        return "\n".join(f"[{self.codigo} | {s.rotulo}] {s.texto}" for s in self.secoes)


# Termos para as seções da FC-07 (que não tem linha de palavras-chave).
# Usados somente na recuperação v2 (a melhoria).
TERMOS_FC07 = {
    "Horário de atendimento presencial": [
        "horario", "sabado", "domingo", "feriado", "abre", "fecha", "funciona", "atendem"],
    "Agendamento": ["agendamento", "agendar", "agenda", "marcar", "marcar horario"],
    "Documentos": ["copia", "fotocopia", "xerox", "autenticada"],
    "Atendimento por terceiros": [
        "terceiro", "outra pessoa", "procuracao", "filho", "filha", "crianca",
        "menor", "responsavel", "por mim"],
    "Pagamento": ["pagamento", "pagar", "pix", "guia", "boleto", "banco"],
    "Atendimento prioritário": [
        "prioridade", "prioritario", "idoso", "gestante", "deficiencia",
        "libras", "interprete", "acessibilidade", "surdo"],
    "Perda, roubo ou furto de documento": [
        "perdi", "perda", "roubo", "roubaram", "furto", "furtaram", "boletim"],
    "Privacidade": ["dados pessoais", "senha", "privacidade", "endereco", "telefone"],
}

# ---------------------------------------------------------------- leitura


def ler_ficha(caminho):
    """Lê um arquivo FC-xx.md e devolve um objeto Ficha."""
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()

    titulo = linhas[0].lstrip("# ").strip()
    codigo = titulo.split()[0]                     # "FC-01"
    secoes, palavras, data = [], [], ""
    atual = None

    for linha in linhas[1:]:
        cabecalho = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", linha)
        if cabecalho:
            atual = Secao(codigo, cabecalho.group(1).strip(), cabecalho.group(2).strip())
            secoes.append(atual)
        elif atual and linha.strip():
            atual.texto += "\n" + linha.strip()

    for secao in secoes:
        if secao.rotulo == "Palavras-chave":
            palavras = [p.strip() for p in secao.texto.split(",") if p.strip()]
        if secao.rotulo == "Fonte":
            achou = re.search(r"\d{2}/\d{2}/\d{4}", secao.texto)
            data = achou.group(0) if achou else ""

    # A linha de palavras-chave não é conteúdo para o cidadão.
    secoes = [s for s in secoes if s.rotulo != "Palavras-chave"]
    return Ficha(codigo, titulo, palavras, data, secoes)


def carregar_fichas(pasta=None):
    """Carrega as 7 fichas em um dicionário {codigo: Ficha}."""
    pasta = pasta or config.achar_pasta_fichas()
    fichas = {}
    for nome in sorted(os.listdir(pasta)):
        if nome.startswith("FC-") and nome.endswith(".md"):
            ficha = ler_ficha(os.path.join(pasta, nome))
            fichas[ficha.codigo] = ficha
    return fichas


# ---------------------------------------------------------------- índice


def termos_da_ficha(ficha, versao):
    """Termos que identificam a ficha. v1: só palavras-chave. v2: + FC-07."""
    termos = list(ficha.palavras_chave)
    if versao == "v2" and ficha.codigo == "FC-07":
        for lista in TERMOS_FC07.values():
            termos += lista
    return termos


def pontuar_ficha(mensagem_norm, ficha, versao):
    """Soma 3 pontos por termo encontrado (+1 por palavra extra do termo)."""
    pontos, achados = 0, []
    for termo in termos_da_ficha(ficha, versao):
        if contem_termo(mensagem_norm, termo):
            pontos += 2 + len(normalizar(termo).split())
            achados.append(termo)
    return pontos, achados


def desempate(mensagem_norm, ficha):
    """Quantas palavras da mensagem aparecem no texto da ficha."""
    texto = normalizar(ficha.texto_completo())
    palavras = set(mensagem_norm.split()) - STOPWORDS
    return sum(1 for p in palavras if contem_termo(texto, p))


def secoes_fc07(mensagem_norm, ficha07, com_privacidade):
    """Seções da FC-07 que combinam com a mensagem (máx. 2 + privacidade)."""
    escolhidas = []
    for secao in ficha07.secoes:
        termos = TERMOS_FC07.get(secao.rotulo, [])
        if any(contem_termo(mensagem_norm, t) for t in termos):
            escolhidas.append(secao)
    escolhidas = escolhidas[:2]
    if com_privacidade:
        privacidade = [s for s in ficha07.secoes if s.rotulo == "Privacidade"]
        escolhidas += [s for s in privacidade if s not in escolhidas]
    return escolhidas


# ---------------------------------------------------------------- busca

PONTUACAO_MINIMA = 3   # pelo menos um termo forte


def buscar(mensagem, fichas, versao="v2", tem_dado_pessoal=False):
    """Devolve {'fichas': [...], 'trechos': [Secao...], 'pontos': int}.

    Lista vazia = nada encontrado (fora do escopo).
    """
    msg = normalizar(mensagem)
    placar = []
    for ficha in fichas.values():
        pontos, achados = pontuar_ficha(msg, ficha, versao)
        if pontos >= PONTUACAO_MINIMA:
            # FC-07 (regras gerais) só é principal se nenhum documento foi citado.
            eh_documento = 1 if ficha.codigo != "FC-07" else 0
            placar.append((eh_documento, pontos, desempate(msg, ficha), ficha))

    if not placar:
        return {"fichas": [], "trechos": [], "pontos": 0}

    placar.sort(key=lambda item: item[:3], reverse=True)
    principal = placar[0][3]
    trechos = list(principal.secoes)
    codigos = [principal.codigo]

    # Melhoria v2: anexa regras gerais da FC-07 quando a pergunta pede.
    if versao == "v2" and principal.codigo != "FC-07" and "FC-07" in fichas:
        extras = secoes_fc07(msg, fichas["FC-07"], tem_dado_pessoal)
        if extras:
            trechos += extras
            codigos.append("FC-07")

    return {"fichas": codigos, "trechos": trechos, "pontos": placar[0][1]}


def formatar_trechos(trechos):
    """Texto dos trechos para o prompt, cada um com sua ficha de origem."""
    return "\n".join(f"[{s.codigo} | {s.rotulo}] {s.texto}" for s in trechos)


def vocabulario(fichas):
    """Todas as palavras das fichas (usado para detectar texto sem sentido)."""
    palavras = set(STOPWORDS)
    for ficha in fichas.values():
        palavras |= set(normalizar(ficha.titulo + " " + ficha.texto_completo()).split())
        palavras |= set(normalizar(" ".join(ficha.palavras_chave)).split())
    return palavras
