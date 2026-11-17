# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# lista_encadeada.py
# Estrutura principal de armazenamento do sistema: uma lista
# simplesmente encadeada, feita à mão (sem usar list do Python).
#
#   inicio                                   fim
#     |                                       |
#     v                                       v
#   [servico|proximo] -> [servico|proximo] -> [servico|proximo] -> None
# ==============================================================


class No:
    """Um elo da lista: guarda um serviço e aponta para o próximo nó."""

    def __init__(self, servico):
        self.servico = servico
        self.proximo = None     # None = este é o último nó


class ListaEncadeada:
    """Lista simplesmente encadeada de serviços."""

    def __init__(self):
        self.inicio = None      # primeiro nó (None = lista vazia)
        self.fim = None         # último nó; evita percorrer tudo para anexar
        self.tamanho = 0        # quantidade de nós

    def esta_vazia(self):
        return self.inicio is None

    # ---------------- BUSCA POR IDENTIFICADOR ----------------
    def buscar_por_id(self, identificador):
        """Busca linear (sequencial): olha nó por nó até achar o id.

        Devolve o serviço encontrado ou None se não existir.
        """
        atual = self.inicio
        while atual is not None:
            if atual.servico.identificador == identificador:
                return atual.servico
            atual = atual.proximo
        return None

    # ----------------------- INSERÇÃO ------------------------
    def anexar_no_fim(self, servico):
        """Liga um novo nó depois do último. NÃO confere id duplicado.

        Uso interno: é chamado por inserir() e para montar a lista
        de resultados de uma pesquisa.
        """
        novo = No(servico)
        if self.esta_vazia():
            self.inicio = novo          # lista vazia: o novo nó é o primeiro...
        else:
            self.fim.proximo = novo     # ...senão o antigo último aponta para ele
        self.fim = novo
        self.tamanho = self.tamanho + 1

    def inserir(self, servico):
        """Cadastra um serviço no fim da lista.

        Antes percorre a lista para garantir que o identificador
        ainda não existe. Devolve True se inseriu e False se o
        identificador já estava em uso (nesse caso nada muda).
        """
        if self.buscar_por_id(servico.identificador) is not None:
            return False
        self.anexar_no_fim(servico)
        return True

    # ----------------------- PERCURSO ------------------------
    def percorrer(self, acao):
        """Visita todos os nós, do primeiro ao último.

        'acao' é uma função que recebe um serviço (por exemplo, a
        função que mostra o serviço na tela). Devolve quantos nós
        foram visitados.
        """
        visitados = 0
        atual = self.inicio
        while atual is not None:
            acao(atual.servico)
            visitados = visitados + 1
            atual = atual.proximo
        return visitados

    # ---------------------- ATUALIZAÇÃO ----------------------
    def atualizar(self, identificador, titulo, categoria, descricao,
                  publico_alvo, canal):
        """Troca os dados do serviço que tem o identificador informado.

        O identificador em si não muda (ele é a "chave" do registro).
        Devolve True se atualizou e False se o id não foi encontrado.
        """
        servico = self.buscar_por_id(identificador)
        if servico is None:
            return False
        servico.titulo = titulo
        servico.categoria = categoria
        servico.descricao = descricao
        servico.publico_alvo = publico_alvo
        servico.canal = canal
        return True

    # ------------------------ REMOÇÃO ------------------------
    def remover(self, identificador):
        """Remove o nó que guarda o identificador informado.

        Devolve o serviço removido ou None se não encontrou
        (o que inclui o caso da lista vazia).
        """
        anterior = None
        atual = self.inicio
        # Anda guardando o nó anterior: é ele que será religado.
        while atual is not None and atual.servico.identificador != identificador:
            anterior = atual
            atual = atual.proximo

        if atual is None:
            return None

        if anterior is None:
            self.inicio = atual.proximo         # removeu o primeiro nó
        else:
            anterior.proximo = atual.proximo    # o anterior "pula" o removido

        if atual is self.fim:
            self.fim = anterior                 # removeu o último nó

        atual.proximo = None    # o nó removido não aponta mais para a lista
        self.tamanho = self.tamanho - 1
        return atual.servico
