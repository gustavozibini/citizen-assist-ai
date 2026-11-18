# Citizen Assist AI - Validação do módulo de decisão lógica
# Gustavo Zibini Belizario - RM 561376 - 1CC
#
# Testa as 16 combinações da tabela-verdade e confirma que
# regra original = forma canônica = expressão simplificada.
# Também testa o tratamento de entradas inválidas do menu.

import builtins
import io
import contextlib
from decisao_logica import (regra_original, expressao_canonica,
                            expressao_simplificada, orientacao, ler_bit)

falhas = 0
print("TABELA-VERDADE EXECUTADA (16 combinações)")
print(" m | A B C D | Regra | Canônica | Simplificada | Igual | Orientação")
print("---+---------+-------+----------+--------------+-------+-----------")
for m in range(16):
    a, b, c, d = (m >> 3) & 1, (m >> 2) & 1, (m >> 1) & 1, m & 1
    r = regra_original(a, b, c, d)
    k = expressao_canonica(a, b, c, d)
    s = expressao_simplificada(a, b, c, d)
    ok = (r == k == s)
    if not ok:
        falhas += 1
    print("%2d | %d %d %d %d |   %d   |    %d     |      %d       |  %s  | %s"
          % (m, a, b, c, d, r, k, s, "OK " if ok else "ERRO", orientacao(a, b, c, d)[:60]))

mintermos = [m for m in range(16)
             if expressao_simplificada((m >> 3) & 1, (m >> 2) & 1, (m >> 1) & 1, m & 1)]
print("\nMintermos com S = 1:", mintermos)
if mintermos != [12, 13, 15]:
    falhas += 1
    print("ERRO: esperado [12, 13, 15]")

print("\nENTRADAS INVÁLIDAS (função ler_bit)")
casos = [
    (["", "2", "abc", "1"], 1, "vazio, número fora de 0/1, texto, depois 1"),
    (["-1", " 0 "], 0, "negativo, depois 0 com espaços"),
    (["sim", "S"], None, "palavra, depois 'S' para sair"),
]
for entradas, esperado, descricao in casos:
    fila = iter(entradas)
    original = builtins.input
    builtins.input = lambda _p="": next(fila)
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        obtido = ler_bit("Pergunta")
    builtins.input = original
    ok = obtido == esperado
    if not ok:
        falhas += 1
    print("Entradas %-26s | esperado %-4s | obtido %-4s | %s  (%s)"
          % (entradas, esperado, obtido, "OK" if ok else "ERRO", descricao))

# Fim de entrada (Ctrl+D) não pode gerar erro técnico
original = builtins.input
def sem_entrada(_p=""):
    raise EOFError
builtins.input = sem_entrada
with contextlib.redirect_stdout(io.StringIO()):
    obtido = ler_bit("Pergunta")
builtins.input = original
print("Fim de entrada (EOF)           | esperado None | obtido %s | %s"
      % (obtido, "OK" if obtido is None else "ERRO"))
if obtido is not None:
    falhas += 1

print("\nRESUMO: %s" % ("TODOS OS TESTES PASSARAM" if falhas == 0 else "%d FALHA(S)" % falhas))
