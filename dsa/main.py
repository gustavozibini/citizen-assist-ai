# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# main.py
# Menu interativo de terminal para gerenciar os serviços e
# orientações ao cidadão guardados na lista encadeada.
#
# Como executar:   python3 main.py
# ==============================================================

import sys

from servico import Servico, validar_identificador, validar_texto
from servico import LIMITE_TEXTO, LIMITE_DESCRICAO
from lista_encadeada import ListaEncadeada
from algoritmos import pesquisar, ordenar
from dados_exemplo import carregar_exemplos, TOTAL_EXEMPLOS

LINHA = "=" * 64


# ==============================================================
# FUNÇÕES DE ENTRADA (teclado)
# ==============================================================

def ler(rotulo):
    """Lê uma linha do teclado, sem espaços nas pontas."""
    texto = input(rotulo)
    # Quando a entrada vem de um arquivo (testes automáticos), o que
    # foi "digitado" não aparece na tela. Mostrar aqui deixa a sessão
    # gravada nas evidências igual à de um uso real.
    if not sys.stdin.isatty():
        print(texto)
    return texto.strip()


def ler_identificador():
    """Lê um identificador. Devolve o número ou None se for inválido."""
    texto = ler("Identificador (número inteiro): ")
    erro = validar_identificador(texto)
    if erro != "":
        print("Entrada inválida: " + erro)
        return None
    return int(texto)


def ler_campo_obrigatorio(nome_campo, limite):
    """Repete a pergunta até o usuário digitar um texto válido."""
    while True:
        valor = ler(nome_campo + ": ")
        erro = validar_texto(nome_campo, valor, limite)
        if erro == "":
            return valor
        print("Entrada inválida: " + erro)


def ler_campo_para_atualizar(nome_campo, valor_atual, limite):
    """Na atualização, Enter (vazio) mantém o valor que já existe."""
    while True:
        valor = ler(f"{nome_campo} (Enter mantém o atual): ")
        if valor == "":
            return valor_atual
        erro = validar_texto(nome_campo, valor, limite)
        if erro == "":
            return valor
        print("Entrada inválida: " + erro)


def confirmar(pergunta):
    """Pergunta de sim ou não. Devolve True para 's' e False para 'n'."""
    while True:
        resposta = ler(pergunta + " (s/n): ").lower()
        if resposta == "s":
            return True
        if resposta == "n":
            return False
        print("Resposta inválida: digite s para sim ou n para não.")


# ==============================================================
# FUNÇÕES DE SAÍDA (tela)
# ==============================================================

def mostrar_servico(servico):
    print(f"[{servico.identificador}] {servico.titulo}")
    print(f"    Categoria     : {servico.categoria}")
    print(f"    Descrição     : {servico.descricao}")
    print(f"    Público-alvo  : {servico.publico_alvo}")
    print(f"    Canal ou local: {servico.canal}")


def mostrar_lista(lista):
    """Mostra todos os serviços, na ordem em que estão encadeados."""
    total = lista.percorrer(mostrar_servico)
    print(f"Total: {total} serviço(s).")


def mostrar_menu():
    # Menu em formato compacto para caber inteiro na tela junto
    # com o resultado da última operação.
    print()
    print(LINHA)
    print(" MENU - Citizen Assist AI (serviços e orientações ao cidadão)")
    print("  1 Cadastrar    2 Listar todos        3 Consultar por id")
    print("  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)")
    print("  7 Ordenar      8 Carregar exemplos   0 Sair")
    print(LINHA)


# ==============================================================
# OPÇÕES DO MENU
# ==============================================================

def opcao_cadastrar(lista):
    print("--- Cadastrar serviço ---")
    print("Cadastre apenas informações do serviço. Não digite dados")
    print("pessoais (nome, CPF, telefone ou endereço de pessoas).")

    identificador = ler_identificador()
    if identificador is None:
        return
    # Confere o id logo no começo, para o usuário não preencher
    # todos os campos e só então descobrir que o id já existe.
    if lista.buscar_por_id(identificador) is not None:
        print(f"Identificador duplicado: já existe um serviço com o id {identificador}.")
        return

    titulo = ler_campo_obrigatorio("Título", LIMITE_TEXTO)
    categoria = ler_campo_obrigatorio("Categoria", LIMITE_TEXTO)
    descricao = ler_campo_obrigatorio("Descrição", LIMITE_DESCRICAO)
    publico_alvo = ler_campo_obrigatorio("Público-alvo", LIMITE_TEXTO)
    canal = ler_campo_obrigatorio("Canal ou local de atendimento", LIMITE_TEXTO)

    servico = Servico(identificador, titulo, categoria, descricao,
                      publico_alvo, canal)
    if lista.inserir(servico):
        print(f"Serviço {identificador} cadastrado com sucesso.")
    else:
        # Não deve acontecer (já conferimos acima), mas a lista
        # também se protege contra identificador repetido.
        print(f"Identificador duplicado: já existe um serviço com o id {identificador}.")


