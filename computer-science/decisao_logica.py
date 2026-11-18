# Citizen Assist AI - Módulo de decisão lógica (Computer Science)
# Gustavo Zibini Belizario - RM 561376 - 1CC
#
# Pergunta respondida: "O cidadão pode ser atendido no balcão agora?"
# Regras da ficha FC-07 (Central do Cidadão de Aurora, versão 01/10/2026):
#   - atendimento presencial de segunda a sexta, das 8h às 17h;
#   - agendamento obrigatório para RG (FC-01) e CNH (FC-06).
#
# Variáveis (1 / 0):
#   A = é dia útil (seg a sex)            / sábado, domingo ou feriado
#   B = está entre 8h e 17h               / fora do horário
#   C = serviço exige agendamento (RG/CNH)/ não exige
#   D = tem agendamento marcado           / não tem
# Saída:
#   S = 1 pode ser atendido agora         / 0 não pode (mostra o motivo)
#
# Expressão simplificada: S = A . B . (C' + D)

AVISO = ("Protótipo educacional: não é canal oficial e não confirma atendimento, "
         "serviços ou direitos. Fonte: ficha FC-07, versão de 01/10/2026 (material didático).")


def regra_original(a, b, c, d):
    """Regra escrita como na ficha, sem simplificar."""
    horario_ok = (a == 1 and b == 1)
    agendamento_ok = (c == 0) or (c == 1 and d == 1)
    return 1 if (horario_ok and agendamento_ok) else 0


def expressao_canonica(a, b, c, d):
    """Soma de mintermos: S = m12 + m13 + m15 = AB C'D' + AB C'D + ABCD."""
    na, nb, nc, nd = 1 - a, 1 - b, 1 - c, 1 - d
    m12 = a & b & nc & nd
    m13 = a & b & nc & d
    m15 = a & b & c & d
    return m12 | m13 | m15


def expressao_simplificada(a, b, c, d):
    """S = A . B . (C' + D)"""
    return a & b & ((1 - c) | d)


def orientacao(a, b, c, d):
    """Texto mostrado ao cidadão. O cálculo do SIM/NÃO usa só a expressão simplificada."""
    if expressao_simplificada(a, b, c, d) == 1:
        if c == 1:
            return "Pode ser atendido agora. Leve o documento original com foto e o comprovante do agendamento."
        return "Pode ser atendido agora. Leve o documento original com foto."
    # S = 0: explica o motivo (pode haver mais de um)
    motivos = []
    if a == 0:
        motivos.append("Não há atendimento aos sábados, domingos e feriados. Volte em um dia útil.")
    if b == 0:
        motivos.append("O balcão funciona das 8h às 17h.")
    if c == 1 and d == 0:
        motivos.append("RG e CNH exigem agendamento prévio pelo portal da Central do Cidadão.")
    return "Não pode ser atendido agora. " + " ".join(motivos)


def ler_bit(pergunta):
    """Lê 0 ou 1. Repete em caso de entrada inválida. Devolve None se o usuário sair."""
    while True:
        try:
            texto = input(pergunta + " [1 = sim / 0 = não / s = sair]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if texto in ("s", "sair"):
            return None
        if texto in ("0", "1"):
            return int(texto)
        if texto == "":
            print("  Entrada vazia. Digite 1 ou 0.")
        else:
            print("  Entrada inválida (%r). Digite apenas 1 ou 0." % texto[:20])


def executar_menu():
    print("=" * 60)
    print("CITIZEN ASSIST AI - Posso ser atendido no balcão agora?")
    print(AVISO)
    print("Não informe dados pessoais: basta responder sim ou não.")
    print("=" * 60)
    while True:
        a = ler_bit("Hoje é dia útil (segunda a sexta, sem feriado)?")
        if a is None:
            break
        b = ler_bit("Agora está entre 8h e 17h?")
        if b is None:
            break
        c = ler_bit("O serviço é RG ou CNH (exige agendamento)?")
        if c is None:
            break
        d = 0
        if c == 1:
            d = ler_bit("Você tem agendamento marcado?")
            if d is None:
                break
        s = expressao_simplificada(a, b, c, d)
        print("\nEntradas: A=%d B=%d C=%d D=%d  ->  S=%d" % (a, b, c, d, s))
        print(orientacao(a, b, c, d))
        print("-" * 60)
    print("Encerrado. " + AVISO)


if __name__ == "__main__":
    executar_menu()
