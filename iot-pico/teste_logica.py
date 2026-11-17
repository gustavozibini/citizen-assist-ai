# =============================================================================
# teste_logica.py - testa a logica do main.py em Python comum (CPython)
#
# Aluno: Gustavo Zibini Belizario - RM 561376
#
# Como rodar (no computador, NAO no Wokwi):   python3 teste_logica.py
#
# O Pico nao existe aqui, entao este arquivo cria um modulo "machine" de
# mentira (Pin, PWM, I2C, time_pulse_us). O main.py verdadeiro e importado sem
# nenhuma alteracao e roda em cima dessas pecas simuladas. Assim testamos a
# logica real: conversao, estados, histerese, falha de sensor e botao.
#
# Este arquivo NAO precisa ser copiado para o Wokwi.
# =============================================================================

import sys
import time as time_real
import types

# -----------------------------------------------------------------------------
# 1) Pecas simuladas
# -----------------------------------------------------------------------------
pinos = {}                 # numero do pino -> objeto Pin simulado
distancia_simulada = [180] # distancia "vista" pelo sensor (None = sem eco)


class PinoFalso:
    IN = 0
    OUT = 1
    PULL_UP = 2

    def __init__(self, numero, modo=None, pull=None):
        self.numero = numero
        self.valor = 1 if pull == PinoFalso.PULL_UP else 0   # botao solto = 1
        pinos[numero] = self

    def value(self, novo=None):
        if novo is None:
            return self.valor
        self.valor = novo


class PWMFalso:
    def __init__(self, pino):
        self.pino = pino
        self.duty = 0
        self.frequencia = 0

    def freq(self, valor):
        self.frequencia = valor

    def duty_u16(self, valor):
        self.duty = valor


class LcdFalso:
    """Faz o papel do chip PCF8574 + display HD44780: recebe os bytes I2C que
    a biblioteca do LCD envia e reconstroi o texto que apareceria na tela."""

    def __init__(self):
        self.linhas = [[" "] * 16, [" "] * 16]
        self.endereco_cursor = 0
        self.nibbles_iniciais = 4     # a inicializacao manda 4 meios-bytes
        self.meio_byte = None
        self.byte_anterior = 0

    def receber(self, byte):
        caiu_enable = (self.byte_anterior & 0x04) and not (byte & 0x04)
        self.byte_anterior = byte
        if not caiu_enable:
            return
        nibble = (byte >> 4) & 0x0F
        eh_dado = byte & 0x01
        if self.nibbles_iniciais > 0:
            self.nibbles_iniciais -= 1
            return
        if self.meio_byte is None:
            self.meio_byte = nibble
            return
        valor = (self.meio_byte << 4) | nibble
        self.meio_byte = None
        if eh_dado:
            linha = 1 if self.endereco_cursor >= 0x40 else 0
            coluna = self.endereco_cursor & 0x3F
            if coluna < 16:
                self.linhas[linha][coluna] = chr(valor)
            self.endereco_cursor += 1
        elif valor == 0x01:                       # comando "limpar"
            self.linhas = [[" "] * 16, [" "] * 16]
            self.endereco_cursor = 0
        elif valor & 0x80:                        # comando "mover cursor"
            self.endereco_cursor = valor & 0x7F

    def texto(self):
        return ("".join(self.linhas[0]), "".join(self.linhas[1]))


lcd_falso = LcdFalso()


class I2CFalso:
    def __init__(self, numero, sda=None, scl=None, freq=0):
        self.sda = sda
        self.scl = scl

    def writeto(self, endereco, dados):
        assert endereco == 0x27, "endereco I2C inesperado"
        for byte in dados:
            lcd_falso.receber(byte)


def time_pulse_us_falso(pino, nivel, timeout):
    """Devolve a duracao do pulso de eco para a distancia simulada."""
    distancia = distancia_simulada[0]
    if distancia is None:
        return -2                                 # igual ao MicroPython: timeout
    return int(distancia * 58)


