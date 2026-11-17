# Fontes dos dados - contribuição de Energia

Aluno: Gustavo Zibini Belizario - RM 561376
Data de acesso de todas as fontes: 16/11/2026.

Cada linha de `premissas.csv` traz valor, unidade, período, fonte, link e a marca:

- **REAL**: valor oficial, publicado ou medido, lido na própria página ou documento.
- **ESTIMADO**: premissa do projeto ou valor ajustado por nós. A justificativa está na coluna `justificativa`.

Os códigos F1 a F14 são usados no CSV, no README e nas respostas do assistente.

## Lista de fontes

| Código | Fonte | O que usamos | Link |
|---|---|---|---|
| F1 | ANEEL - Resolução Homologatória nº 3.596, de 30/06/2026 (reajuste da Enel Distribuição São Paulo). Tabela 2 (tarifas do Grupo B) e Tabela 3 (benefícios da baixa renda). Vigência de 04/07/2026 a 03/07/2027. | B1 residencial: TUSD 472,42 R$/MWh e TE 316,96 R$/MWh. B1 baixa renda (referência): TUSD 306,31 e TE 305,60 R$/MWh. Desconto de 100% até 80 kWh e 0% acima. | https://www.enel.com.br/content/dam/enel-br/megamenu/para-voc%C3%AA/REH%203596.2026%20Enel%20SP.pdf |
| F2 | Secom - Presidência da República: "Milhões de famílias de baixa renda já estão sendo beneficiadas com novo desconto social na conta de luz" (06/01/2026). | Quem tem direito à gratuidade de 80 kWh (CadÚnico com renda por pessoa de até meio salário mínimo; idosos 65+ e pessoas com deficiência do BPC; indígenas e quilombolas). Desconto social de cerca de 11,8% para renda entre meio e um salário mínimo e consumo até 120 kWh, desde 01/01/2026, automático com CadÚnico atualizado. | https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/01/milhoes-de-familias-de-baixa-renda-ja-estao-sendo-beneficiadas-com-novo-desconto-social-na-conta-de-luz |
| F3 | MCTI - fator médio de emissão de CO2 do SIN, citado pela eixos (2023: 38,5 kg CO2/MWh) e pela Cenário Energia (jan. a abr. de 2025: 23,7; 24,8; 21,5; 28,9 kg CO2/MWh). | Fator de emissão do caso-base e fator alternativo da análise de sensibilidade. | https://eixos.com.br/energia-eletrica/brasil-tem-menor-taxa-de-emissao-de-carbono-na-geracao-eletrica-em-onze-anos/ e https://cenarioenergia.com.br/2025/06/13/brasil-reduz-intensidade-de-carbono-na-geracao-eletrica-com-inclusao-de-novas-renovaveis-na-base-de-calculo-oficial/ |
| F4 | Lorenzetti - manual do chuveiro Top Jet (tabela de características técnicas). | Chuveiro 127 V: 5500 W na posição mais quente, 4700 W e 2300 W (potência econômica) nas outras. | https://www.lorenzetti.com.br/manuais/topjet/manual.pdf |
| F5 | Cemig - Cartilha "Eficiência Energética: saiba como economizar energia" (2025). | Posição verão economiza até 30%. Banho bom de até 10 minutos. | https://www.cemig.com.br/wp-content/uploads/2025/09/Cartilha-Eficiencia-Energetica-Saiba-como-economizar-energia.pdf |
| F6 | Secretaria de Energia do Estado de São Paulo - "Energia Solar Paulista: levantamento do potencial" (2013), Tabela 3, com dados do Atlas Brasileiro de Energia Solar (INPE, 2006; medições de 1995 a 2005). | Irradiação global média no município de São Paulo: 4,589 kWh/m²/dia no ano e 3,784 no inverno. | https://www.absolar.org.br/wp-content/uploads/2021/02/S%C3%A3o%20Paulo.pdf |
| F7 | SINAPI (sistema de custos de referência de obras) consultado no Orcamentor: composição 103517 (ref. 09/2026) e insumo 34472 (ref. 10/2026). Custo médio nacional. | Aquecedor solar compacto, coletor de 2,0 m² e reservatório de 200 L: R$ 3.240,00 sem instalação e R$ 3.359,57 com instalação. | https://orcamentor.com/composicao/103517/ e https://orcamentor.com/insumo/34472/ |
| F8 | ABRASIP, ABRAVA e ABRINSTAL - "Guia e Software de Parametrização da Lei Solar de São Paulo" (Lei municipal 14.459/2007). | Fração solar mínima exigida de 40%; cerca de 70% tratada como fração ideal; 95 L/dia de água a 40 °C por pessoa; exemplo de 87,1 kWh/mês/m² com 15% de perdas. | https://solarthermalworld.org/sites/default/files/Sizing%20tool%20Sao%20Paulo.pdf |
| F9 | Altoé, L.; Oliveira Filho, D.; Carlo, J. C. "Análise energética de sistemas solares térmicos para diferentes demandas de água em uma residência unifamiliar". Ambiente Construído, v. 12, n. 3, p. 75-87, 2012. | Simulação em Viçosa (MG): aquecedor solar com apoio elétrico reduziu em média 70% a energia de aquecimento de água. | https://seer.ufrgs.br/ambienteconstruido/article/download/25706/21162 |
| F10 | Fundação Banco do Brasil - Transforma: "Aquecedor Solar de Baixo Custo" (tecnologia social da Sociedade do Sol). | Custo de R$ 1.000 a R$ 2.000 para casa de 4 pessoas (sem ano). Cerca de 75% de economia na energia de aquecer água. Durabilidade mínima de 10 anos. Precisa de caixa d'água e do chuveiro elétrico como apoio. | https://transforma.fbb.org.br/aquecedor-solar-de-baixo-custo/generate-pdf?id=139 |
| F11 | Greener - Estudo Estratégico de Geração Distribuída (1º semestre de 2025), citado pelo Canal Solar (30/09/2025). | Sistema fotovoltaico residencial de 4 kWp: preço médio de R$ 11.360. | https://canalsolar.com.br/gd-desempenho-primeiro-semestre-atencao-integradores/ |
| F12 | Olhar Digital - "Quanto custa instalar energia solar em casa?" (17/05/2026). | Sistema de 2 kWp: R$ 10 mil a R$ 14 mil (a matéria não cita a origem da tabela). | https://olhardigital.com.br/2026/05/17/curiosidades/quanto-custa-instalar-energia-solar-em-casa/ |
| F13 | Enel São Paulo - página "Tarifa de Energia Elétrica". | Confirma os valores da F1 para a tarifa convencional (0,78938 R$/kWh sem impostos). | https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html |
| F14 | Diário do Pará - "Aneel regulamenta a Tarifa Social do Luz do Povo". | Lei 15.235/2025 (programa Luz do Povo, sancionada em 08/10/2025). Exigências novas: conta no nome de alguém da família e endereço atualizado no CadÚnico. | https://diariodopara.com.br/noticias/brasil/aneel-regulamenta-a-tarifa-social-do-luz-do-povo/ |

