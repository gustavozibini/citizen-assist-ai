# ==============================================================
# Citizen Assist AI - Global Solution 2026.2 (FIAP)
# Disciplina: Data Structures and Algorithms (DSA)
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# dados_exemplo.py
# Registros de exemplo para testar e demonstrar o sistema.
# TODOS OS DADOS SÃO FICTÍCIOS ("Central do Cidadão de Aurora").
# Os identificadores estão fora de ordem de propósito, para a
# ordenação ter o que fazer.
# ==============================================================

from servico import Servico

TOTAL_EXEMPLOS = 15


def adicionar(lista, identificador, titulo, categoria, descricao,
              publico_alvo, canal):
    """Tenta inserir um exemplo. Devolve 1 se inseriu e 0 se o id já existia."""
    servico = Servico(identificador, titulo, categoria, descricao,
                      publico_alvo, canal)
    if lista.inserir(servico):
        return 1
    return 0


def carregar_exemplos(lista):
    """Insere os registros de exemplo na lista. Devolve quantos entraram."""
    inseridos = 0

    inseridos += adicionar(
        lista, 104, "Segunda via da Carteira de Identidade (RG)", "Documentos",
        "Segunda via custa R$ 38,00 e fica pronta em 10 dias úteis. "
        "Agendamento obrigatório pelo portal. Leve certidão e comprovante "
        "de residência.",
        "Qualquer pessoa; menores de 12 anos acompanhados do responsável legal",
        "Posto de Identificação de Aurora")

    inseridos += adicionar(
        lista, 302, "Matrícula na rede municipal de ensino", "Educação",
        "Orientação para matricular crianças e adolescentes nas escolas "
        "municipais. Matrícula gratuita, feita na escola mais próxima de casa.",
        "Responsáveis por crianças e adolescentes em idade escolar",
        "Secretaria de Educação de Aurora ou escola municipal mais próxima")

    inseridos += adicionar(
        lista, 102, "Inscrição no CPF", "Documentos",
        "Inscrição e correção de dados gratuitas pelo portal, com comprovante "
        "em até 2 dias úteis. O atendimento presencial tem taxa de R$ 7,00.",
        "Quem precisa se inscrever no CPF ou corrigir dados",
        "Portal da Central do Cidadão ou balcão de atendimento")

    inseridos += adicionar(
        lista, 401, "Vacinação de rotina", "Saúde",
        "Aplicação das vacinas do calendário básico para todas as idades. "
        "Gratuita e sem agendamento; leve a carteira de vacinação.",
        "Crianças, adultos e idosos",
        "Unidade Básica de Saúde Central de Aurora")

    inseridos += adicionar(
        lista, 203, "Cadastro em programas sociais", "Assistência social",
        "Orientação e inscrição de famílias de baixa renda nos programas "
        "sociais do município. Atendimento gratuito.",
        "Famílias de baixa renda",
        "Centro de Assistência Social de Aurora")

    inseridos += adicionar(
        lista, 106, "Título de eleitor", "Documentos",
        "Primeira via, segunda via e transferência gratuitas. O título "
        "digital sai em até 5 dias úteis. O cadastro fecha 150 dias antes "
        "de cada eleição.",
        "Eleitores a partir de 16 anos",
        "Portal da Central do Cidadão ou Central Eleitoral de Aurora")

    inseridos += adicionar(
        lista, 601, "Tarifa social de energia elétrica", "Energia",
        "Orientação sobre o desconto na conta de luz para famílias de baixa "
        "renda e sobre como pedir o benefício.",
        "Famílias de baixa renda",
        "Centro de Assistência Social de Aurora ou portal da Central do Cidadão")

    inseridos += adicionar(
        lista, 101, "Carteira de Trabalho digital", "Documentos",
        "Gratuita em qualquer canal. A versão digital fica disponível logo "
        "após o cadastro. Não precisa de agendamento.",
        "Trabalhadores; menores de 18 anos acompanhados do responsável legal",
        "Portal ou aplicativo da Central do Cidadão")

    inseridos += adicionar(
        lista, 501, "Ouvidoria comunitária", "Atendimento comunitário",
        "Canal para registrar sugestões, elogios e reclamações sobre os "
        "serviços públicos do bairro.",
        "Moradores de Aurora",
        "Balcão da Central do Cidadão, de segunda a sexta, das 8h às 17h")

    inseridos += adicionar(
        lista, 105, "Certidões de nascimento, casamento e óbito", "Documentos",
        "No balcão: R$ 55,00, pronta em 5 dias úteis. Pelo portal, em PDF: "
        "R$ 49,00, pronta em 3 dias úteis. Isenção no balcão para baixa renda.",
        "A própria pessoa ou terceiro com procuração simples",
        "Cartório Central de Aurora ou portal da Central do Cidadão")

    inseridos += adicionar(
        lista, 301, "Educação de Jovens e Adultos (EJA)", "Educação",
        "Turmas noturnas gratuitas para quem não concluiu o ensino "
        "fundamental ou médio na idade regular.",
        "Jovens e adultos a partir de 15 anos",
        "Escolas municipais com turmas de EJA")

    inseridos += adicionar(
        lista, 402, "Agendamento de consulta médica", "Saúde",
        "Marcação de consulta com clínico geral na unidade de saúde do "
        "bairro. Leve documento original com foto.",
        "Moradores de Aurora",
        "Unidade Básica de Saúde do bairro")

    inseridos += adicionar(
        lista, 103, "Renovação da CNH", "Documentos",
        "Taxa de R$ 180,00; exame médico pago à parte na clínica "
        "credenciada. A nova CNH fica pronta em 7 dias úteis após a "
        "aprovação no exame.",
        "Motoristas com CNH vencida ou a até 30 dias do vencimento",
        "Agendamento obrigatório pelo portal da Central do Cidadão")

    inseridos += adicionar(
        lista, 502, "Ônibus da Cidadania: atendimento itinerante",
        "Atendimento comunitário",
        "Unidade móvel que leva orientação sobre documentos e serviços aos "
        "bairros mais distantes. Consulte o calendário no portal.",
        "Moradores de bairros distantes do centro",
        "Praças e escolas dos bairros, conforme calendário do portal")

    inseridos += adicionar(
        lista, 602, "Economia de energia em casa", "Energia",
        "Orientações simples para reduzir o consumo: lâmpadas de LED, banho "
        "mais curto e aparelhos fora da tomada quando não estão em uso.",
        "Todos os moradores",
        "Portal da Central do Cidadão e mutirões de bairro")

    return inseridos