machine_falso = types.ModuleType("machine")
machine_falso.Pin = PinoFalso
machine_falso.PWM = PWMFalso
machine_falso.I2C = I2CFalso
machine_falso.time_pulse_us = time_pulse_us_falso

# O "time" do MicroPython tem sleep_ms / sleep_us, que o CPython nao tem.
time_falso = types.ModuleType("time")
time_falso.sleep_ms = lambda ms: None             # nao espera: teste rapido
time_falso.sleep_us = lambda us: None
time_falso.sleep = lambda s: None
time_falso.time = time_real.time

sys.modules["machine"] = machine_falso
sys.modules["time"] = time_falso
sys.modules["utime"] = time_falso

import main                                       # o main.py de verdade

sys.modules["time"] = time_real                   # devolve o time original

# -----------------------------------------------------------------------------
# 2) Ferramentas de teste
# -----------------------------------------------------------------------------
total = 0
falhas = 0


def conferir(descricao, entrada, esperado, observado):
    global total, falhas
    total += 1
    ok = esperado == observado
    if not ok:
        falhas += 1
    print("[{}] {}".format("OK  " if ok else "ERRO", descricao))
    print("       entrada  : {}".format(entrada))
    print("       esperado : {}".format(esperado))
    print("       observado: {}".format(observado))


def reiniciar():
    """Volta o main ao estado inicial (como se ligasse a placa de novo)."""
    main.leituras = []
    main.estado = main.NORMAL
    main.estado_nivel = main.NORMAL
    main.nivel_cm = 0
    main.percentual = 0
    main.nivel_anterior = None
    main.antecipacao = 0
    main.subida_rapida = False
    main.falhas_seguidas = 0
    main.silenciado = False
    main.pisca = False
    pinos[main.PINO_BOTAO].valor = 1


def rodar(distancia, ciclos=1):
    """Coloca o sensor numa distancia e executa ciclos completos do main."""
    distancia_simulada[0] = distancia
    for _ in range(ciclos):
        main.ciclo()


def leds():
    """Devolve (verde, amarelo, vermelho) como estao nos pinos."""
    return (pinos[main.PINO_LED_VERDE].valor,
            pinos[main.PINO_LED_AMARELO].valor,
            pinos[main.PINO_LED_VERMELHO].valor)


def buzzer_tocou(distancia, ciclos=4):
    """Roda alguns ciclos e diz se o buzzer ligou em algum deles."""
    tocou = False
    for _ in range(ciclos):
        rodar(distancia)
        if main.buzzer.duty > 0:
            tocou = True
    return tocou


def titulo(texto):
    print()
    print("=" * 70)
    print(texto)
    print("=" * 70)


# -----------------------------------------------------------------------------
# 3) Testes
# -----------------------------------------------------------------------------
print("TESTE DE LOGICA - Sentinela de Alagamento (main.py em CPython)")
print("Configuracao lida do main.py: sensor a {} cm do fundo, canal de {} cm,".format(
    main.ALTURA_SENSOR_CM, main.ALTURA_CANAL_CM))
print("ATENCAO >= {}%, ALERTA >= {}%, histerese {} pontos, media de {} leituras,".format(
    main.LIMIAR_ATENCAO, main.LIMIAR_ALERTA, main.HISTERESE, main.TAMANHO_MEDIA))
print("FALHA apos {} leituras invalidas seguidas.".format(main.MAX_FALHAS))

titulo("A) Conversao distancia -> nivel -> percentual")
for dist, nivel_esp, pct_esp in [(200, 0, 0.0), (180, 20, 13.3), (125, 75, 50.0),
                                 (110, 90, 60.0), (87.5, 112.5, 75.0),
                                 (60, 140, 93.3), (50, 150, 100.0),
                                 (10, 190, 100.0), (215, 0, 0.0)]:
    nivel = main.calcular_nivel(dist)
    pct = round(float(main.calcular_percentual(nivel)), 1)
    conferir("distancia {} cm".format(dist), "distancia={} cm".format(dist),
             "nivel={} cm, {}%".format(nivel_esp, pct_esp),
             "nivel={} cm, {}%".format(nivel, pct))