## Observações sobre as fontes (o que não deu para confirmar)

1. **Impostos.** A F1 e a F13 trazem a tarifa **sem** ICMS e sem PIS/Cofins. Não achamos o valor final com tributos em fonte oficial. Todos os custos do projeto são **sem impostos e sem bandeira tarifária**. Na conta real o valor por kWh é maior, então a economia em reais tende a ser maior também.
2. **Tarifa Social na página da Enel (F13).** A página ainda mostra a tabela antiga por faixas (até 30, 31 a 100, 101 a 220 kWh). A resolução da ANEEL (F1, Tabela 3) traz a regra nova: 100% de desconto até 80 kWh e nada acima. Usamos a F1, que é o documento oficial.
3. **Fator de emissão.** A página oficial do MCTI (gov.br/mcti, SIRENE) não abriu para leitura automática (tem verificação anti-robô). Usamos a última **média anual** que conseguimos conferir (2023, 38,5 kg CO2/MWh) por meio de duas reportagens que citam o MCTI. Recomendação: o aluno deve abrir https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao no navegador e trocar pelo fator anual mais recente, se houver. Basta mudar uma linha do CSV.
4. **Irradiação.** O SunData do CRESESB não abriu no dia do acesso. Usamos o estudo do Governo de SP (F6), que tira os dados do Atlas Brasileiro de Energia Solar do INPE.
5. **Lei 15.235/2025.** O site do Planalto não abriu para leitura automática. O número da lei foi conferido em reportagem (F14). As regras de quem tem direito vêm da F2 (governo federal) e o desconto de 80 kWh vem da F1 (ANEEL).
6. **ASBC.** Os manuais da Sociedade do Sol não abriram. Os valores vêm da página da Fundação Banco do Brasil (F10), que é de divulgação da tecnologia e não informa o ano dos preços.
7. **Tempo de banho e número de banhos.** Não achamos dado oficial aberto (a Pesquisa de Posse e Hábitos do Procel/Eletrobras de 2019 não trouxe a seção do chuveiro na leitura). São premissas marcadas como ESTIMADO e podem ser mudadas na calculadora.
