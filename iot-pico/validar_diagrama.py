# =============================================================================
# validar_diagrama.py - confere o diagram.json (rodar no computador)
#
# Aluno: Gustavo Zibini Belizario - RM 561376
# Como rodar:   python3 validar_diagrama.py
#
# Confere: JSON valido, ids unicos, tipos de peca conhecidos, atributos
# documentados, toda ligacao aponta para peca e pino existentes, e a tabela
# de pinos do main.py e a mesma do diagrama.
# Os nomes de pinos e atributos abaixo foram copiados da documentacao oficial
# do Wokwi (docs.wokwi.com/parts/...), consultada em 16/11/2026.
# Este arquivo NAO precisa ser copiado para o Wokwi.
# =============================================================================
import json
import re
import sys

PINOS = {
    "wokwi-pi-pico": (["GP%d" % n for n in range(0, 23)] + ["GP26", "GP27", "GP28"]
                      + ["GND.%d" % n for n in range(1, 9)]
                      + ["VSYS", "VBUS", "3V3", "TP4", "TP5"]),
    "wokwi-hc-sr04": ["VCC", "TRIG", "ECHO", "GND"],
    "wokwi-lcd1602": ["GND", "VCC", "SDA", "SCL"],      # configuracao "i2c"
    "wokwi-led": ["A", "C"],
    "wokwi-buzzer": ["1", "2"],
    "wokwi-pushbutton": ["1.l", "1.r", "2.l", "2.r"],
    "wokwi-resistor": ["1", "2"],
}
ATRIBUTOS = {
    "wokwi-pi-pico": ["env"],   # "env" nao esta na pagina da peca; vem do
                                # modelo MicroPython e de projetos reais
    "wokwi-hc-sr04": ["distance"],
    "wokwi-lcd1602": ["pins", "i2cAddress", "color", "background", "variant"],
    "wokwi-led": ["color", "lightColor", "label", "gamma", "flip", "fps"],
    "wokwi-buzzer": ["mode", "volume"],
    "wokwi-pushbutton": ["color", "xray", "label", "key", "bounce"],
    "wokwi-resistor": ["value"],
}

erros = []
total = 0


def conferir(ok, texto):
    global total
    total += 1
    print("[{}] {}".format("OK  " if ok else "ERRO", texto))
    if not ok:
        erros.append(texto)


print("VALIDACAO DO diagram.json - Sentinela de Alagamento")
print()
try:
    diagrama = json.load(open("diagram.json", encoding="utf-8"))
    conferir(True, "diagram.json e um JSON valido")
except ValueError as erro:
    conferir(False, "diagram.json invalido: {}".format(erro))
    sys.exit(1)

conferir(diagrama.get("version") == 1 and diagrama.get("editor") == "wokwi",
         'cabecalho: "version": 1 e "editor": "wokwi"')

pecas = {}
for peca in diagrama["parts"]:
    conferir(peca["id"] not in pecas, "id unico: {}".format(peca["id"]))
    pecas[peca["id"]] = peca
    conferir(peca["type"] in PINOS,
             "tipo documentado: {} ({})".format(peca["type"], peca["id"]))
    for atributo in peca.get("attrs", {}):
        conferir(atributo in ATRIBUTOS.get(peca["type"], []),
                 "atributo documentado: {}.{} = {!r}".format(
                     peca["id"], atributo, peca["attrs"][atributo]))

pico = [p for p in pecas.values() if p["type"] == "wokwi-pi-pico"]
conferir(len(pico) == 1 and pico[0]["attrs"].get("env", "").startswith("micropython-"),
         "placa Raspberry Pi Pico configurada para MicroPython (env={})".format(
             pico[0]["attrs"].get("env") if pico else None))
lcd = pecas["lcd1"]["attrs"]
conferir(lcd.get("pins") == "i2c", 'LCD em modo I2C ("pins": "i2c")')

print()
ligacoes = {}       # "peca:pino" -> lista de pontas ligadas a ele
for conexao in diagrama["connections"]:
    for ponta in conexao[:2]:
        id_peca, pino = ponta.split(":", 1)
        existe = id_peca in pecas and pino in PINOS.get(pecas[id_peca]["type"], [])
        conferir(existe, "ligacao aponta para peca e pino existentes: {}".format(ponta))
    ligacoes.setdefault(conexao[0], []).append(conexao[1])
    ligacoes.setdefault(conexao[1], []).append(conexao[0])


