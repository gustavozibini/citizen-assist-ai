# Sentinela de Alagamento

**Global Solution 2026.2 – CitizenTech · Computer Organization and Architecture (FIAP)**
**Aluno:** Gustavo Zibini Belizario · **RM:** 561376 · 1º ano de Ciência da Computação · trabalho individual

Estação de baixo custo que mede o nível da água em um córrego, galeria ou boca de lobo e avisa a comunidade **antes** do alagamento. Protótipo simulado no Wokwi com Raspberry Pi Pico e MicroPython.

---

## 1. O problema e quem é afetado

Todo período de chuvas, a cidade de São Paulo registra centenas de alagamentos.

- Na temporada de novembro de 2022 a abril de 2023, o Centro de Gerenciamento de Emergências (CGE) da Prefeitura registrou **771 ocorrências em seis meses**, aumento de **57%** em relação à temporada anterior [1].
- Em um único temporal, em 24/01/2025, choveu **124 mm**, a cidade chegou a ter **32 pontos de alagamento ativos** ao mesmo tempo, o Corpo de Bombeiros recebeu **219 chamados ligados a inundações**, o trânsito chegou a **510 km** de lentidão e linhas de metrô e trem foram interrompidas [2].

Quem sofre com isso:

- **moradores de áreas baixas**, que têm a casa invadida pela água e perdem móveis e eletrodomésticos;
- **pedestres**, que podem ser arrastados pela enxurrada ou cair em bocas de lobo encobertas;
- **motoristas e motociclistas**, que entram em vias alagadas sem saber a profundidade;
- **comerciantes**, que perdem mercadoria e dias de trabalho.

Na maioria dos casos a pessoa só descobre que a água subiu quando ela já está na porta.

## 2. Por que a tecnologia ajuda

A água de um córrego ou galeria sobe por alguns minutos antes de transbordar. Um sensor que mede esse nível o tempo todo consegue avisar nesses minutos — o suficiente para tirar o carro, subir os móveis, fechar a loja ou desviar o caminho.

Isso já é feito em outros lugares. Em Luxemburgo, a operadora POST, o instituto de pesquisa LIST e a administração de águas do país instalaram uma rede de sensores IoT de nível de rio que envia dados a cada 15 minutos e, quando a chuva passa de um limite, dispara um alerta automático e passa a medir o nível a cada minuto [3]. O Sentinela de Alagamento aplica a mesma ideia (medir o nível, comparar com um limiar, alertar sozinho) em um ponto de bairro, com componentes baratos.

## 3. A solução

Um sensor ultrassônico **HC-SR04** fica preso acima da água (por exemplo, embaixo de uma ponte ou na tampa da galeria), apontando para baixo. Ele mede a distância até a superfície. Quanto mais a água sobe, menor a distância.

A Raspberry Pi Pico:

1. **recebe** a distância do sensor;
2. **processa**: converte em nível da água (cm) e em percentual da altura do canal, faz a média das últimas leituras e decide o estado;
3. **responde**: acende o LED do estado, toca o buzzer no alerta, escreve no display e registra a leitura no console serial.

| Estado | Quando | O que a comunidade vê e ouve |
|---|---|---|
| NORMAL | nível abaixo de 50% | LED verde |
| ATENÇÃO | nível a partir de 50%, ou nível subindo rápido | LED amarelo |
| ALERTA | nível a partir de 75% | LED vermelho + buzzer intermitente |
| FALHA | 3 leituras inválidas seguidas | LED amarelo piscando + "FALHA NO SENSOR" |

O **botão azul** silencia o buzzer durante um alerta. O LED vermelho continua aceso e o display mostra "ALERTA (SEM SOM)". Se o nível baixar e subir de novo, o som volta.

## 4. Componentes

| Qtd | Componente | Peça no Wokwi | Função |
|---|---|---|---|
| 1 | Raspberry Pi Pico | `wokwi-pi-pico` | lê, processa e aciona as saídas |
| 1 | Sensor ultrassônico HC-SR04 | `wokwi-hc-sr04` | entrada: distância até a água |
| 1 | Display LCD 16x2 com módulo I2C | `wokwi-lcd1602` (`pins: i2c`) | saída: nível e estado |
| 3 | LED (verde, amarelo, vermelho) | `wokwi-led` | saída: estado |
| 3 | Resistor de 220 Ω | `wokwi-resistor` | limita a corrente de cada LED |
| 1 | Buzzer | `wokwi-buzzer` | saída: alerta sonoro |
| 1 | Botão | `wokwi-pushbutton` | entrada: silenciar o buzzer |

