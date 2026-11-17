# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# algoritmos.py
# Algoritmos de PESQUISA (por título ou categoria) e de
# ORDENAÇÃO (merge sort) que trabalham direto nos nós da lista
# encadeada. Nada de sorted(), list.sort() ou conversão para list.
#
# Obs.: a busca por identificador fica em lista_encadeada.py
# (método buscar_por_id), porque a própria lista precisa dela
# para inserir e atualizar.
# ==============================================================

from lista_encadeada import ListaEncadeada
from servico import normalizar


# ==============================================================
# PESQUISA POR ATRIBUTO (busca linear)
# ==============================================================

def pesquisar(lista, campo, trecho):
    """Procura os serviços cujo título ou categoria contém o trecho.

    campo  : "titulo" ou "categoria"
    trecho : texto procurado (maiúsculas e acentos são ignorados)

    Devolve OUTRA lista encadeada com os serviços encontrados, na
    mesma ordem em que aparecem na lista original.
    """
    resultado = ListaEncadeada()
    procurado = normalizar(trecho.strip())
    if procurado == "":
        return resultado    # sem trecho não há o que procurar

    # Vários serviços podem combinar, então é preciso visitar
    # TODOS os nós (não dá para parar no primeiro encontrado).
    atual = lista.inicio
    while atual is not None:
        if campo == "titulo":
            texto = atual.servico.titulo
        else:
            texto = atual.servico.categoria
        if procurado in normalizar(texto):
            resultado.anexar_no_fim(atual.servico)
        atual = atual.proximo
    return resultado


# ==============================================================
# ORDENAÇÃO: MERGE SORT PARA LISTA ENCADEADA
#
# Ideia (dividir para conquistar):
#   1. corta a lista ao meio;
#   2. ordena cada metade (chamando a si mesmo);
#   3. intercala as duas metades já ordenadas.
# Nenhum nó novo é criado: só as ligações "proximo" são refeitas.
# ==============================================================

def vem_antes(servico_a, servico_b, criterio):
    """Diz se servico_a deve ficar antes de servico_b (ou empata).

    criterio: "titulo" (ordem alfabética) ou "identificador" (numérica).
    """
    if criterio == "titulo":
        # normalizar() faz "água" ficar junto do "a" e não depois do "z"
        return normalizar(servico_a.titulo) <= normalizar(servico_b.titulo)
    return servico_a.identificador <= servico_b.identificador


def dividir_ao_meio(inicio):
    """Corta a sequência de nós em duas e devolve o início da 2ª metade.

    Usa dois "ponteiros": o lento anda 1 nó por vez e o rápido 2.
    Quando o rápido chega ao fim, o lento está no meio.
    """
    lento = inicio
    rapido = inicio.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    segunda_metade = lento.proximo
    lento.proximo = None        # aqui a lista é cortada em duas
    return segunda_metade


def intercalar(a, b, criterio):
    """Junta duas sequências JÁ ordenadas em uma só, também ordenada.

    'a' e 'b' são os primeiros nós de cada sequência (nunca None).
    Devolve o primeiro nó da sequência resultante.
    """
    # Escolhe quem será o primeiro nó do resultado.
    if vem_antes(a.servico, b.servico, criterio):
        primeiro = a
        a = a.proximo
    else:
        primeiro = b
        b = b.proximo

    # 'ultimo' é sempre o último nó já colocado no resultado.
    ultimo = primeiro
    while a is not None and b is not None:
        # Em caso de empate entra o nó de 'a' (que vinha antes),
        # então a ordenação é estável.
        if vem_antes(a.servico, b.servico, criterio):
            ultimo.proximo = a
            a = a.proximo
        else:
            ultimo.proximo = b
            b = b.proximo
        ultimo = ultimo.proximo

    # Uma das sequências acabou: o que sobrou da outra já está em ordem.
    if a is not None:
        ultimo.proximo = a
    else:
        ultimo.proximo = b
    return primeiro


def merge_sort(inicio, criterio):
    """Ordena a sequência que começa em 'inicio'; devolve o novo 1º nó."""
    # Caso base: sequência vazia ou com 1 nó já está ordenada.
    if inicio is None or inicio.proximo is None:
        return inicio

    segunda_metade = dividir_ao_meio(inicio)
    esquerda = merge_sort(inicio, criterio)
    direita = merge_sort(segunda_metade, criterio)
    return intercalar(esquerda, direita, criterio)


def ordenar(lista, criterio):
    """Ordena a própria lista encadeada (não cria outra lista).

    criterio: "titulo" ou "identificador".
    """
    lista.inicio = merge_sort(lista.inicio, criterio)

    # A ordem dos nós mudou, então o último nó pode ser outro:
    # percorre uma vez para acertar a referência 'fim'.
    lista.fim = None
    atual = lista.inicio
    while atual is not None:
        lista.fim = atual
        atual = atual.proximo
