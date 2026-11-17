# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# testes.py
# Executa cenários reais contra o código do sistema e mostra,
# para cada um: entrada, resultado esperado, resultado observado
# e a situação (OK ou FALHOU).
#
# Como executar:   python3 testes.py
# ==============================================================

import io
import sys

import main
from servico import Servico, validar_identificador, validar_texto
from servico import LIMITE_TEXTO, LIMITE_DESCRICAO
from lista_encadeada import ListaEncadeada
from algoritmos import pesquisar, ordenar
from dados_exemplo import carregar_exemplos

# Contadores gerais dos testes.
total_cenarios = 0
total_falhas = 0


# ==============================================================
# FUNÇÕES DE APOIO
# ==============================================================

def verificar(descricao, entrada, esperado, observado):
    """Registra um cenário: compara esperado x observado e imprime tudo."""
    global total_cenarios, total_falhas
    total_cenarios = total_cenarios + 1
    codigo = "T" + str(total_cenarios).zfill(2)     # T01, T02, ...

    esperado = str(esperado)
    observado = str(observado)
    if esperado == observado:
        situacao = "OK"
    else:
        situacao = "FALHOU"
        total_falhas = total_falhas + 1

    print(f"[{codigo}] {descricao}")
    print(f"  Entrada  : {entrada}")
    print(f"  Esperado : {esperado}")
    print(f"  Observado: {observado}")
    print(f"  Situação : {situacao}")
    print()


def secao(titulo):
    print("-" * 70)
    print(titulo)
    print("-" * 70)


def novo(identificador, titulo="Serviço de teste", categoria="Teste"):
    """Cria um serviço simples, só para os testes."""
    return Servico(identificador, titulo, categoria, "Descrição de teste",
                   "Público de teste", "Canal de teste")


def lista_com(id1, id2=None, id3=None, id4=None, id5=None):
    """Monta uma lista encadeada com até 5 ids, na ordem informada."""
    lista = ListaEncadeada()
    lista.inserir(novo(id1))
    if id2 is not None:
        lista.inserir(novo(id2))
    if id3 is not None:
        lista.inserir(novo(id3))
    if id4 is not None:
        lista.inserir(novo(id4))
    if id5 is not None:
        lista.inserir(novo(id5))
    return lista


def retrato(lista):
    """Descreve a lista percorrendo os nós um a um.

    Mostra os ids na ordem do encadeamento, o tamanho guardado e o
    id do nó 'fim'. Também confere se o tamanho guardado bate com a
    quantidade de nós realmente encadeados.
    """
    ids = ""
    contados = 0
    atual = lista.inicio
    while atual is not None:
        ids = ids + " " + str(atual.servico.identificador)
        contados = contados + 1
        atual = atual.proximo
    if ids == "":
        ids = " (nenhum)"

    if lista.fim is None:
        fim = "(nenhum)"
    else:
        fim = str(lista.fim.servico.identificador)

    texto = f"ids:{ids} | tamanho: {lista.tamanho} | fim: {fim}"
    if contados != lista.tamanho:
        texto = texto + f"| ERRO: {contados} nós encadeados"
    return texto


def titulos(lista):
    """Devolve os títulos na ordem do encadeamento, separados por ' / '."""
    texto = ""
    atual = lista.inicio
    while atual is not None:
        if texto != "":
            texto = texto + " / "
        texto = texto + atual.servico.titulo
        atual = atual.proximo
    return texto


def esta_ordenada_por_id(lista):
    """Confere, nó a nó, se cada id é menor ou igual ao do nó seguinte."""
    atual = lista.inicio
    while atual is not None and atual.proximo is not None:
        if atual.servico.identificador > atual.proximo.servico.identificador:
            return "não"
        atual = atual.proximo
    return "sim"


def descrever_busca(servico):
    if servico is None:
        return "não encontrado"
    return f"encontrado: [{servico.identificador}] {servico.titulo}"


def mensagem_ou_valido(erro):
    """As funções de validação devolvem "" quando o valor é válido."""
    if erro == "":
        return "válido"
    return erro


class TecladoComCtrlC:
    """Entrada falsa que simula o usuário apertando Ctrl+C."""

    def readline(self):
        raise KeyboardInterrupt

    def isatty(self):
        return False