## 5. Tabela de pinos

A mesma tabela vale para o `main.py` (constantes `PINO_...`) e para o `diagram.json`.

| Pino do Pico | Liga em | Direção | Constante no `main.py` |
|---|---|---|---|
| GP0 | LCD – SDA | I2C0 | `PINO_LCD_SDA = 0` |
| GP1 | LCD – SCL | I2C0 | `PINO_LCD_SCL = 1` |
| GP2 | HC-SR04 – ECHO | entrada | `PINO_ECHO = 2` |
| GP3 | HC-SR04 – TRIG | saída | `PINO_TRIG = 3` |
| GP13 | resistor 220 Ω → LED verde (ânodo) | saída | `PINO_LED_VERDE = 13` |
| GP14 | resistor 220 Ω → LED amarelo (ânodo) | saída | `PINO_LED_AMARELO = 14` |
| GP15 | resistor 220 Ω → LED vermelho (ânodo) | saída | `PINO_LED_VERMELHO = 15` |
| GP16 | buzzer – pino 2 (positivo) | saída PWM | `PINO_BUZZER = 16` |
| GP17 | botão – contato 1 | entrada com pull-up interno | `PINO_BOTAO = 17` |
| VBUS (5 V) | HC-SR04 – VCC e LCD – VCC | alimentação | — |
| GND | HC-SR04, LCD, cátodo dos 3 LEDs, buzzer pino 1, botão contato 2 | terra | — |

Endereço I2C do LCD: **0x27** (padrão do Wokwi; está no `main.py` em `ENDERECO_LCD` e no `diagram.json` em `i2cAddress`).

## 6. Lógica do programa

Constantes no topo do `main.py`:

| Constante | Valor | Significado |
|---|---|---|
| `ALTURA_SENSOR_CM` | 200 | distância do sensor até o fundo do canal |
| `ALTURA_CANAL_CM` | 150 | nível em que a água transborda (100%) |
| `LIMIAR_ATENCAO` | 50 | % para entrar em ATENÇÃO |
| `LIMIAR_ALERTA` | 75 | % para entrar em ALERTA |
| `HISTERESE` | 5 | pontos percentuais abaixo do limiar para descer de estado |
| `TAMANHO_MEDIA` | 3 | leituras usadas na média móvel |
| `MAX_FALHAS` | 3 | leituras inválidas seguidas para declarar FALHA |
| `TOLERANCIA_CM` | 20 | leitura acima de 220 cm é considerada inválida |
| `SUBIDA_RAPIDA_CM` | 10 | subida da média, em cm por leitura, que antecipa a ATENÇÃO |
| `INTERVALO_MS` | 500 | tempo entre leituras |

Contas:

```
distância (cm)  = duração do pulso ECHO (µs) / 58
nível (cm)      = ALTURA_SENSOR_CM − distância
percentual (%)  = nível × 100 / ALTURA_CANAL_CM   (limitado a 100)
```

A cada ciclo (`ciclo()`):

1. `ler_distancia()` dispara o sensor e mede o eco. Sem eco, devolve `None`.
2. `processar_leitura()`:
   - leitura inválida (sem eco, menor que 2 cm ou maior que 220 cm): conta a falha; na 3ª seguida, entra em **FALHA**. Uma ou duas leituras ruins isoladas só são ignoradas.
   - leitura válida: entra na **média móvel** das 3 últimas e vira nível e percentual.
   - `definir_estado()` aplica os limiares com **histerese**: sobe para ATENÇÃO em 50% e só volta a NORMAL abaixo de 45%; sobe para ALERTA em 75% e só desce abaixo de 70%. Assim o estado não fica trocando quando o nível está bem em cima do limiar.
   - **subida rápida**: se a média subiu 10 cm ou mais de uma leitura para a outra e o estado ainda é NORMAL, o programa antecipa a ATENÇÃO por 6 leituras ("ATENCAO: SUBINDO").
3. `verificar_botao()` silencia o buzzer se o botão for apertado durante o ALERTA.
4. `atualizar_saidas()` liga os LEDs e o buzzer.
5. `atualizar_lcd()` escreve nível e estado no display.
6. `registrar_serial()` imprime a leitura no console — é o registro que seria enviado a uma central.

Exemplo do console:

