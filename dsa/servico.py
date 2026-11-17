# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# servico.py
# Representa UM serviço/orientação ao cidadão (o "registro")
# e reúne as regras de validação dos campos.
# ==============================================================

import unicodedata

# Limites de tamanho dos campos. Além de evitar textos absurdos,
# garantem que comparar dois textos tem custo limitado (isso é
# usado como hipótese na análise Big-O da documentação).
LIMITE_TEXTO = 80          # título, categoria, público-alvo e canal
LIMITE_DESCRICAO = 200     # descrição
MAIOR_IDENTIFICADOR = 999999


class Servico:
    """Um serviço ou orientação da central de atendimento."""

    def __init__(self, identificador, titulo, categoria, descricao,
                 publico_alvo, canal):
        self.identificador = identificador   # número inteiro, único na lista
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.publico_alvo = publico_alvo
        self.canal = canal                   # canal ou local de atendimento


def normalizar(texto):
    """Devolve o texto em minúsculas e sem acentos.

    Serve para comparar textos de forma "tolerante": assim
    "SAUDE", "saúde" e "Saúde" são tratados como iguais.
    """
    # A forma NFD separa a letra do acento: "ú" vira "u" + acento.
    separado = unicodedata.normalize("NFD", texto.lower())
    resultado = ""
    for caractere in separado:
        # A categoria "Mn" é a dos acentos soltos; eles ficam de fora.
        if unicodedata.category(caractere) != "Mn":
            resultado = resultado + caractere
    return resultado


def validar_identificador(texto):
    """Confere se o texto digitado serve como identificador.

    Devolve "" (texto vazio) quando está tudo certo ou a mensagem
    de erro quando não está.
    """
    texto = texto.strip()
    if texto == "":
        return "o identificador é obrigatório."
    try:
        numero = int(texto)
    except ValueError:
        # Caiu aqui: o usuário digitou letras, vírgula, ponto etc.
        return "o identificador deve ser um número inteiro (exemplo: 101)."
    if numero < 1 or numero > MAIOR_IDENTIFICADOR:
        return f"o identificador deve estar entre 1 e {MAIOR_IDENTIFICADOR}."
    return ""


def validar_texto(nome_campo, valor, limite):
    """Confere um campo de texto obrigatório.

    Devolve "" quando está tudo certo ou a mensagem de erro.
    """
    valor = valor.strip()
    if valor == "":
        return f"o campo '{nome_campo}' é obrigatório e não pode ficar vazio."
    if len(valor) > limite:
        return (f"o campo '{nome_campo}' aceita no máximo {limite} "
                f"caracteres (foram digitados {len(valor)}).")
    return ""
