# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Validação de entrada, proteção de dados pessoais e detecção de prompt injection.

Tudo aqui é regra fixa (regex e listas), sem IA: é rápido, previsível
e roda ANTES de qualquer texto ir para o modelo.
"""

import re
import unicodedata

import config
from fichas import normalizar


def compactar(texto):
    """Minúsculas, sem acento e SEM espaços nem pontuação (não corta plural)."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", texto)

# ================================================================ entrada


def validar_entrada(texto):
    """Devolve None se a entrada é aceitável, ou o motivo: 'vazia' / 'longa'."""
    if texto is None or not str(texto).strip():
        return "vazia"
    if len(texto) > config.LIMITE_CARACTERES:
        return "longa"
    return None


PALAVRAS_COMUNS = set(normalizar(
    "oi ola bom boa dia tarde noite obrigado obrigada ajuda ajudar menu sim nao "
    "quero gostaria saber informacao duvida documento documentos preco valor custo "
    "custa prazo demora tempo vale validade renovar tirar emitir pedir solicitar "
    "onde fica endereco telefone horario agora hoje amanha mudar trocar passaporte "
    "vacina multa ipva imposto beneficio aposentadoria carro moto filho filha "
    "mae pai pessoa prefeitura governo canal oficial site portal situacao"
).split())


def texto_sem_sentido(texto, vocabulario):
    """True se nenhuma palavra da mensagem é conhecida (ex.: 'asdfgh ??? 123')."""
    palavras = [p for p in normalizar(texto).split() if p.isalpha()]
    conhecidas = [p for p in palavras if p in vocabulario or p in PALAVRAS_COMUNS]
    return len(conhecidas) == 0


# ================================================================ dados pessoais

# Ordem importa: padrões mais específicos primeiro.
PADROES_DADOS = [
    ("E-MAIL", r"[\w.+-]+@[\w-]+\.[\w.]+"),
    ("CPF", r"\b\d{3}\.\d{3}\.\d{3}-?\d{2}\b|\b\d{3}\s\d{3}\s\d{3}\s?\d{2}\b"),
    ("RG", r"\b\d{1,2}\.\d{3}\.\d{3}-?[\dxX]\b"),
    ("CEP", r"\b\d{5}-\d{3}\b"),
    ("TELEFONE", r"(\+?55\s?)?(\(?\b\d{2}\)?\s?)?\b9?\d{4}[-\s]\d{4}\b"),
    ("NÚMERO", r"\b\d{8,}\b"),   # CPF/CNH/título/PIS sem pontuação, protocolo
    ("ENDEREÇO", r"(?i)\b(rua|avenida|av\.|travessa|alameda|estrada|rodovia|pra[cç]a)"
                 r"\s+[^\d,\n]{2,40},?\s*(n[ºo°.]*\s*)?\d{1,5}"),
    ("NOME", r"(?i)(?<=meu nome [eé] )[\wÀ-ú]+(\s+[\wÀ-ú]+){0,3}"
             r"|(?<=me chamo )[\wÀ-ú]+(\s+[\wÀ-ú]+){0,3}"),
]


def mascarar_dados(texto):
    """Troca dados pessoais por marcadores. Devolve (texto_mascarado, tipos)."""
    tipos = []
    for tipo, padrao in PADROES_DADOS:
        if re.search(padrao, texto):
            tipos.append(tipo)
            texto = re.sub(padrao, f"[{tipo} REMOVIDO]", texto)
    return texto, tipos


# Intenção de enviar dados, mesmo sem o número (ex.: "vou te passar meu telefone").
PADROES_INTENCAO = [
    r"\b(vou|posso|quer|queria|deixa eu)\b.{0,25}\b(passar|mandar|enviar|informar|dar|digitar)\b"
    r".{0,30}\b(dado|cpf|rg|endereco|telefone|celular|e mail|nome|numero|cnh|titulo|foto)",
    r"\b(meu|minha)\s+(endereco|telefone|celular|e ?mail|cep|senha|nome completo)\b",
    r"\b(meu|minha)\s+(cpf|rg|cnh|titulo|pi|ni|identidade)\s+(e|eh)\b",
]


def tem_intencao_de_dados(texto):
    msg = normalizar(texto)
    return any(re.search(p, msg) for p in PADROES_INTENCAO)


def contem_dado_pessoal(texto):
    """Usado na checagem final: a resposta não pode ter dado pessoal."""
    return bool(mascarar_dados(texto)[1])


# ================================================================ prompt injection

# Procurados no texto normalizado (sem acento e pontuação).
PADROES_INJECAO = [
    r"\bignor\w*\b(\s+\w+){0,4}\s+(instruc\w*|regra\w*|orientac\w*|comando\w*|prompt)",
    r"\besquec\w*\b(\s+\w+){0,4}\s+(instruc\w*|regra\w*|tudo)",
    r"\b(mostr|revel|exib|imprim|repit|diga|conte|escrev)\w*\b(\s+\w+){0,4}\s+"
    r"(prompt|instruc\w* (interna|do sistema|inicial|original)|regra\w* interna)",
    r"\bprompt (de|do) sistema\b|\bsystem prompt\b",
    r"\bnova\w* regra\w*\b|\ba partir de agora\b|\bde agora em diante\b",
    r"\b(finja|aja como|atue como|faca de conta|voce agora e|roleplay)\b",
    r"\bmodo (desenvolvedor|dev|deus|admin)\b|\bjailbreak\b",
    r"\b(comece|comecando|inicie|iniciando)\b(\s+\w+){0,3}\s+respost",
    r"\bcaso contrario\b.{0,40}\bnota zero\b",
]

# Procurados no texto "compacto" (sem espaços): pega tentativas com letras
# separadas, como "Responda t odas as perguntas começa ndo a resposta com".
PADROES_COMPACTOS = [
    "ignoreasinstruc", "ignoretodasasinstruc", "promptdesistema", "respondatodasasperguntas",
    "comecandoarespostacom", "comecesuarespostacom", "novaregra", "notazero",
]

# Marcas de papel falso no texto original: [SISTEMA], <system>, ###admin etc.
PADRAO_PAPEL_FALSO = r"(?i)[\[<#{]\s*(sistema|system|admin|desenvolvedor|developer|assistant)\s*[\]>#}:]"


def detectar_injecao(texto):
    """Devolve a lista de regras que dispararam (vazia = sem injeção)."""
    msg = normalizar(texto)
    compacto = compactar(texto)
    disparos = [p for p in PADROES_INJECAO if re.search(p, msg)]
    disparos += [p for p in PADROES_COMPACTOS if p in compacto]
    if re.search(PADRAO_PAPEL_FALSO, texto):
        disparos.append("papel_falso")
    return disparos


def neutralizar(texto):
    """Remove marcas que imitam o sistema e os sinais < > usados nas tags do prompt."""
    texto = re.sub(PADRAO_PAPEL_FALSO, "", texto)
    return texto.replace("<", "(").replace(">", ")").strip()


# ================================================================ limitação

PADROES_LIMITACAO = [
    r"\bcanal oficial\b", r"\bvoce e (o |a |um |uma )?(site |canal |atendimento )?oficial\b",
    r"\bvoce e (da|do) (prefeitura|governo|central)\b", r"\bquem e voce\b",
    r"\bvoce e (um )?(robo|humano|pessoa)\b", r"\bposso confiar\b",
]


def pergunta_sobre_limitacao(texto):
    msg = normalizar(texto)
    return any(re.search(p, msg) for p in PADROES_LIMITACAO)