titulo("B) Leitura do sensor (pulso de eco -> cm) e validacao de faixa")
distancia_simulada[0] = 116
conferir("pulso de 6728 us vira 116 cm", "eco=6728 us", 116.0,
         round(main.ler_distancia(), 1))
distancia_simulada[0] = None
conferir("sem eco (timeout) devolve None", "eco=timeout", None, main.ler_distancia())
for dist, esp in [(None, False), (1, False), (2, True), (200, True), (220, True),
                  (221, False), (400, False)]:
    conferir("leitura_valida({})".format(dist), "distancia={}".format(dist), esp,
             main.leitura_valida(dist))

titulo("C) Funcao definir_estado: limiares e histerese")
for atual, pct, esp in [
        (main.NORMAL, 49.9, main.NORMAL), (main.NORMAL, 50, main.ATENCAO),
        (main.ATENCAO, 47, main.ATENCAO), (main.ATENCAO, 45, main.ATENCAO),
        (main.ATENCAO, 44.9, main.NORMAL), (main.NORMAL, 47, main.NORMAL),
        (main.ATENCAO, 74.9, main.ATENCAO), (main.ATENCAO, 75, main.ALERTA),
        (main.ALERTA, 72, main.ALERTA), (main.ALERTA, 70, main.ALERTA),
        (main.ALERTA, 69.9, main.ATENCAO), (main.ALERTA, 47, main.ATENCAO),
        (main.ALERTA, 30, main.NORMAL), (main.NORMAL, 90, main.ALERTA)]:
    conferir("estado atual {} com {}%".format(atual, pct),
             "estado_atual={}, percentual={}".format(atual, pct), esp,
             main.definir_estado(atual, pct))

titulo("D) Ciclo completo: estados, LEDs (verde, amarelo, vermelho) e display")
reiniciar()
rodar(180, 5)
conferir("agua baixa -> NORMAL, so LED verde", "distancia=180 cm por 5 leituras",
         (main.NORMAL, (1, 0, 0)), (main.estado, leds()))
conferir("display no estado NORMAL", "distancia=180 cm",
         ("Nivel: 20cm  13%", "NORMAL          "), lcd_falso.texto())

rodar(110, 10)
conferir("agua a 60% -> ATENCAO, so LED amarelo", "distancia=110 cm por 10 leituras",
         (main.ATENCAO, (0, 1, 0)), (main.estado, leds()))
conferir("display no estado ATENCAO", "distancia=110 cm",
         ("Nivel: 90cm  60%", "ATENCAO         "), lcd_falso.texto())

rodar(60, 5)
conferir("agua a 93% -> ALERTA, so LED vermelho", "distancia=60 cm por 5 leituras",
         (main.ALERTA, (0, 0, 1)), (main.estado, leds()))
conferir("display no estado ALERTA", "distancia=60 cm",
         ("Nivel:140cm  93%", "ALERTA! RISCO   "), lcd_falso.texto())

titulo("E) Buzzer intermitente somente no ALERTA")
sequencia = []
for _ in range(6):
    rodar(60)
    sequencia.append(1 if main.buzzer.duty > 0 else 0)
conferir("no ALERTA o buzzer alterna ligado/desligado a cada ciclo",
         "distancia=60 cm por 6 leituras", True,
         sequencia in ([1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1]))
print("       sequencia do buzzer: {}".format(sequencia))
reiniciar()
conferir("no NORMAL o buzzer nunca toca", "distancia=180 cm por 4 leituras", False,
         buzzer_tocou(180))
conferir("na ATENCAO o buzzer nunca toca", "distancia=110 cm por 8 leituras", False,
         buzzer_tocou(110, 8))

