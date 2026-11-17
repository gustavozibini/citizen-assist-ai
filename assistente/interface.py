# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
"""Interfaces: menu de texto (input em loop) e Gradio opcional.

Nada do que o usuário digita é salvo. Não há histórico.
"""

from agente import perguntar

# Menu por categoria: uma categoria por ficha, com perguntas prontas.
MENU = {
    "1": ("RG - Carteira de Identidade (FC-01)", [
        "Quanto custa a segunda via do RG?",
        "Que documentos preciso para a segunda via do RG?",
        "Em quanto tempo fica pronto o RG?",
        "Perdi meu RG. Preciso levar boletim de ocorrência?"]),
    "2": ("CPF (FC-02)", [
        "Como faço para me inscrever no CPF?",
        "Quanto custa tirar o CPF presencialmente?",
        "Que documentos preciso para o CPF?"]),
    "3": ("Título de eleitor (FC-03)", [
        "O título de eleitor é pago?",
        "Votar é obrigatório para quem tem 17 anos?",
        "Até quando posso mudar meu título antes da eleição?"]),
    "4": ("Carteira de Trabalho (FC-04)", [
        "Quanto custa e quanto demora a carteira de trabalho digital?",
        "Que documentos preciso para a carteira de trabalho?"]),
    "5": ("Certidões (FC-05)", [
        "Quanto custa a segunda via da certidão de nascimento pelo portal?",
        "Posso pedir a certidão de outra pessoa?"]),
    "6": ("CNH - renovação (FC-06)", [
        "Com quanto tempo de antecedência posso renovar a CNH?",
        "Quanto custa renovar a CNH?",
        "Minha CNH venceu há 45 dias. Posso dirigir?"]),
    "7": ("Atendimento e regras gerais (FC-07)", [
        "Qual o horário de atendimento? Vocês atendem aos sábados?",
        "Preciso de intérprete de Libras. Como faço?",
        "Como pago as taxas?"]),
}

BOAS_VINDAS = (
    "Olá! Sou o Citizen Assist AI, um protótipo educacional.\n"
    "Respondo sobre documentos, com base nas fichas da Central do Cidadão de Aurora.\n"
    "Não digite dados pessoais (CPF, RG, endereço, telefone).\n"
)


def texto_menu():
    linhas = ["Categorias:"] + [f"  {n} - {titulo}" for n, (titulo, _) in MENU.items()]
    linhas += ["Digite o número da categoria ou escreva sua pergunta.",
               "Digite 'menu' para ver de novo ou 'sair' para encerrar."]
    return "\n".join(linhas)


def texto_submenu(numero):
    titulo, perguntas = MENU[numero]
    linhas = [titulo] + [f"  {i} - {p}" for i, p in enumerate(perguntas, 1)]
    linhas.append("Digite o número da pergunta (ou 0 para voltar).")
    return "\n".join(linhas)


def escolher_pergunta(numero_categoria, escolha):
    """Devolve a pergunta pronta ou None se a escolha for inválida."""
    _, perguntas = MENU[numero_categoria]
    if escolha.isdigit() and 1 <= int(escolha) <= len(perguntas):
        return perguntas[int(escolha) - 1]
    return None


def loop_texto(agente, entrada=input, saida=print):
    """Interface de texto. `entrada`/`saida` podem ser trocadas nos testes."""
    saida(BOAS_VINDAS)
    saida(texto_menu())
    while True:
        texto = entrada("\nVocê: ").strip()
        comando = texto.lower()
        if comando in ("sair", "fim", "q"):
            saida("Até logo!")
            return
        if comando == "menu":
            saida(texto_menu())
            continue
        if comando in MENU:
            saida(texto_submenu(comando))
            escolha = entrada("Número: ").strip()
            pergunta = escolher_pergunta(comando, escolha)
            if pergunta is None:
                saida(texto_menu())
                continue
            saida(f"Pergunta: {pergunta}")
            texto = pergunta
        saida("\nAssistente:\n" + perguntar(agente, texto)["resposta"])


# ---------------------------------------------------------------- Gradio (opcional)


def _aceita(funcao, parametro):
    import inspect
    return parametro in inspect.signature(funcao).parameters

CSS_ACESSIVEL = """
body, .gradio-container { background:#ffffff !important; color:#111111 !important; font-size:18px !important; }
textarea, input, select { font-size:18px !important; color:#111111 !important; background:#ffffff !important;
                          border:2px solid #1a1a1a !important; }
button { font-size:18px !important; background:#0b3d91 !important; color:#ffffff !important; }
*:focus-visible { outline:3px solid #ff8c00 !important; outline-offset:2px; }
.prose, .prose * { color:#111111 !important; font-size:18px !important; line-height:1.5; }
"""


def criar_gradio(agente):
    """Interface web simples: categorias + pergunta livre. Tab e Enter funcionam."""
    import gradio as gr

    opcoes = [p for _, (_, perguntas) in MENU.items() for p in perguntas]

    def responder(pergunta_livre, pergunta_menu):
        texto = pergunta_livre if pergunta_livre and pergunta_livre.strip() else pergunta_menu
        return perguntar(agente, texto or "")["resposta"]

    # Gradio 4/5 recebe o CSS no Blocks; Gradio 6 recebe no launch().
    extra = {"css": CSS_ACESSIVEL} if _aceita(gr.Blocks.__init__, "css") else {}
    with gr.Blocks(title="Citizen Assist AI", **extra) as app:
        gr.Markdown("# Citizen Assist AI\n" + BOAS_VINDAS)
        menu = gr.Dropdown(choices=opcoes, label="1. Escolha uma pergunta pronta (setas do teclado)")
        livre = gr.Textbox(label="2. Ou escreva sua pergunta (Enter envia)", lines=2, max_lines=4)
        botao = gr.Button("Perguntar")
        resposta = gr.Textbox(label="Resposta", lines=12, interactive=False)
        botao.click(responder, [livre, menu], resposta)
        livre.submit(responder, [livre, menu], resposta)
    return app


def abrir_gradio(app, **opcoes):
    """Abre a interface. share=False: não cria link público (nada passa por servidor externo)."""
    extra = {"css": CSS_ACESSIVEL} if _aceita(app.launch, "css") else {}
    return app.launch(share=False, **extra, **opcoes)
