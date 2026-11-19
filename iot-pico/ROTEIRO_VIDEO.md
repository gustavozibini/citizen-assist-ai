# Roteiro do vídeo – Sentinela de Alagamento

**Tempo:** 2 a 3 minutos · **YouTube:** "Não listado"

## Antes de gravar

- Abra o link do Wokwi. Não clique em Play ainda.
- Som do Mac ligado, sem fone (o buzzer precisa aparecer no áudio).

| Distância | O que acontece |
|---|---|
| 180 cm | NORMAL – LED verde |
| 110 cm | ATENÇÃO – LED amarelo |
| 60 cm | ALERTA – LED vermelho + buzzer |
| 400 cm | FALHA NO SENSOR – amarelo piscando |

---

## 1. Apresentação (30 s)

**Fale:**
> Oi, eu sou o Gustavo Zibini Belizario, RM 561376. Este é o Sentinela de Alagamento, meu projeto de Computer Organization and Architecture.
>
> Todo verão São Paulo alaga. Numa só temporada de chuvas foram 771 ocorrências. E quase sempre a pessoa só percebe quando a água já está na porta.

## 2. Componentes (30 s)

**Faça:** passe o mouse em cada peça enquanto fala.

**Fale:**
> A ideia é avisar antes.
>
> Este sensor fica em cima do córrego e mede a distância até a água. Quanto mais a água sobe, menor a distância.
>
> A Raspberry Pi Pico calcula o nível. Os LEDs mostram verde, amarelo ou vermelho. O buzzer avisa, o display mostra o nível e o botão azul silencia o som.

## 3. Demonstração (50 s)

**Faça:** clique em **Play**. Depois clique no sensor para abrir o controle de distância.

**180 cm**
> A água está longe. LED verde, o display mostra normal. Embaixo, no console, cada leitura fica registrada.

**Mude para 110 cm**
> A água subiu. LED amarelo: atenção. Como subiu rápido, ele avisa que está subindo.

**Mude para 60 cm**
> Subiu mais. LED vermelho e buzzer tocando: alerta.

## 4. Botão e falha (35 s)

**Clique no botão azul**
> Se alguém já está cuidando, o botão desliga o som. O LED vermelho continua aceso.

**Mude para 400 cm**
> Se o sensor quebrar, o sistema não mostra "normal" por engano. Ele mostra falha no sensor e pisca o amarelo.

**Volte para 180 cm**
> E volta ao normal.

## 5. Encerramento (15 s)

**Fale:**
> Com peças baratas, dá para colocar um desses em cada ponto crítico do bairro. O morador ganha tempo para se proteger. Esse é o Sentinela de Alagamento. Obrigado!

---

## Conferir antes de publicar

- [ ] Falei nome e RM
- [ ] Mostrei verde, amarelo, vermelho, botão e falha
- [ ] O buzzer aparece no áudio
- [ ] Entre 2 e 3 minutos