titulo("F) Histerese no ciclo completo (o estado nao fica piscando no limiar)")
reiniciar()
rodar(110, 6)                                   # 60% -> ATENCAO
rodar(129, 6)                                   # 47,3%: abaixo de 50, acima de 45
conferir("desceu para 47% vindo da ATENCAO: continua ATENCAO",
         "distancia=129 cm (47,3%) depois de 60%", main.ATENCAO, main.estado)
rodar(135, 6)                                   # 43,3% -> NORMAL
conferir("desceu para 43%: volta ao NORMAL", "distancia=135 cm (43,3%)",
         main.NORMAL, main.estado)
rodar(129, 12)                                  # 47,3% vindo de baixo
conferir("subiu devagar para 47% vindo do NORMAL: continua NORMAL",
         "distancia=129 cm (47,3%) depois de 43%", main.NORMAL, main.estado)

reiniciar()
rodar(60, 6)                                    # ALERTA
rodar(92, 6)                                    # 72%: abaixo de 75, acima de 70
conferir("desceu para 72% vindo do ALERTA: continua ALERTA",
         "distancia=92 cm (72%) depois de 93%", main.ALERTA, main.estado)
rodar(98, 6)                                    # 68% -> ATENCAO
conferir("desceu para 68%: cai para ATENCAO", "distancia=98 cm (68%)",
         main.ATENCAO, main.estado)

reiniciar()
historico = []
for i in range(20):                             # leituras oscilando no limiar
    rodar(124 if i % 2 == 0 else 127)           # 50,7% e 48,7%
    historico.append(main.estado)
trocas = sum(1 for i in range(1, len(historico)) if historico[i] != historico[i - 1])
conferir("leitura oscilando entre 48,7% e 50,7%: no maximo 1 troca de estado",
         "distancia alternando 124/127 cm por 20 leituras", True, trocas <= 1)
print("       trocas de estado observadas: {}".format(trocas))

titulo("G) Media movel filtra uma leitura isolada fora do padrao")
reiniciar()
rodar(180, 5)
rodar(120)                                      # um pico isolado (53% sozinho)
conferir("um pico isolado nao muda o nivel para o valor bruto",
         "leituras 180,180,180 e depois uma de 120 cm",
         "nivel medio=40 cm", "nivel medio={:.0f} cm".format(main.nivel_cm))

titulo("H) Leitura invalida / falha no sensor")
reiniciar()
rodar(110, 6)
rodar(None, 2)
conferir("2 leituras sem eco: mantem o ultimo estado (ainda nao e falha)",
         "2 leituras com timeout depois de ATENCAO", main.ATENCAO, main.estado)
rodar(None, 1)
conferir("3a leitura sem eco: entra em FALHA", "3 leituras com timeout seguidas",
         main.FALHA, main.estado)
conferir("display mostra a falha", "estado FALHA",
         ("FALHA NO SENSOR ", "Verificar equip."), lcd_falso.texto())
amarelos = []
for _ in range(4):
    rodar(None)
    amarelos.append(leds())
conferir("na FALHA: verde e vermelho apagados, amarelo piscando, sem som",
         "4 leituras com timeout",
         True,
         all(l[0] == 0 and l[2] == 0 for l in amarelos)
         and sorted(set(l[1] for l in amarelos)) == [0, 1]
         and main.buzzer.duty == 0)
print("       LEDs (verde, amarelo, vermelho) em cada ciclo: {}".format(amarelos))

reiniciar()
rodar(180, 3)
rodar(400, 3)                                   # controle do Wokwi no maximo
conferir("distancia fora da faixa (400 cm) tambem vira FALHA",
         "distancia=400 cm por 3 leituras", main.FALHA, main.estado)
rodar(180, 1)
conferir("sensor voltou: sai da FALHA na primeira leitura valida",
         "distancia=180 cm depois da falha", (main.NORMAL, (1, 0, 0)),
         (main.estado, leds()))
reiniciar()
rodar(None, 3)
rodar(60, 1)
conferir("sensor voltou com agua alta: vai direto para ALERTA",
         "distancia=60 cm depois da falha", main.ALERTA, main.estado)