```
[0012] dist=110.0cm nivel=90cm (60%) estado=ATENCAO som=desligado
[0020] dist=60.0cm nivel=140cm (93%) estado=ALERTA som=ligado
>> Botao: buzzer silenciado (alerta visual continua)
[0021] dist=60.0cm nivel=140cm (93%) estado=ALERTA som=silenciado
```

## 7. Como abrir no Wokwi (passo a passo)

1. Entre em <https://wokwi.com> e faça login (necessário para salvar).
2. Crie um projeto novo de **Raspberry Pi Pico com MicroPython**: <https://wokwi.com/projects/new/micropython-pi-pico>.
3. Na aba **`main.py`**, apague tudo e cole o conteúdo do `main.py` desta pasta.
4. Na aba **`diagram.json`**, apague tudo e cole o conteúdo do `diagram.json` desta pasta. O circuito aparece montado à direita.
5. Crie os dois arquivos da biblioteca do display: clique na setinha ao lado das abas dos arquivos, escolha **New file…**, dê o nome **`lcd_api.py`** e cole o conteúdo. Repita para **`pico_i2c_lcd.py`**. Os nomes precisam ser exatamente esses.
6. Clique no botão verde **▶ (Start the simulation)**. O display mostra "Sentinela de Alagamento" e depois o nível; o LED verde acende.
7. **Clique no sensor HC-SR04** no desenho. Aparece um controle deslizante de distância. Mova para simular a água subindo:

   | Distância no controle | Nível | Resultado esperado |
   |---|---|---|
   | 180 cm | 20 cm (13%) | NORMAL – LED verde |
   | 110 cm | 90 cm (60%) | ATENÇÃO – LED amarelo |
   | 60 cm | 140 cm (93%) | ALERTA – LED vermelho + buzzer |
   | 400 cm | fora da faixa | FALHA NO SENSOR – amarelo piscando |

   Ao mover o controle de uma vez, o display pode mostrar "ATENCAO: SUBINDO" por alguns segundos: é a detecção de subida rápida.
8. Com o alerta tocando, clique no **botão azul** (ou aperte a tecla **S** com o desenho em foco) para silenciar.
9. Clique em **Save** e copie o endereço da página (`https://wokwi.com/projects/…`). Esse é o link da entrega. Cole no `ENTREGA.txt`.

Os arquivos `teste_logica.py`, `validar_diagrama.py`, `README.md`, `ROTEIRO_VIDEO.md`, `ENTREGA.txt`, `LICENCA_LCD.txt` e a pasta `evidencias/` **não** vão para o Wokwi.

Se algo não funcionar na primeira vez, veja a seção 11.

## 8. Testes feitos fora do simulador

- **`teste_logica.py`** roda o `main.py` verdadeiro em Python comum, com um módulo `machine` simulado, e confere 68 itens: conversão distância → nível, limiares, histerese, média móvel, falha de sensor, botão de silenciar, subida rápida e o texto que a biblioteca do LCD enviaria ao display. Saída completa em `evidencias/saida_teste_logica.txt`.
- **`validar_diagrama.py`** confere o `diagram.json` contra a documentação do Wokwi: JSON válido, ids únicos, tipos, atributos, pinos de cada ligação e a tabela de pinos igual à do `main.py`. Saída em `evidencias/saida_validacao_diagrama.txt`.

Para repetir: `python3 teste_logica.py` e `python3 validar_diagrama.py`, dentro desta pasta.

Esses testes verificam a lógica e a consistência dos arquivos. Eles não substituem a execução no Wokwi.

## 9. Benefícios para a sociedade

- **Tempo de reação**: o aviso chega enquanto a água ainda está dentro do canal.
- **Aviso para quem está na rua**: luz e som no próprio local, sem depender de celular ou internet.
- **Baixo custo**: poucos componentes comuns, o que permite instalar em vários pontos de um bairro.
- **Dados para o poder público**: o registro de cada leitura mostra quais pontos enchem primeiro e com que frequência, ajudando a priorizar limpeza de bocas de lobo e obras.
- **Confiança no equipamento**: quando o sensor falha, o aparelho mostra a falha em vez de indicar "normal" por engano.

## 10. Limitações