def rodar_menu(entradas, teclado=None):
    """Executa o menu DE VERDADE e devolve tudo o que ele imprimiu.

    O teclado é trocado por um texto em memória (cada linha é uma
    resposta digitada) e a tela por outro texto, que é devolvido.
    """
    teclado_original = sys.stdin
    tela_original = sys.stdout
    if teclado is None:
        teclado = io.StringIO(entradas)
    sys.stdin = teclado
    sys.stdout = io.StringIO()
    try:
        main.executar_menu()
        saida = sys.stdout.getvalue()
    except Exception as erro:
        # Qualquer erro técnico que escapar do menu reprova o cenário.
        saida = sys.stdout.getvalue() + f"\nERRO TÉCNICO: {erro!r}\n"
    finally:
        sys.stdin = teclado_original
        sys.stdout = tela_original
    return saida


def linha_com(saida, trecho):
    """Devolve a linha da saída do menu que contém o trecho procurado."""
    posicao = saida.find(trecho)
    if posicao == -1:
        if "ERRO TÉCNICO" in saida:
            return linha_com(saida, "ERRO TÉCNICO")
        return "(a mensagem não apareceu)"
    comeco = saida.rfind("\n", 0, posicao) + 1
    final = saida.find("\n", posicao)
    if final == -1:
        final = len(saida)
    return saida[comeco:final].strip()


def contar(saida, trecho):
    """Conta quantas vezes o trecho aparece na saída do menu."""
    return saida.count(trecho)


# ==============================================================
# CENÁRIOS
# ==============================================================