titulo("I) Botao de silenciar")
reiniciar()
rodar(60, 4)
pinos[main.PINO_BOTAO].valor = 0                # aperta o botao
main.esperar_lendo_botao(main.INTERVALO_MS)
pinos[main.PINO_BOTAO].valor = 1                # solta
conferir("apertar no ALERTA silencia", "botao apertado durante ALERTA", True,
         main.silenciado)
tocou = buzzer_tocou(60, 6)
conferir("silenciado: buzzer mudo, LED vermelho continua aceso",
         "distancia=60 cm por 6 leituras depois do botao",
         (False, main.ALERTA, (0, 0, 1)), (tocou, main.estado, leds()))
conferir("display avisa que esta sem som", "ALERTA silenciado",
         "ALERTA (SEM SOM)", lcd_falso.texto()[1])
rodar(180, 6)
conferir("nivel baixou: silencio e cancelado", "distancia=180 cm por 6 leituras",
         (main.NORMAL, False), (main.estado, main.silenciado))
conferir("nivel subiu de novo: o som volta", "distancia=60 cm de novo", True,
         buzzer_tocou(60, 6))

reiniciar()
rodar(180, 4)
pinos[main.PINO_BOTAO].valor = 0
main.esperar_lendo_botao(main.INTERVALO_MS)
pinos[main.PINO_BOTAO].valor = 1
conferir("apertar fora do ALERTA nao faz nada", "botao apertado no NORMAL", False,
         main.silenciado)
conferir("alerta seguinte toca normalmente", "distancia=60 cm depois disso", True,
         buzzer_tocou(60, 6))

titulo("J) Subida rapida antecipa a ATENCAO")
reiniciar()
rodar(180, 5)                                   # 13%
rodar(140, 1)                                   # media sobe 13 cm em 1 leitura
conferir("nivel ainda baixo, mas subindo rapido: ATENCAO antecipada",
         "distancia 180 -> 140 cm (media passa de 20 para 33 cm, 22%)",
         (main.ATENCAO, True), (main.estado, main.subida_rapida))
conferir("display indica a subida", "ATENCAO por subida rapida", "ATENCAO: SUBINDO",
         lcd_falso.texto()[1])
rodar(140, 12)                                  # estabilizou em 40%
conferir("nivel estabilizou abaixo de 45%: volta ao NORMAL",
         "distancia=140 cm por 12 leituras", (main.NORMAL, False),
         (main.estado, main.subida_rapida))
reiniciar()
rodar(180, 5)
historico = []
for dist in range(179, 139, -3):                # sobe 3 cm por leitura (lento)
    rodar(dist)
    historico.append(main.estado)
conferir("subida lenta (3 cm por leitura) nao antecipa",
         "distancia de 179 ate 143 cm, 3 cm por leitura", True,
         all(e == main.NORMAL for e in historico))

titulo("K) Pinos usados pelo programa (conferir com README e diagram.json)")
tabela = {"LCD SDA": main.PINO_LCD_SDA, "LCD SCL": main.PINO_LCD_SCL,
          "ECHO": main.PINO_ECHO, "TRIG": main.PINO_TRIG,
          "LED verde": main.PINO_LED_VERDE, "LED amarelo": main.PINO_LED_AMARELO,
          "LED vermelho": main.PINO_LED_VERMELHO, "Buzzer": main.PINO_BUZZER,
          "Botao": main.PINO_BOTAO}
conferir("nenhum pino repetido", str(tabela), len(tabela), len(set(tabela.values())))
conferir("I2C usa os pinos certos e o endereco 0x27",
         "objeto I2C criado pelo main.py", (0, 1, 0x27),
         (main.i2c.sda.numero, main.i2c.scl.numero, main.ENDERECO_LCD))

print()
print("=" * 70)
print("RESULTADO: {} verificacoes, {} OK, {} com erro".format(total, total - falhas, falhas))
print("=" * 70)
sys.exit(1 if falhas else 0)