- É um **protótipo simulado**. Não foi montado nem testado em campo.
- **Não tem comunicação de rede**. O console serial faz o papel do envio para uma central; uma versão real usaria uma placa com Wi-Fi (Pico W) ou rádio LoRa.
- **Precisa de calibração em campo**: altura do sensor, altura do canal e limiares mudam em cada ponto e devem ser ajustados nas constantes.
- O intervalo de 0,5 s e o limite de subida rápida foram escolhidos para a demonstração. Em campo, as leituras seriam mais espaçadas e os valores, outros.
- O HC-SR04 real sofre com chuva forte, espuma, lixo flutuante e variação de temperatura. Um produto final usaria sensor ultrassônico à prova d'água ou sensor de pressão.
- Na montagem física, o HC-SR04 e o módulo I2C do LCD trabalham em 5 V e o Pico em 3,3 V: o pino ECHO e as linhas I2C precisam de divisor de tensão ou conversor de nível. No simulador isso não é necessário.
- Falta alimentação própria (bateria e painel solar) e caixa protegida contra água.

## 11. Se precisar ajustar no Wokwi

| Sintoma | O que verificar |
|---|---|
| Erro ao iniciar citando a placa ou o firmware | No `diagram.json`, o atributo `"env"` do `wokwi-pi-pico`. Copie o valor que vem no `diagram.json` de um projeto novo criado pelo link do passo 2. |
| `ImportError: no module named 'pico_i2c_lcd'` | Nome dos arquivos extras (`lcd_api.py`, `pico_i2c_lcd.py`). |
| `OSError` na linha do `I2cLcd(...)` ou display em branco | Endereço I2C: `ENDERECO_LCD` no `main.py` e `i2cAddress` no `diagram.json` devem ser iguais (0x27). |
| Buzzer sem som | Som do navegador e o atributo `volume` do buzzer no `diagram.json` (está em 0.1 para não estourar no vídeo). |
| Fios cruzados no desenho | Só estética: arraste as peças. As ligações não mudam. |

## 12. Arquivos desta pasta

| Arquivo | Para quê | Vai para o Wokwi? |
|---|---|---|
| `main.py` | programa principal | sim |
| `diagram.json` | circuito | sim |
| `lcd_api.py`, `pico_i2c_lcd.py` | biblioteca do display LCD I2C | sim |
| `LICENCA_LCD.txt` | licença MIT da biblioteca do display | não |
| `teste_logica.py` | teste da lógica em Python comum | não |
| `validar_diagrama.py` | validação do `diagram.json` | não |
| `evidencias/` | saídas dos dois testes | não |
| `ROTEIRO_VIDEO.md` | roteiro do vídeo | não |
| `ENTREGA.txt` | modelo da entrega com os links | não |

## 13. Fontes

Todas acessadas em 16/11/2026.

1. GAZETA DE S. PAULO. *Alagamentos aumentaram 57% na temporada passada de chuvas em SP*. 16 jan. 2024. Dados do CGE da Prefeitura de São Paulo. <https://www.gazetasp.com.br/estado/alagamentos-aumentaram-57-na-temporada-passada-de-chuvas-em-sao-paulo/>
2. AGÊNCIA BRASIL. *São Paulo ainda registra alagamentos e trânsito intenso após temporal*. 24 jan. 2025. Dados do CGE, CET, Defesa Civil e Corpo de Bombeiros. <https://agenciabrasil.ebc.com.br/geral/noticia/2025-01/sao-paulo-ainda-registra-alagamentos-e-transito-intenso-apos-temporal>
3. CHRONICLE.LU. *POST, LIST Collaborate on New IoT Flood Detection Research Project*. 22 out. 2019. <https://chronicle.lu/category/research-r-d/30745-post-list-collaborate-on-new-iot-flood-detection-research-project>
4. WOKWI. Documentação oficial: formato do `diagram.json`, peças `wokwi-pi-pico`, `wokwi-hc-sr04`, `wokwi-lcd1602`, `wokwi-led`, `wokwi-buzzer`, `wokwi-pushbutton`, `wokwi-resistor` e guia de MicroPython. <https://docs.wokwi.com/diagram-format> · <https://docs.wokwi.com/parts/wokwi-pi-pico> · <https://docs.wokwi.com/parts/wokwi-hc-sr04> · <https://docs.wokwi.com/parts/wokwi-lcd1602> · <https://docs.wokwi.com/guides/micropython>
5. Biblioteca do display: T-622, *RPI-PICO-I2C-LCD* <https://github.com/T-622/RPI-PICO-I2C-LCD>, adaptada de Dave Hylands, *python_lcd* (licença MIT) <https://github.com/dhylands/python_lcd>.