def testes_lista_vazia():
    secao("1. OPERAÇÕES SOBRE LISTA VAZIA")

    lista = ListaEncadeada()
    verificar("Percorrer (listar) uma lista vazia",
              "lista recém-criada; percorrer()",
              "0 nó(s) visitado(s) | ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              f"{lista.percorrer(descrever_busca)} nó(s) visitado(s) | {retrato(lista)}")

    verificar("Consultar por id em lista vazia",
              "buscar_por_id(10)",
              "não encontrado",
              descrever_busca(lista.buscar_por_id(10)))

    verificar("Excluir em lista vazia",
              "remover(10)",
              "não encontrado | ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              f"{descrever_busca(lista.remover(10))} | {retrato(lista)}")

    verificar("Atualizar em lista vazia",
              "atualizar(10, ...)",
              "False",
              lista.atualizar(10, "a", "b", "c", "d", "e"))

    resultado = pesquisar(lista, "titulo", "rg")
    verificar("Pesquisar em lista vazia",
              "pesquisar(titulo, 'rg')",
              "0 resultado(s)",
              f"{resultado.tamanho} resultado(s)")

    ordenar(lista, "titulo")
    verificar("Ordenar lista vazia (não pode dar erro)",
              "ordenar(titulo)",
              "ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              retrato(lista))


def testes_cadastro():
    secao("2. CADASTRO (INSERÇÃO) E VALIDAÇÃO")

    lista = ListaEncadeada()
    inseriu = lista.inserir(novo(30))
    verificar("Inserir o primeiro registro em lista vazia",
              "inserir(id 30)",
              "True | ids: 30 | tamanho: 1 | fim: 30",
              f"{inseriu} | {retrato(lista)}")

    lista.inserir(novo(10))
    lista.inserir(novo(20))
    lista.inserir(novo(40))
    verificar("Inserir mais três registros (cada um entra no fim)",
              "inserir(id 10), inserir(id 20), inserir(id 40)",
              "ids: 30 10 20 40 | tamanho: 4 | fim: 40",
              retrato(lista))

    inseriu = lista.inserir(novo(20, "Outro título"))
    verificar("Recusar identificador duplicado sem alterar a lista",
              "inserir(id 20) com o id 20 já cadastrado",
              "False | ids: 30 10 20 40 | tamanho: 4 | fim: 40",
              f"{inseriu} | {retrato(lista)}")

    verificar("Identificador com texto no lugar de número",
              "validar_identificador('abc')",
              "o identificador deve ser um número inteiro (exemplo: 101).",
              mensagem_ou_valido(validar_identificador("abc")))

    verificar("Identificador com número não inteiro",
              "validar_identificador('3.5')",
              "o identificador deve ser um número inteiro (exemplo: 101).",
              mensagem_ou_valido(validar_identificador("3.5")))

    verificar("Identificador vazio",
              "validar_identificador('')",
              "o identificador é obrigatório.",
              mensagem_ou_valido(validar_identificador("")))

    verificar("Identificador negativo",
              "validar_identificador('-5')",
              "o identificador deve estar entre 1 e 999999.",
              mensagem_ou_valido(validar_identificador("-5")))

    verificar("Identificador zero",
              "validar_identificador('0')",
              "o identificador deve estar entre 1 e 999999.",
              mensagem_ou_valido(validar_identificador("0")))

    verificar("Identificador válido",
              "validar_identificador('25')",
              "válido",
              mensagem_ou_valido(validar_identificador("25")))

    verificar("Campo obrigatório vazio (só espaços)",
              "validar_texto('Título', '   ', 80)",
              "o campo 'Título' é obrigatório e não pode ficar vazio.",
              mensagem_ou_valido(validar_texto("Título", "   ", LIMITE_TEXTO)))

    verificar("Campo de texto acima do limite",
              "validar_texto('Título', 81 letras 'a', 80)",
              "o campo 'Título' aceita no máximo 80 caracteres (foram digitados 81).",
              mensagem_ou_valido(validar_texto("Título", "a" * 81, LIMITE_TEXTO)))

    verificar("Campo de texto válido",
              "validar_texto('Título', 'Renovação da CNH', 80)",
              "válido",
              mensagem_ou_valido(validar_texto("Título", "Renovação da CNH", LIMITE_TEXTO)))

    exemplos = ListaEncadeada()
    inseridos = carregar_exemplos(exemplos)
    verificar("Carregar os registros de exemplo (múltiplos registros)",
              "carregar_exemplos(lista vazia)",
              "15 inseridos | ids: 104 302 102 401 203 106 601 101 501 105 301 "
              "402 103 502 602 | tamanho: 15 | fim: 602",
              f"{inseridos} inseridos | {retrato(exemplos)}")

    inseridos = carregar_exemplos(exemplos)
    verificar("Carregar os exemplos de novo: todos os ids já existem",
              "carregar_exemplos(lista já carregada)",
              "0 inseridos | tamanho: 15",
              f"{inseridos} inseridos | tamanho: {exemplos.tamanho}")

    # Os próprios exemplos precisam respeitar as regras de validação.
    problemas = 0
    atual = exemplos.inicio
    while atual is not None:
        s = atual.servico
        if validar_identificador(str(s.identificador)) != "":
            problemas = problemas + 1
        if validar_texto("Título", s.titulo, LIMITE_TEXTO) != "":
            problemas = problemas + 1
        if validar_texto("Categoria", s.categoria, LIMITE_TEXTO) != "":
            problemas = problemas + 1
        if validar_texto("Descrição", s.descricao, LIMITE_DESCRICAO) != "":
            problemas = problemas + 1
        if validar_texto("Público-alvo", s.publico_alvo, LIMITE_TEXTO) != "":
            problemas = problemas + 1
        if validar_texto("Canal", s.canal, LIMITE_TEXTO) != "":
            problemas = problemas + 1
        atual = atual.proximo
    verificar("Registros de exemplo respeitam as validações",
              "validar os 6 campos dos 15 exemplos",
              "0 problema(s)",
              f"{problemas} problema(s)")


def testes_consulta():
    secao("3. CONSULTA POR IDENTIFICADOR (BUSCA LINEAR)")

    lista = ListaEncadeada()
    carregar_exemplos(lista)

    verificar("Consultar o registro do primeiro nó",
              "buscar_por_id(104)",
              "encontrado: [104] Segunda via da Carteira de Identidade (RG)",
              descrever_busca(lista.buscar_por_id(104)))

    verificar("Consultar um registro do meio da lista",
              "buscar_por_id(101)",
              "encontrado: [101] Carteira de Trabalho digital",
              descrever_busca(lista.buscar_por_id(101)))

    verificar("Consultar o registro do último nó",
              "buscar_por_id(602)",
              "encontrado: [602] Economia de energia em casa",
              descrever_busca(lista.buscar_por_id(602)))

    verificar("Consultar identificador que não existe",
              "buscar_por_id(999)",
              "não encontrado",
              descrever_busca(lista.buscar_por_id(999)))


def testes_atualizacao():
    secao("4. ATUALIZAÇÃO")

    lista = lista_com(30, 10, 20)
    atualizou = lista.atualizar(10, "Título novo", "Categoria nova",
                                "Descrição nova", "Público novo", "Canal novo")
    s = lista.buscar_por_id(10)
    verificar("Atualizar um registro existente",
              "atualizar(10, 'Título novo', 'Categoria nova', ...)",
              "True | Título novo | Categoria nova | Descrição nova | "
              "Público novo | Canal novo",
              f"{atualizou} | {s.titulo} | {s.categoria} | {s.descricao} | "
              f"{s.publico_alvo} | {s.canal}")

    verificar("Atualização não muda a posição nem os outros registros",
              "lista após atualizar(10, ...)",
              "ids: 30 10 20 | tamanho: 3 | fim: 20 | "
              "Serviço de teste / Título novo / Serviço de teste",
              f"{retrato(lista)} | {titulos(lista)}")

    atualizou = lista.atualizar(99, "x", "x", "x", "x", "x")
    verificar("Atualizar identificador que não existe",
              "atualizar(99, ...)",
              "False | ids: 30 10 20 | tamanho: 3 | fim: 20",
              f"{atualizou} | {retrato(lista)}")


def testes_exclusao():
    secao("5. EXCLUSÃO (INÍCIO, MEIO E FIM)")

    lista = lista_com(30, 10, 20, 40, 50)
    removido = lista.remover(30)
    verificar("Excluir o primeiro nó (o início passa a ser o 2º)",
              "lista 30 10 20 40 50; remover(30)",
              "encontrado: [30] Serviço de teste | ids: 10 20 40 50 | tamanho: 4 | fim: 50",
              f"{descrever_busca(removido)} | {retrato(lista)}")

    removido = lista.remover(20)
    verificar("Excluir um nó do meio (o anterior é religado ao seguinte)",
              "lista 10 20 40 50; remover(20)",
              "encontrado: [20] Serviço de teste | ids: 10 40 50 | tamanho: 3 | fim: 50",
              f"{descrever_busca(removido)} | {retrato(lista)}")

    removido = lista.remover(50)
    verificar("Excluir o último nó (o fim passa a ser o anterior)",
              "lista 10 40 50; remover(50)",
              "encontrado: [50] Serviço de teste | ids: 10 40 | tamanho: 2 | fim: 40",
              f"{descrever_busca(removido)} | {retrato(lista)}")

    removido = lista.remover(77)
    verificar("Excluir identificador que não existe",
              "lista 10 40; remover(77)",
              "não encontrado | ids: 10 40 | tamanho: 2 | fim: 40",
              f"{descrever_busca(removido)} | {retrato(lista)}")

    lista.inserir(novo(60))
    verificar("Inserir depois de excluir o último (o novo fim funciona)",
              "lista 10 40; inserir(id 60)",
              "ids: 10 40 60 | tamanho: 3 | fim: 60",
              retrato(lista))

    lista.remover(10)
    lista.remover(40)
    lista.remover(60)
    verificar("Excluir todos os registros: a lista volta a ficar vazia",
              "remover(10), remover(40), remover(60)",
              "vazia: True | ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              f"vazia: {lista.esta_vazia()} | {retrato(lista)}")

    lista.inserir(novo(5))
    verificar("Inserir de novo depois de esvaziar a lista",
              "inserir(id 5)",
              "ids: 5 | tamanho: 1 | fim: 5",
              retrato(lista))


def testes_pesquisa():
    secao("6. PESQUISA POR TÍTULO E POR CATEGORIA")

    lista = ListaEncadeada()
    carregar_exemplos(lista)

    verificar("Pesquisar no título, sem acento e em minúsculas",
              "pesquisar(titulo, 'certidoes')",
              "ids: 105 | tamanho: 1 | fim: 105",
              retrato(pesquisar(lista, "titulo", "certidoes")))

    verificar("Pesquisar no título, em maiúsculas, com mais de um resultado",
              "pesquisar(titulo, 'CARTEIRA')",
              "ids: 104 101 | tamanho: 2 | fim: 101",
              retrato(pesquisar(lista, "titulo", "CARTEIRA")))

    verificar("Pesquisar na categoria ignorando o acento",
              "pesquisar(categoria, 'saude')",
              "ids: 401 402 | tamanho: 2 | fim: 402",
              retrato(pesquisar(lista, "categoria", "saude")))

    verificar("Pesquisar na categoria por parte da palavra",
              "pesquisar(categoria, 'DOCUM')",
              "ids: 104 102 106 101 105 103 | tamanho: 6 | fim: 103",
              retrato(pesquisar(lista, "categoria", "DOCUM")))

    verificar("Pesquisar um trecho que não existe",
              "pesquisar(titulo, 'xyz')",
              "ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              retrato(pesquisar(lista, "titulo", "xyz")))

    verificar("Pesquisar com trecho vazio não devolve a lista inteira",
              "pesquisar(titulo, '   ')",
              "ids: (nenhum) | tamanho: 0 | fim: (nenhum)",
              retrato(pesquisar(lista, "titulo", "   ")))

    verificar("A pesquisa não altera a lista original",
              "lista original depois das pesquisas acima",
              "ids: 104 302 102 401 203 106 601 101 501 105 301 402 103 502 602 "
              "| tamanho: 15 | fim: 602",
              retrato(lista))


def testes_ordenacao():
    secao("7. ORDENAÇÃO (MERGE SORT NA LISTA ENCADEADA)")

    lista = ListaEncadeada()
    carregar_exemplos(lista)

    ordenar(lista, "identificador")
    verificar("Ordenar os 15 exemplos por identificador",
              "ordenar(identificador)",
              "ids: 101 102 103 104 105 106 203 301 302 401 402 501 502 601 602 "
              "| tamanho: 15 | fim: 602",
              retrato(lista))

    ordenar(lista, "titulo")
    verificar("Ordenar os 15 exemplos por título (ordem alfabética)",
              "ordenar(titulo)",
              "ids: 402 203 101 105 602 301 102 302 502 501 103 104 601 106 401 "
              "| tamanho: 15 | fim: 401",
              retrato(lista))

    pequena = ListaEncadeada()
    pequena.inserir(novo(1, "Zeladoria"))
    pequena.inserir(novo(2, "água e esgoto"))
    pequena.inserir(novo(3, "Biblioteca"))
    pequena.inserir(novo(4, "Ônibus"))
    pequena.inserir(novo(5, "energia"))
    ordenar(pequena, "titulo")
    verificar("Ordenar por título ignorando acentos e maiúsculas",
              "títulos: Zeladoria, água e esgoto, Biblioteca, Ônibus, energia",
              "água e esgoto / Biblioteca / energia / Ônibus / Zeladoria",
              titulos(pequena))

    um = lista_com(7)
    ordenar(um, "identificador")
    verificar("Ordenar lista com um único registro",
              "lista 7; ordenar(identificador)",
              "ids: 7 | tamanho: 1 | fim: 7",
              retrato(um))

    dois = lista_com(9, 4)
    ordenar(dois, "identificador")
    verificar("Ordenar lista com dois registros",
              "lista 9 4; ordenar(identificador)",
              "ids: 4 9 | tamanho: 2 | fim: 9",
              retrato(dois))

    em_ordem = lista_com(1, 2, 3, 4, 5)
    ordenar(em_ordem, "identificador")
    verificar("Ordenar lista que já está em ordem",
              "lista 1 2 3 4 5; ordenar(identificador)",
              "ids: 1 2 3 4 5 | tamanho: 5 | fim: 5",
              retrato(em_ordem))

    invertida = lista_com(5, 4, 3, 2, 1)
    ordenar(invertida, "identificador")
    verificar("Ordenar lista em ordem invertida",
              "lista 5 4 3 2 1; ordenar(identificador)",
              "ids: 1 2 3 4 5 | tamanho: 5 | fim: 5",
              retrato(invertida))

    invertida.inserir(novo(6))
    removido = invertida.remover(1)
    verificar("Inserir e excluir depois de ordenar (início e fim corretos)",
              "lista ordenada 1 2 3 4 5; inserir(id 6); remover(1)",
              "encontrado: [1] Serviço de teste | ids: 2 3 4 5 6 | tamanho: 5 | fim: 6",
              f"{descrever_busca(removido)} | {retrato(invertida)}")

    # Lista grande com ids embaralhados por uma conta simples:
    # como 211 é primo, (i * 37) % 211 nunca repete para i de 0 a 199.
    grande = ListaEncadeada()
    for i in range(200):
        grande.inserir(novo((i * 37) % 211 + 1))
    antes = esta_ordenada_por_id(grande)
    ordenar(grande, "identificador")
    verificar("Ordenar 200 registros embaralhados",
              "200 ids gerados por (i * 37) % 211 + 1; ordenar(identificador)",
              "antes ordenada: não | depois ordenada: sim | tamanho: 200 | "
              "primeiro: 1 | fim: 211",
              f"antes ordenada: {antes} | depois ordenada: "
              f"{esta_ordenada_por_id(grande)} | tamanho: {grande.tamanho} | "
              f"primeiro: {grande.inicio.servico.identificador} | "
              f"fim: {grande.fim.servico.identificador}")


def testes_menu():
    secao("8. MENU INTERATIVO E ENTRADAS INVÁLIDAS (menu executado de verdade)")

    saida = rodar_menu("99\n0\n")
    verificar("Opção de menu inexistente",
              "teclado: 99, 0",
              "Opção inválida: digite um número de 0 a 8.",
              linha_com(saida, "Opção inválida"))

    saida = rodar_menu("abc\n0\n")
    verificar("Texto no lugar do número da opção",
              "teclado: abc, 0",
              "Opção inválida: digite um número de 0 a 8.",
              linha_com(saida, "Opção inválida"))

    saida = rodar_menu("\n0\n")
    verificar("Opção em branco (só Enter)",
              "teclado: (Enter), 0",
              "Opção inválida: digite um número de 0 a 8.",
              linha_com(saida, "Opção inválida"))

    saida = rodar_menu("2\n0\n")
    verificar("Listar com a lista vazia",
              "teclado: 2, 0",
              "Lista vazia: nenhum serviço cadastrado.",
              linha_com(saida, "Lista vazia"))

    saida = rodar_menu("5\n0\n")
    verificar("Excluir com a lista vazia",
              "teclado: 5, 0",
              "Lista vazia: nenhum serviço cadastrado.",
              linha_com(saida, "Lista vazia"))

    saida = rodar_menu("8\n3\nabc\n0\n")
    verificar("Consulta com texto no lugar do identificador",
              "teclado: 8, 3, abc, 0",
              "Entrada inválida: o identificador deve ser um número inteiro (exemplo: 101).",
              linha_com(saida, "Entrada inválida"))

    saida = rodar_menu("8\n3\n999\n0\n")
    verificar("Consulta de identificador que não existe",
              "teclado: 8, 3, 999, 0",
              "Registro não encontrado: não existe serviço com o id 999.",
              linha_com(saida, "Registro não encontrado"))

    saida = rodar_menu("8\n1\n104\n0\n")
    verificar("Cadastro com identificador duplicado",
              "teclado: 8, 1, 104, 0",
              "Identificador duplicado: já existe um serviço com o id 104.",
              linha_com(saida, "Identificador duplicado"))

    saida = rodar_menu("1\n700\n\nHorta comunitária\nAtendimento comunitário\n"
                       "Canteiros coletivos no bairro\nMoradores\n"
                       "Praça central\n3\n700\n0\n")
    verificar("Cadastro com título vazio: o menu avisa e pergunta de novo",
              "teclado: 1, 700, (Enter), Horta comunitária, ...",
              "Entrada inválida: o campo 'Título' é obrigatório e não pode ficar vazio.",
              linha_com(saida, "Entrada inválida"))

    verificar("Mesmo cadastro, depois de corrigir o título: registro gravado",
              "continuação: ..., Praça central; depois 3, 700, 0",
              "Serviço 700 cadastrado com sucesso. | [700] Horta comunitária",
              f"{linha_com(saida, 'cadastrado com sucesso')} | "
              f"{linha_com(saida, '[700]')}")

    saida = rodar_menu("8\n4\n103\n\n\n\n\nBalcão 7\n3\n103\n0\n")
    verificar("Atualizar pelo menu só o canal (Enter mantém os outros campos)",
              "teclado: 8, 4, 103, (Enter) x4, Balcão 7, 3, 103, 0",
              "Serviço 103 atualizado com sucesso. | Canal ou local: Balcão 7 | "
              "[103] Renovação da CNH",
              f"{linha_com(saida, 'atualizado com sucesso')} | "
              f"{linha_com(saida, 'Canal ou local: Balcão 7')} | "
              f"{linha_com(saida, '[103]')}")

    saida = rodar_menu("8\n5\n104\ntalvez\ns\n3\n104\n0\n")
    verificar("Exclusão com resposta inválida na confirmação e depois 's'",
              "teclado: 8, 5, 104, talvez, s, 3, 104, 0",
              "Resposta inválida: digite s para sim ou n para não. | "
              "Serviço 104 excluído. Restam 14 serviço(s). | "
              "Registro não encontrado: não existe serviço com o id 104.",
              f"{linha_com(saida, 'Resposta inválida')} | "
              f"{linha_com(saida, 'excluído')} | "
              f"{linha_com(saida, 'Registro não encontrado')}")

    saida = rodar_menu("8\n5\n104\nn\n0\n")
    verificar("Exclusão cancelada com 'n'",
              "teclado: 8, 5, 104, n, 0",
              "Exclusão cancelada. Nada foi alterado.",
              linha_com(saida, "Exclusão cancelada"))

    saida = rodar_menu("8\n6\n1\nzzz\n0\n")
    verificar("Pesquisa pelo menu sem resultados",
              "teclado: 8, 6, 1, zzz, 0",
              "Nenhum serviço encontrado com 'zzz' em título.",
              linha_com(saida, "Nenhum serviço encontrado"))

    saida = rodar_menu("8\n6\n2\nEDUCACAO\n0\n")
    verificar("Pesquisa pelo menu por categoria",
              "teclado: 8, 6, 2, EDUCACAO, 0",
              "Total: 2 serviço(s). | [302] Matrícula na rede municipal de ensino | "
              "[301] Educação de Jovens e Adultos (EJA)",
              f"{linha_com(saida, 'Total:')} | {linha_com(saida, '[302]')} | "
              f"{linha_com(saida, '[301]')}")

    saida = rodar_menu("8\n7\n5\n0\n")
    verificar("Critério de ordenação inexistente",
              "teclado: 8, 7, 5, 0",
              "Opção inválida: digite 1 ou 2.",
              linha_com(saida, "Opção inválida"))

    saida = rodar_menu("8\n7\n2\n0\n")
    primeiro = saida.find("[101]")
    ultimo = saida.find("[602]")
    verificar("Ordenar pelo menu por identificador",
              "teclado: 8, 7, 2, 0",
              "Lista ordenada por identificador: | [101] aparece antes de [602]: True",
              f"{linha_com(saida, 'Lista ordenada')} | "
              f"[101] aparece antes de [602]: {-1 < primeiro < ultimo}")

    saida = rodar_menu("8\n8\n0\n")
    verificar("Carregar exemplos duas vezes: ids repetidos são ignorados",
              "teclado: 8, 8, 0",
              "15 não entraram porque o identificador já estava em uso.",
              linha_com(saida, "não entraram"))

    saida = rodar_menu("0\n")
    verificar("Sair pelo menu e aviso de protótipo educacional",
              "teclado: 0",
              "AVISO: protótipo educacional com dados FICTÍCIOS. | "
              "Sistema encerrado. Até logo!",
              f"{linha_com(saida, 'AVISO')} | {linha_com(saida, 'Sistema encerrado')}")

    saida = rodar_menu("8\n1\n")
    verificar("Fim da entrada (EOF / Ctrl+D) no meio de um cadastro",
              "teclado: 8, 1 e a entrada termina",
              "Entrada encerrada. Sistema encerrado. | erros técnicos: 0",
              f"{linha_com(saida, 'Entrada encerrada')} | "
              f"erros técnicos: {contar(saida, 'ERRO TÉCNICO')}")

    saida = rodar_menu("", TecladoComCtrlC())
    verificar("Ctrl+C durante a leitura da opção",
              "teclado: Ctrl+C (KeyboardInterrupt simulado)",
              "Programa interrompido pelo usuário (Ctrl+C). Sistema encerrado. | "
              "erros técnicos: 0",
              f"{linha_com(saida, 'Programa interrompido')} | "
              f"erros técnicos: {contar(saida, 'ERRO TÉCNICO')}")


# ==============================================================
# EXECUÇÃO
# ==============================================================

def executar_testes():
    print("=" * 70)
    print("TESTES DO SISTEMA - Citizen Assist AI (DSA)")
    print("Aluno: Gustavo Zibini Belizario - RM 561376")
    print("=" * 70)
    print()

    testes_lista_vazia()
    testes_cadastro()
    testes_consulta()
    testes_atualizacao()
    testes_exclusao()
    testes_pesquisa()
    testes_ordenacao()
    testes_menu()

    print("=" * 70)
    print(f"RESUMO: {total_cenarios} cenários executados | "
          f"{total_cenarios - total_falhas} OK | {total_falhas} FALHOU")
    print("=" * 70)


if __name__ == "__main__":
    executar_testes()
    if total_falhas > 0:
        sys.exit(1)     # avisa o sistema operacional que houve falha