def ligado(a, b):
    return b in ligacoes.get(a, [])


def outro_lado(id_peca, ponta):
    """Num componente de 2 terminais, devolve o terminal oposto."""
    pino = ponta.split(":")[1]
    pares = {"1": "2", "2": "1", "A": "C", "C": "A"}
    return "{}:{}".format(id_peca, pares[pino])


print()
print("Tabela de pinos: main.py x diagram.json")
fonte = open("main.py", encoding="utf-8").read()
constantes = dict((nome, int(valor)) for nome, valor in
                  re.findall(r"^(PINO_\w+)\s*=\s*(\d+)", fonte, re.M))
endereco = re.search(r"^ENDERECO_LCD\s*=\s*(0x[0-9A-Fa-f]+)", fonte, re.M).group(1)

diretas = {"PINO_LCD_SDA": "lcd1:SDA", "PINO_LCD_SCL": "lcd1:SCL",
           "PINO_ECHO": "ultra1:ECHO", "PINO_TRIG": "ultra1:TRIG",
           "PINO_BUZZER": "bz1:2", "PINO_BOTAO": "btn1:1.l"}
for nome, ponta in diretas.items():
    gp = "pico:GP{}".format(constantes[nome])
    conferir(ligado(gp, ponta), "{} = {} -> {} ligado a {}".format(
        nome, constantes[nome], gp, ponta))

for cor in ["verde", "amarelo", "vermelho"]:
    nome = "PINO_LED_" + cor.upper()
    gp = "pico:GP{}".format(constantes[nome])
    resistor = "r_" + cor
    led = "led_" + cor
    entrada = [p for p in ligacoes.get(gp, []) if p.startswith(resistor + ":")]
    ok = False
    if len(entrada) == 1:
        saida = outro_lado(resistor, entrada[0])
        gnd = [p for p in ligacoes.get(led + ":C", []) if p.startswith("pico:GND.")]
        ok = ligado(saida, led + ":A") and len(gnd) == 1
    conferir(ok, "{} = {} -> {} -> resistor {} ({} ohms) -> anodo do {} -> catodo no GND".format(
        nome, constantes[nome], gp, resistor, pecas[resistor]["attrs"]["value"], led))

conferir(len(set(constantes.values())) == len(constantes), "nenhum GPIO usado duas vezes no main.py")
usados = sorted(p for p in ligacoes if p.startswith("pico:GP"))
esperados = sorted("pico:GP{}".format(v) for v in constantes.values())
conferir(usados == esperados, "os GPIOs ligados no diagrama sao exatamente os do main.py: {}".format(
    ", ".join(p.split(":")[1] for p in usados)))
conferir(int(lcd.get("i2cAddress", "0x27"), 16) == int(endereco, 16),
         "endereco I2C do LCD igual nos dois arquivos ({})".format(endereco))

print()
print("Alimentacao e terra")
conferir(ligado("ultra1:VCC", "pico:VBUS"), "HC-SR04 VCC em VBUS (5 V)")
conferir(ligado("lcd1:VCC", "pico:VBUS"), "LCD VCC em VBUS (5 V)")
for ponta in ["ultra1:GND", "lcd1:GND", "bz1:1", "btn1:2.l"]:
    conferir(any(p.startswith("pico:GND.") for p in ligacoes.get(ponta, [])),
             "{} ligado a um GND do Pico".format(ponta))

soltos = []
for id_peca, peca in pecas.items():
    if peca["type"] in ("wokwi-pi-pico", "wokwi-pushbutton"):
        continue        # o Pico e o botao tem pinos que ficam livres de proposito
    for pino in PINOS[peca["type"]]:
        if "{}:{}".format(id_peca, pino) not in ligacoes:
            soltos.append("{}:{}".format(id_peca, pino))
conferir(not soltos, "nenhum terminal de componente sem ligacao {}".format(soltos or ""))

print()
print("RESULTADO: {} verificacoes, {} OK, {} com erro".format(total, total - len(erros), len(erros)))
print("Observacao: esta validacao compara o arquivo com a documentacao do Wokwi.")
print("Ela nao executa o simulador.")
sys.exit(1 if erros else 0)
