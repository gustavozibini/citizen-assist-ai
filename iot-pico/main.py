# =============================================================================
# SENTINELA DE ALAGAMENTO
# Global Solution 2026.2 - CitizenTech
# Disciplina: Computer Organization and Architecture - FIAP
#
# Aluno: Gustavo Zibini Belizario - RM 561376
# Curso: Ciencia da Computacao - 1o ano
#
# O que faz: mede o nivel da agua de um corrego, galeria ou boca de lobo com
# um sensor ultrassonico e avisa a comunidade antes do alagamento.
#   NORMAL  -> LED verde
#   ATENCAO -> LED amarelo
#   ALERTA  -> LED vermelho + buzzer intermitente (botao silencia o som)
#   FALHA   -> LED amarelo piscando + "FALHA NO SENSOR" no display
#
# Placa: Raspberry Pi Pico (MicroPython) - simulacao no Wokwi
# =============================================================================

from machine import Pin, PWM, I2C, time_pulse_us
import time

from pico_i2c_lcd import I2cLcd   # biblioteca do display (arquivo do projeto)

# -----------------------------------------------------------------------------
# 1) PINOS (a mesma tabela esta no README.md e no diagram.json)
# -----------------------------------------------------------------------------
PINO_LCD_SDA = 0        # GP0  -> SDA do display LCD (I2C0)
PINO_LCD_SCL = 1        # GP1  -> SCL do display LCD (I2C0)
PINO_ECHO = 2           # GP2  <- ECHO do sensor HC-SR04
PINO_TRIG = 3           # GP3  -> TRIG do sensor HC-SR04
PINO_LED_VERDE = 13     # GP13 -> LED verde (com resistor de 220 ohms)
PINO_LED_AMARELO = 14   # GP14 -> LED amarelo (com resistor de 220 ohms)
PINO_LED_VERMELHO = 15  # GP15 -> LED vermelho (com resistor de 220 ohms)
PINO_BUZZER = 16        # GP16 -> buzzer
PINO_BOTAO = 17         # GP17 <- botao "silenciar" (liga o pino ao GND)

ENDERECO_LCD = 0x27     # endereco I2C padrao do LCD no Wokwi

# -----------------------------------------------------------------------------
# 2) CONFIGURACAO DO LOCAL (ajustar na instalacao real)
# -----------------------------------------------------------------------------
ALTURA_SENSOR_CM = 200  # distancia do sensor ate o fundo do canal (canal vazio)
ALTURA_CANAL_CM = 150   # nivel em que a agua transborda (100 %)
TOLERANCIA_CM = 20      # folga aceita alem do fundo antes de considerar erro
DISTANCIA_MINIMA_CM = 2 # o HC-SR04 nao mede abaixo de 2 cm

# -----------------------------------------------------------------------------
# 3) LIMIARES (em % da altura do canal)
# -----------------------------------------------------------------------------
LIMIAR_ATENCAO = 50     # a partir de 50 % -> ATENCAO
LIMIAR_ALERTA = 75      # a partir de 75 % -> ALERTA
HISTERESE = 5           # para descer de estado precisa cair 5 pontos abaixo
                        # do limiar (ATENCAO sai em 45 %, ALERTA sai em 70 %)

# -----------------------------------------------------------------------------
# 4) LEITURAS
# -----------------------------------------------------------------------------
INTERVALO_MS = 500      # tempo entre leituras (no campo seria bem maior)
TAMANHO_MEDIA = 3       # quantas leituras entram na media movel
MAX_FALHAS = 3          # leituras invalidas seguidas para declarar FALHA
TIMEOUT_ECHO_US = 30000 # tempo maximo de espera pelo eco (microssegundos)
US_POR_CM = 58          # o pulso do ECHO dura 58 microssegundos por cm

SUBIDA_RAPIDA_CM = 10   # subida da media (cm por leitura) considerada rapida
LEITURAS_ANTECIPACAO = 6  # por quantas leituras a ATENCAO antecipada dura

FREQUENCIA_BUZZER = 2000  # tom do buzzer, em Hz

# Nomes dos estados
NORMAL = "NORMAL"
ATENCAO = "ATENCAO"
ALERTA = "ALERTA"
FALHA = "FALHA"

# -----------------------------------------------------------------------------
# 5) COMPONENTES
# -----------------------------------------------------------------------------
trig = Pin(PINO_TRIG, Pin.OUT)
echo = Pin(PINO_ECHO, Pin.IN)
led_verde = Pin(PINO_LED_VERDE, Pin.OUT)
led_amarelo = Pin(PINO_LED_AMARELO, Pin.OUT)
led_vermelho = Pin(PINO_LED_VERMELHO, Pin.OUT)
botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)   # solto = 1, apertado = 0

buzzer = PWM(Pin(PINO_BUZZER))
buzzer.freq(FREQUENCIA_BUZZER)
buzzer.duty_u16(0)                              # comeca em silencio

