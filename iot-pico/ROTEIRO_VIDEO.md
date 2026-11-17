# Roteiro do vídeo – Sentinela de Alagamento

**Duração-alvo:** 2 a 3 minutos · **Aluno:** Gustavo Zibini Belizario – RM 561376
**Publicar:** YouTube, como "Não listado". Colar o link no `ENTREGA.txt`.

## Antes de gravar

- Abra o projeto salvo no Wokwi e deixe a simulação **parada**.
- Deixe visíveis ao mesmo tempo: o circuito, o display e o console serial (parte de baixo).
- Ligue o som do computador e confira se a gravação capta o áudio do navegador (o buzzer precisa ser ouvido).
- Faça um ensaio completo com os valores da tabela abaixo antes de gravar de verdade.
- As falas são sugestões. Fale com as suas palavras; o que importa é passar pelos cinco trechos.

| Distância no controle do sensor | O que deve acontecer |
|---|---|
| 180 cm | NORMAL, LED verde |
| 110 cm | ATENÇÃO, LED amarelo |
| 60 cm | ALERTA, LED vermelho e buzzer |
| 400 cm | FALHA NO SENSOR, amarelo piscando |

---

## Trecho 1 – Problema e público (0:00 a 0:30)

**Na tela:** você na câmera ou a primeira parte do README (seção 1).

**Fala sugerida:**
"Oi, eu sou o Gustavo Zibini Belizario, RM 561376, e este é o meu projeto da Global Solution de Computer Organization and Architecture: o Sentinela de Alagamento.
Todo verão São Paulo alaga. Numa única temporada de chuvas, o centro de emergências da prefeitura registrou 771 ocorrências em seis meses. Quem mais sofre é quem mora em área baixa, o pedestre, o motorista e o pequeno comerciante. E quase sempre a pessoa só percebe que a água subiu quando ela já está na porta."

## Trecho 2 – Como funciona e componentes (0:30 a 1:05)

**Na tela:** o circuito no Wokwi, simulação parada. Aponte com o mouse cada peça enquanto fala.

**Fala sugerida:**
"A ideia é avisar antes. Este sensor ultrassônico fica preso acima do córrego ou da boca de lobo, apontando para a água, e mede a distância até a superfície. Quanto mais a água sobe, menor a distância.
A Raspberry Pi Pico, programada em MicroPython, transforma essa distância em nível da água e em porcentagem do canal. Abaixo de 50% é normal, LED verde. A partir de 50% é atenção, LED amarelo. A partir de 75% é alerta: LED vermelho e buzzer. O display mostra o nível e o estado, e este botão silencia o som."

**Opcional (5 segundos):** mostre o topo do `main.py` com as constantes dos limiares.

## Trecho 3 – Demonstração dos três estados (1:05 a 1:55)

**Na tela:** inicie a simulação. Clique no sensor HC-SR04 para abrir o controle de distância.

1. **Controle em 180 cm.**
   "Comecei a simulação. A água está a 180 centímetros do sensor, nível baixo: LED verde, e o display mostra normal. Aqui embaixo, no console, cada leitura fica registrada, como se fosse enviada para uma central."

2. **Mova para 110 cm.** Espere o display estabilizar em "ATENCAO".
   "Agora a água subiu. O nível passou de 50% e o sistema foi para atenção, LED amarelo. Repara que, como o nível subiu de uma vez, ele mostrou 'subindo': o programa percebe subida rápida e já adianta o aviso."

3. **Mova para 60 cm.**
   "Subiu mais, passou de 75%: alerta. LED vermelho aceso e o buzzer tocando para avisar quem está na rua."

## Trecho 4 – Botão e falha de sensor (1:55 a 2:30)

1. **Com o alerta tocando, clique no botão azul.**
   "Se alguém já está cuidando da situação, aperta o botão: o som para, mas o LED vermelho continua e o display avisa que está sem som. Se a água baixar e subir de novo, o som volta sozinho."

2. **Mova para 180 cm**, espere o verde, **e volte para 60 cm** (o buzzer volta a tocar). *Se o tempo estiver apertado, pule este passo.*

3. **Mova para 400 cm.**
   "E se o sensor quebrar ou for coberto? A leitura fica fora da faixa. Depois de três leituras ruins seguidas, em vez de travar ou mostrar 'normal' por engano, o sistema mostra falha no sensor e pisca o amarelo, pedindo manutenção."

4. **Volte para 180 cm.** O sistema volta ao normal.

## Trecho 5 – Benefício e encerramento (2:30 a 2:50)

**Na tela:** o circuito funcionando, ou você na câmera.

**Fala sugerida:**
"Com poucos componentes baratos, dá para colocar um ponto desses em cada trecho crítico do bairro. O morador ganha minutos para tirar o carro, subir os móveis ou mudar o caminho, e a prefeitura ganha dados de quais pontos enchem primeiro. É um protótipo simulado: o próximo passo seria colocar comunicação por rede e calibrar em um local real. Esse é o Sentinela de Alagamento. Obrigado!"

---

## Conferência final do vídeo

- [ ] Falei nome completo e RM.
- [ ] Expliquei o problema e quem é afetado.
- [ ] Mostrei os componentes e expliquei o funcionamento.
- [ ] Mostrei a entrada mudando (controle de distância) e as saídas respondendo: verde, amarelo, vermelho com buzzer.
- [ ] Mostrei o botão de silenciar e a falha de sensor.
- [ ] Mostrei o display e o console serial.
- [ ] Falei do benefício para a sociedade.
- [ ] O buzzer aparece no áudio da gravação.
- [ ] Vídeo entre 2 e 3 minutos, publicado como "Não listado", link colado no `ENTREGA.txt`.