def opcao_listar(lista):
    print("--- Listar todos os serviços ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    mostrar_lista(lista)


def opcao_consultar(lista):
    print("--- Consultar serviço pelo identificador ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    identificador = ler_identificador()
    if identificador is None:
        return
    servico = lista.buscar_por_id(identificador)
    if servico is None:
        print(f"Registro não encontrado: não existe serviço com o id {identificador}.")
        return
    mostrar_servico(servico)


def opcao_atualizar(lista):
    print("--- Atualizar serviço ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    identificador = ler_identificador()
    if identificador is None:
        return
    servico = lista.buscar_por_id(identificador)
    if servico is None:
        print(f"Registro não encontrado: não existe serviço com o id {identificador}.")
        return

    print("Dados atuais:")
    mostrar_servico(servico)
    print("Digite os novos dados. O identificador não pode ser alterado.")
    titulo = ler_campo_para_atualizar("Título", servico.titulo, LIMITE_TEXTO)
    categoria = ler_campo_para_atualizar("Categoria", servico.categoria, LIMITE_TEXTO)
    descricao = ler_campo_para_atualizar("Descrição", servico.descricao, LIMITE_DESCRICAO)
    publico_alvo = ler_campo_para_atualizar("Público-alvo", servico.publico_alvo, LIMITE_TEXTO)
    canal = ler_campo_para_atualizar("Canal ou local de atendimento", servico.canal, LIMITE_TEXTO)

    lista.atualizar(identificador, titulo, categoria, descricao,
                    publico_alvo, canal)
    print(f"Serviço {identificador} atualizado com sucesso.")
    mostrar_servico(servico)


def opcao_excluir(lista):
    print("--- Excluir serviço ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    identificador = ler_identificador()
    if identificador is None:
        return
    servico = lista.buscar_por_id(identificador)
    if servico is None:
        print(f"Registro não encontrado: não existe serviço com o id {identificador}.")
        return

    mostrar_servico(servico)
    if confirmar("Confirma a exclusão deste serviço?"):
        lista.remover(identificador)
        print(f"Serviço {identificador} excluído. Restam {lista.tamanho} serviço(s).")
    else:
        print("Exclusão cancelada. Nada foi alterado.")


def opcao_pesquisar(lista):
    print("--- Pesquisar por título ou categoria ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    print(" 1 - Pesquisar no título")
    print(" 2 - Pesquisar na categoria")
    escolha = ler("Onde pesquisar: ")
    if escolha == "1":
        campo = "titulo"
        nome_campo = "título"
    elif escolha == "2":
        campo = "categoria"
        nome_campo = "categoria"
    else:
        print("Opção inválida: digite 1 ou 2.")
        return

    trecho = ler_campo_obrigatorio("Trecho procurado", LIMITE_TEXTO)
    encontrados = pesquisar(lista, campo, trecho)
    if encontrados.esta_vazia():
        print(f"Nenhum serviço encontrado com '{trecho}' em {nome_campo}.")
        return
    print(f"Serviços com '{trecho}' em {nome_campo}:")
    mostrar_lista(encontrados)


def opcao_ordenar(lista):
    print("--- Ordenar serviços ---")
    if lista.esta_vazia():
        print("Lista vazia: nenhum serviço cadastrado.")
        return
    print(" 1 - Por título (ordem alfabética)")
    print(" 2 - Por identificador (ordem crescente)")
    escolha = ler("Critério: ")
    if escolha == "1":
        ordenar(lista, "titulo")
        print("Lista ordenada por título:")
    elif escolha == "2":
        ordenar(lista, "identificador")
        print("Lista ordenada por identificador:")
    else:
        print("Opção inválida: digite 1 ou 2.")
        return
    mostrar_lista(lista)


def opcao_carregar_exemplos(lista):
    print("--- Carregar registros de exemplo ---")
    inseridos = carregar_exemplos(lista)
    ignorados = TOTAL_EXEMPLOS - inseridos
    print(f"{inseridos} registro(s) de exemplo carregado(s).")
    if ignorados > 0:
        print(f"{ignorados} não entraram porque o identificador já estava em uso.")
    print(f"A lista tem agora {lista.tamanho} serviço(s).")


# ==============================================================
# LAÇO PRINCIPAL
# ==============================================================

def executar_menu(lista=None):
    """Mostra o menu até o usuário escolher sair.

    Pode ser chamada por outro programa. Se nenhuma lista for
    passada, começa com uma lista encadeada vazia.
    """
    if lista is None:
        lista = ListaEncadeada()

    print(LINHA)
    print(" AVISO: protótipo educacional com dados FICTÍCIOS.")
    print(" Não é um canal oficial de atendimento e não coleta")
    print(" dados pessoais. Os dados ficam só na memória e somem")
    print(" ao sair. Dica: a opção 8 carrega registros de exemplo.")
    print(LINHA)

    try:
        while True:
            mostrar_menu()
            opcao = ler("Escolha uma opção: ")
            if opcao == "1":
                opcao_cadastrar(lista)
            elif opcao == "2":
                opcao_listar(lista)
            elif opcao == "3":
                opcao_consultar(lista)
            elif opcao == "4":
                opcao_atualizar(lista)
            elif opcao == "5":
                opcao_excluir(lista)
            elif opcao == "6":
                opcao_pesquisar(lista)
            elif opcao == "7":
                opcao_ordenar(lista)
            elif opcao == "8":
                opcao_carregar_exemplos(lista)
            elif opcao == "0":
                print("Sistema encerrado. Até logo!")
                break
            else:
                print("Opção inválida: digite um número de 0 a 8.")
    except KeyboardInterrupt:
        # Usuário apertou Ctrl+C: sai com uma mensagem amigável.
        print()
        print("Programa interrompido pelo usuário (Ctrl+C). Sistema encerrado.")
    except EOFError:
        # A entrada acabou (Ctrl+D, Ctrl+Z ou fim do arquivo de entradas).
        print()
        print("Entrada encerrada. Sistema encerrado.")


if __name__ == "__main__":
    executar_menu()