i2c = I2C(0, sda=Pin(PINO_LCD_SDA), scl=Pin(PINO_LCD_SCL), freq=400000)
lcd = I2cLcd(i2c, ENDERECO_LCD, 2, 16)          # 2 linhas, 16 colunas

# -----------------------------------------------------------------------------
# 6) VARIAVEIS DE ESTADO (memoria do programa entre uma leitura e outra)
# -----------------------------------------------------------------------------
leituras = []            # ultimos niveis validos (para a media movel)
estado = NORMAL          # estado mostrado para a comunidade
estado_nivel = NORMAL    # estado calculado so pelos limiares (com histerese)
nivel_cm = 0             # nivel medio atual, em cm
percentual = 0           # nivel medio atual, em % do canal
nivel_anterior = None    # nivel medio da leitura anterior (para a taxa)
antecipacao = 0          # leituras restantes de ATENCAO por subida rapida
subida_rapida = False    # True quando a ATENCAO veio da subida rapida
falhas_seguidas = 0      # contador de leituras invalidas seguidas
silenciado = False       # True depois que o botao foi apertado no ALERTA
pisca = False            # alterna a cada ciclo (buzzer e LED intermitentes)
numero_leitura = 0       # contador para o registro serial
texto_lcd = ("", "")     # o que esta escrito no display agora


# -----------------------------------------------------------------------------
# 7) FUNCOES
# -----------------------------------------------------------------------------
def ler_distancia():
    """Dispara o HC-SR04 e devolve a distancia em cm (ou None se falhar)."""
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)              # pulso de 10 microssegundos inicia a medicao
    time.sleep_us(10)
    trig.value(0)

    duracao = time_pulse_us(echo, 1, TIMEOUT_ECHO_US)
    if duracao < 0:            # valor negativo = o eco nao voltou a tempo
        return None
    return duracao / US_POR_CM


def leitura_valida(distancia):
    """Confere se a distancia faz sentido para este local."""
    if distancia is None:
        return False
    if distancia < DISTANCIA_MINIMA_CM:
        return False
    if distancia > ALTURA_SENSOR_CM + TOLERANCIA_CM:
        return False           # mais longe que o fundo do canal: sensor errado
    return True


def calcular_nivel(distancia):
    """Converte distancia (sensor -> agua) em nivel da agua, em cm."""
    nivel = ALTURA_SENSOR_CM - distancia
    if nivel < 0:
        nivel = 0
    return nivel


def calcular_percentual(nivel):
    """Converte o nivel em % da altura do canal (limitado a 100 %)."""
    valor = nivel * 100 / ALTURA_CANAL_CM
    if valor > 100:
        valor = 100
    return valor


def calcular_media(valores):
    """Media simples da lista de leituras."""
    return sum(valores) / len(valores)


def definir_estado(estado_atual, pct):
    """Escolhe NORMAL, ATENCAO ou ALERTA usando os limiares e a histerese."""
    # Para subir de estado usa o limiar cheio.
    if pct >= LIMIAR_ALERTA:
        return ALERTA
    # Ja estava em ALERTA: so sai quando cair abaixo de (limiar - histerese).
    if estado_atual == ALERTA and pct >= LIMIAR_ALERTA - HISTERESE:
        return ALERTA

    if pct >= LIMIAR_ATENCAO:
        return ATENCAO
    # Ja estava em ATENCAO ou ALERTA: mesma regra para voltar ao NORMAL.
    if estado_atual != NORMAL and pct >= LIMIAR_ATENCAO - HISTERESE:
        return ATENCAO

    return NORMAL


def processar_leitura(distancia):
    """Atualiza nivel, percentual e estado a partir de uma leitura."""
    global estado, estado_nivel, nivel_cm, percentual, nivel_anterior
    global antecipacao, subida_rapida, falhas_seguidas, silenciado, leituras

    # --- Leitura invalida: conta a falha e, se repetir, entra em FALHA ---
    if not leitura_valida(distancia):
        falhas_seguidas = falhas_seguidas + 1
        if falhas_seguidas >= MAX_FALHAS:
            estado = FALHA
            estado_nivel = NORMAL
            leituras = []          # descarta leituras antigas
            nivel_anterior = None
            antecipacao = 0
            subida_rapida = False
            silenciado = False
        return

    # --- Leitura valida ---
    falhas_seguidas = 0
    leituras.append(calcular_nivel(distancia))
    if len(leituras) > TAMANHO_MEDIA:
        leituras.pop(0)            # mantem so as ultimas leituras

    nivel_cm = calcular_media(leituras)
    percentual = calcular_percentual(nivel_cm)

    # Subida rapida: compara a media de agora com a da leitura anterior.
    if nivel_anterior is not None:
        if nivel_cm - nivel_anterior >= SUBIDA_RAPIDA_CM:
            antecipacao = LEITURAS_ANTECIPACAO
        elif antecipacao > 0:
            antecipacao = antecipacao - 1
    nivel_anterior = nivel_cm

    # Estado pelos limiares (com histerese).
    estado_nivel = definir_estado(estado_nivel, percentual)
    estado = estado_nivel

    # Antecipa a ATENCAO se o nivel ainda esta baixo mas subindo rapido.
    subida_rapida = False
    if estado_nivel == NORMAL and antecipacao > 0:
        estado = ATENCAO
        subida_rapida = True

    # Saiu do ALERTA: o som volta a valer no proximo alerta.
    if estado != ALERTA:
        silenciado = False


def verificar_botao():
    """Se o botao for apertado durante o ALERTA, silencia o buzzer."""
    global silenciado
    if botao.value() == 0 and estado == ALERTA and not silenciado:
        silenciado = True
        buzzer.duty_u16(0)         # corta o som na hora
        print(">> Botao: buzzer silenciado (alerta visual continua)")


def atualizar_saidas():
    """Liga e desliga LEDs e buzzer conforme o estado."""
    global pisca
    pisca = not pisca              # inverte a cada ciclo: gera o intermitente

    led_verde.value(1 if estado == NORMAL else 0)
    led_vermelho.value(1 if estado == ALERTA else 0)

    if estado == ATENCAO:
        led_amarelo.value(1)
    elif estado == FALHA:
        led_amarelo.value(1 if pisca else 0)   # amarelo piscando = defeito
    else:
        led_amarelo.value(0)

    if estado == ALERTA and not silenciado and pisca:
        buzzer.duty_u16(32768)     # 50 % do ciclo PWM = som ligado
    else:
        buzzer.duty_u16(0)         # som desligado


def montar_texto_lcd():
    """Monta as duas linhas de 16 caracteres do display."""
    if estado == FALHA:
        return ("FALHA NO SENSOR ", "Verificar equip.")

    linha1 = "Nivel:{:3d}cm {:3d}%".format(round(nivel_cm), round(percentual))

    if estado == ALERTA and silenciado:
        linha2 = "ALERTA (SEM SOM)"
    elif estado == ALERTA:
        linha2 = "ALERTA! RISCO"
    elif estado == ATENCAO and subida_rapida:
        linha2 = "ATENCAO: SUBINDO"
    elif estado == ATENCAO:
        linha2 = "ATENCAO"
    else:
        linha2 = "NORMAL"

    return (linha1, "{:<16}".format(linha2))   # completa com espacos


def atualizar_lcd():
    """Escreve no display somente quando o texto mudou (evita piscar)."""
    global texto_lcd
    novo = montar_texto_lcd()
    if novo != texto_lcd:
        lcd.move_to(0, 0)
        lcd.putstr(novo[0])
        lcd.move_to(0, 1)
        lcd.putstr(novo[1])
        texto_lcd = novo


def registrar_serial(distancia):
    """Imprime o registro da leitura (o que seria enviado a uma central)."""
    if estado == FALHA:
        print("[{:04d}] FALHA NO SENSOR - sem leitura valida".format(numero_leitura))
        return
    if not leitura_valida(distancia):
        print("[{:04d}] leitura invalida ({}/{}) - mantendo estado {}".format(
            numero_leitura, falhas_seguidas, MAX_FALHAS, estado))
        return

    if estado != ALERTA:
        som = "desligado"
    elif silenciado:
        som = "silenciado"
    else:
        som = "ligado"

    print("[{:04d}] dist={:.1f}cm nivel={:.0f}cm ({:.0f}%) estado={}{} som={}".format(
        numero_leitura, distancia, nivel_cm, percentual, estado,
        " (subida rapida)" if subida_rapida else "", som))


def esperar_lendo_botao(tempo_ms):
    """Espera o intervalo em passos de 50 ms, sem deixar de olhar o botao."""
    passos = tempo_ms // 50
    for _ in range(passos):
        verificar_botao()
        time.sleep_ms(50)


def ciclo():
    """Um ciclo completo: ler -> processar -> agir -> mostrar -> registrar."""
    global numero_leitura
    numero_leitura = numero_leitura + 1

    distancia = ler_distancia()
    processar_leitura(distancia)
    verificar_botao()
    atualizar_saidas()
    atualizar_lcd()
    registrar_serial(distancia)


def principal():
    """Tela de abertura e laco principal."""
    lcd.clear()
    lcd.putstr("Sentinela de")
    lcd.move_to(0, 1)
    lcd.putstr("Alagamento")
    print("Sentinela de Alagamento - Gustavo Zibini Belizario - RM 561376")
    print("Limiares: ATENCAO >= {}%  ALERTA >= {}%  histerese {} pontos".format(
        LIMIAR_ATENCAO, LIMIAR_ALERTA, HISTERESE))
    time.sleep_ms(1500)

    while True:
        ciclo()
        esperar_lendo_botao(INTERVALO_MS)


# -----------------------------------------------------------------------------
# 8) INICIO DO PROGRAMA
# -----------------------------------------------------------------------------
# No Pico, o main.py roda com __name__ == "__main__". O "if" existe para que o
# arquivo de teste (teste_logica.py) consiga importar as funcoes sem entrar no
# laco infinito.
if __name__ == "__main__":
    principal()
