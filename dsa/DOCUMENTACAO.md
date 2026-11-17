# Citizen Assist AI — Sistema de serviços e orientações ao cidadão

**Documentação técnica — Data Structures and Algorithms (DSA)**

- **Aluno:** Gustavo Zibini Belizario — RM 561376
- **Curso:** Ciência da Computação — 1º ano — FIAP
- **Trabalho:** Global Solution 2026.2 — Citizen Tech — entrega individual
- **Linguagem:** Python 3, apenas biblioteca padrão

## 1. Objetivo

O sistema é um protótipo de terminal que organiza **serviços e orientações ao cidadão** (emissão de documentos, assistência social, educação, saúde, atendimento comunitário e energia) e permite gerenciá-los por um **menu interativo**: cadastrar, listar, consultar, atualizar, excluir, pesquisar e ordenar.

O foco da disciplina está na estrutura de dados: todos os registros ficam em uma **lista simplesmente encadeada implementada à mão**, e a busca e a ordenação são **algoritmos escritos no próprio código** (busca linear e merge sort), sem `sorted()`, `list.sort()` nem conversão para listas nativas do Python.

O cenário é a fictícia **Central do Cidadão de Aurora**. Todos os dados de exemplo são inventados. O sistema é um protótipo educacional: não é canal oficial de atendimento, não se conecta a nenhuma plataforma de governo e não coleta dados pessoais (os registros descrevem serviços, não pessoas).

## 2. Campos dos registros

Cada serviço ou orientação é um objeto da classe `Servico` (arquivo `servico.py`), com os seis campos mínimos pedidos no enunciado:

<!-- larguras: 21 19 13 47 -->
| Campo | Atributo | Tipo | Regra de validação |
|---|---|---|---|
| Identificador único | `identificador` | inteiro | Obrigatório, número inteiro de 1 a 999999, não pode repetir na lista. Não muda depois do cadastro. |
| Título | `titulo` | texto | Obrigatório, até 80 caracteres. |
| Categoria | `categoria` | texto | Obrigatório, até 80 caracteres. Exemplos: Documentos, Saúde, Educação. |
| Descrição | `descricao` | texto | Obrigatório, até 200 caracteres. |
| Público-alvo | `publico_alvo` | texto | Obrigatório, até 80 caracteres. |
| Canal ou local de atendimento | `canal` | texto | Obrigatório, até 80 caracteres. |

As regras ficam em duas funções de `servico.py`: `validar_identificador(texto)` e `validar_texto(nome_campo, valor, limite)`. As duas devolvem um texto vazio quando o valor é válido ou a mensagem de erro que o menu mostra ao usuário. A função `normalizar(texto)` devolve o texto em minúsculas e sem acentos e é usada na pesquisa e na ordenação por título.

## 3. Lista encadeada

### 3.1 Estrutura

A lista está no arquivo `lista_encadeada.py` e usa duas classes:

- **`No`**: um elo da lista. Guarda um `servico` e a referência `proximo`, que aponta para o nó seguinte (ou `None` quando é o último).
- **`ListaEncadeada`**: guarda `inicio` (primeiro nó), `fim` (último nó) e `tamanho` (quantidade de nós). Com a lista vazia, `inicio` e `fim` valem `None`.

Não existe índice nem acesso direto ao "elemento número 5": para chegar a um nó é preciso partir de `inicio` e seguir as referências `proximo`, uma por uma.

```
 lista.inicio                                             lista.fim
      |                                                       |
      v                                                       v
 +---------+---------+     +---------+---------+     +---------+---------+
 | servico | proximo |---->| servico | proximo |---->| servico | proximo |----> None
 | id 104  |         |     | id 302  |         |     | id 102  |         |
 +---------+---------+     +---------+---------+     +---------+---------+
        nó 1                      nó 2                      nó 3

 lista.tamanho = 3
```

A referência `fim` existe para que ligar um nó novo no final não exija percorrer a lista inteira.

### 3.2 Operações

<!-- larguras: 16 26 58 -->
| Operação | Método | Como funciona |
|---|---|---|
| Inserção | `inserir(servico)` | Percorre a lista conferindo se o identificador já existe. Se existir, devolve `False` e nada muda. Se não, chama `anexar_no_fim`, que cria o nó, liga o antigo último a ele (`fim.proximo = novo`) e atualiza `fim` e `tamanho`. |
| Percurso | `percorrer(acao)` | Parte de `inicio` e segue `proximo` até `None`, chamando a função `acao` para cada serviço (o menu passa a função que mostra o serviço na tela). Devolve quantos nós visitou. |
| Busca por id | `buscar_por_id(id)` | Busca linear: compara o id de cada nó, do primeiro ao último. Devolve o serviço ou `None`. |
| Atualização | `atualizar(id, ...)` | Localiza o serviço com `buscar_por_id` e troca título, categoria, descrição, público-alvo e canal. O nó continua na mesma posição. Devolve `False` se o id não existir. |
| Remoção | `remover(id)` | Percorre guardando o nó `anterior`. Ao achar o nó, religa a lista em volta dele e ajusta `inicio`, `fim` e `tamanho`. Devolve o serviço removido ou `None`. |

### 3.3 Remoção: ajuste da estrutura

A remoção trata três posições diferentes:

- **Primeiro nó:** `inicio` passa a apontar para o segundo nó.
- **Nó do meio:** o nó anterior passa a apontar para o nó seguinte ao removido.
- **Último nó:** além de religar, `fim` passa a ser o nó anterior. Se a lista só tinha esse nó, `inicio` e `fim` voltam a ser `None`.

```
 Antes de remover o id 302 (nó do meio):

   [104] ----> [302] ----> [102] ----> None
  anterior     atual

 Depois de executar  anterior.proximo = atual.proximo :

   [104] ----------------> [102] ----> None       [302] ficou fora da lista
```

Em Python não há `free`: o nó removido deixa de ser referenciado pela lista e a própria linguagem libera a memória. O código ainda faz `atual.proximo = None` para o nó removido não continuar apontando para dentro da lista.

### 3.4 Uso de listas nativas

Nenhuma `list`, `dict` ou `set` do Python é usada para guardar, buscar ou ordenar registros. O resultado de uma pesquisa também é devolvido em uma `ListaEncadeada`. Os registros de exemplo são inseridos um a um por chamadas a `lista.inserir(...)`.

## 4. Organização do código

<!-- larguras: 24 76 -->
| Arquivo | Conteúdo |
|---|---|
| `servico.py` | Classe `Servico` (o registro), limites dos campos, `normalizar`, `validar_identificador` e `validar_texto`. |
| `lista_encadeada.py` | Classes `No` e `ListaEncadeada`: inserção, percurso, busca por id, atualização e remoção. |
| `algoritmos.py` | `pesquisar` (busca linear por título ou categoria) e a ordenação por merge sort: `ordenar`, `merge_sort`, `dividir_ao_meio`, `intercalar` e `vem_antes`. |
| `dados_exemplo.py` | `carregar_exemplos(lista)`: 15 registros fictícios de seis categorias. |
| `main.py` | Menu interativo: leitura e validação das entradas, mensagens e a função `executar_menu()`. |
| `testes.py` | 72 cenários de teste que imprimem entrada, esperado, observado e situação. |
| `evidencias/` | Saídas reais: `saida_testes.txt`, `sessao_menu.txt` e o roteiro digitado `entradas_menu.txt`. |
| `ferramentas/` | `gerar_documentacao.py`: monta este documento em PDF e copia as evidências para dentro dele. Não faz parte do sistema e é o único arquivo que usa biblioteca externa (reportlab). |

### 4.1 Onde está cada item do enunciado

<!-- larguras: 38 62 -->
| Item do enunciado | Onde encontrar |
|---|---|
| Modelo mínimo de informações (6 campos) | `servico.py`, classe `Servico` |
| Cadastrar validando campos e identificadores | `main.py` `opcao_cadastrar`; `servico.py` `validar_identificador` e `validar_texto`; `lista_encadeada.py` `inserir` |
| Consultar pelo identificador | `main.py` `opcao_consultar`; `lista_encadeada.py` `buscar_por_id` |
| Listar todos os registros | `main.py` `opcao_listar`; `lista_encadeada.py` `percorrer` |
| Atualizar um registro | `main.py` `opcao_atualizar`; `lista_encadeada.py` `atualizar` |
| Excluir ajustando a estrutura | `main.py` `opcao_excluir`; `lista_encadeada.py` `remover` |
| Pesquisar por atributo | `main.py` `opcao_pesquisar`; `algoritmos.py` `pesquisar` (título e categoria) |
| Ordenar por critério | `main.py` `opcao_ordenar`; `algoritmos.py` `ordenar` (título e identificador) |
| Menu com saída e mensagens claras | `main.py` `executar_menu` e `mostrar_menu` |
| Tratamento de entradas inválidas | `main.py` funções `ler_identificador`, `ler_campo_obrigatorio`, `ler_campo_para_atualizar` e `confirmar`; bloco `try/except` de `executar_menu` |
| Lista encadeada própria, com nós e referências | `lista_encadeada.py`, classes `No` e `ListaEncadeada` |
| Busca e ordenação implementadas no código | `lista_encadeada.py` `buscar_por_id`; `algoritmos.py` |
| Análise Big-O | Seção 7 deste documento |
| Testes e evidências | `testes.py`, pasta `evidencias/` e seção 8 deste documento |

## 5. Instruções de uso

### 5.1 Como executar

É preciso apenas o Python 3 (versão 3.6 ou superior; o sistema foi testado no Python 3.13). Não há nada para instalar ou compilar. Dentro da pasta `dsa`:

```
python3 main.py        (abre o menu interativo)
python3 testes.py      (executa os 72 cenários de teste)
```

No Windows o comando costuma ser `python` no lugar de `python3`.

Outro programa pode abrir o mesmo menu importando a função: `from main import executar_menu` e depois `executar_menu()`. Opcionalmente ela recebe uma `ListaEncadeada` já preenchida.

### 5.2 Opções do menu

O sistema começa com a lista vazia. A opção 8 carrega os 15 registros de exemplo.

<!-- larguras: 24 76 -->
| Opção | O que faz |
|---|---|
| 1 Cadastrar | Pede o identificador e os cinco campos de texto. O identificador é conferido primeiro; campo de texto inválido é perguntado de novo. |
| 2 Listar todos | Mostra todos os serviços na ordem em que estão encadeados e o total. |
| 3 Consultar por id | Mostra todos os campos do serviço com o identificador informado. |
| 4 Atualizar | Mostra os dados atuais e pede os novos. Enter sem digitar nada mantém o valor atual do campo. O identificador não muda. |
| 5 Excluir | Mostra o serviço e pede confirmação (`s` ou `n`) antes de remover. |
| 6 Pesquisar | Procura um trecho de texto no título ou na categoria, ignorando maiúsculas e acentos (`saude` encontra `Saúde`). |
| 7 Ordenar | Reordena a própria lista por título (ordem alfabética) ou por identificador (ordem crescente) e mostra o resultado. A nova ordem permanece para as próximas listagens. |
| 8 Carregar exemplos | Insere os registros de exemplo. Os que tiverem identificador já em uso são ignorados. |
| 0 Sair | Encerra o sistema. |

### 5.3 Mensagens para situações inválidas

<!-- larguras: 38 62 -->
| Situação | Mensagem exibida |
|---|---|
| Opção de menu inexistente, texto ou vazio | `Opção inválida: digite um número de 0 a 8.` |
| Listar, consultar, atualizar, excluir, pesquisar ou ordenar com a lista vazia | `Lista vazia: nenhum serviço cadastrado.` |
| Identificador com texto ou número não inteiro | `Entrada inválida: o identificador deve ser um número inteiro (exemplo: 101).` |
| Identificador vazio | `Entrada inválida: o identificador é obrigatório.` |
| Identificador zero, negativo ou grande demais | `Entrada inválida: o identificador deve estar entre 1 e 999999.` |
| Identificador já cadastrado | `Identificador duplicado: já existe um serviço com o id 104.` |
| Campo obrigatório vazio | `Entrada inválida: o campo 'Título' é obrigatório e não pode ficar vazio.` |
| Texto acima do limite | `Entrada inválida: o campo 'Título' aceita no máximo 80 caracteres (foram digitados 81).` |
| Identificador não encontrado | `Registro não encontrado: não existe serviço com o id 999.` |
| Pesquisa sem resultado | `Nenhum serviço encontrado com 'xyz' em título.` |
| Resposta diferente de s ou n na confirmação | `Resposta inválida: digite s para sim ou n para não.` |
| Ctrl+C | `Programa interrompido pelo usuário (Ctrl+C). Sistema encerrado.` |
| Fim da entrada (Ctrl+D ou Ctrl+Z) | `Entrada encerrada. Sistema encerrado.` |

Nenhuma dessas situações mostra erro técnico do Python (traceback).

## 6. Algoritmos de busca e ordenação

### 6.1 Busca por identificador: busca linear

Método `buscar_por_id` de `lista_encadeada.py`.

1. Começa no nó `inicio`.
2. Compara o identificador do nó atual com o procurado.
3. Se for igual, devolve o serviço e para.
4. Se não, avança para `proximo` e repete.
5. Se chegar a `None`, o identificador não existe e o método devolve `None`.

A busca linear foi escolhida porque é a que combina com a estrutura: a lista encadeada não tem acesso direto a uma posição (para chegar ao meio é preciso andar nó por nó), então a busca binária não traria ganho, e os registros não ficam necessariamente em ordem de identificador.

### 6.2 Pesquisa por título ou categoria: busca linear com filtro

Função `pesquisar(lista, campo, trecho)` de `algoritmos.py`.

1. Normaliza o trecho procurado (minúsculas, sem acentos). Trecho vazio devolve resultado vazio.
2. Percorre **todos** os nós, porque mais de um serviço pode combinar.
3. Em cada nó, normaliza o título ou a categoria e verifica se o trecho aparece dentro desse texto (operador `in` entre dois textos).
4. Cada serviço que combina é anexado a uma nova `ListaEncadeada` de resultados, na mesma ordem da lista original.
5. Devolve a lista de resultados. A lista original não é alterada.

### 6.3 Ordenação: merge sort na lista encadeada

Funções `ordenar`, `merge_sort`, `dividir_ao_meio`, `intercalar` e `vem_antes` de `algoritmos.py`. A ideia é dividir para conquistar:

1. **Caso base:** uma sequência vazia ou com um nó já está ordenada.
2. **Dividir** (`dividir_ao_meio`): dois ponteiros partem do início; o lento anda um nó por vez e o rápido anda dois. Quando o rápido chega ao fim, o lento está no meio. A ligação `proximo` do nó do meio é cortada e a sequência vira duas.
3. **Ordenar cada metade:** `merge_sort` chama a si mesma para a metade esquerda e para a direita.
4. **Intercalar** (`intercalar`): compara o primeiro nó de cada metade ordenada, liga o menor ao final do resultado e avança naquela metade. Quando uma metade acaba, o restante da outra é ligado de uma vez.
5. **Ajuste final** (`ordenar`): `inicio` recebe o primeiro nó do resultado e a lista é percorrida uma vez para acertar `fim`.

Exemplo com quatro identificadores:

```
 [104, 302, 102, 401]                  lista original
 [104, 302]      [102, 401]            dividir ao meio
 [104] [302]     [102] [401]           dividir até sobrar 1 nó em cada parte
 [104, 302]      [102, 401]            intercalar os pares
 [102, 104, 302, 401]                  intercalar as duas metades
```

A função `vem_antes` decide a ordem conforme o critério: por **identificador** compara os números; por **título** compara os títulos normalizados, para que `Ônibus` fique entre o M e o O e não depois do Z. Em caso de empate, entra primeiro o nó que já estava antes, então a ordenação é **estável**.

O merge sort foi escolhido porque se encaixa bem na lista encadeada: não precisa de acesso por índice, não cria nós novos (só refaz as ligações `proximo`) e tem custo O(n log n) em qualquer situação, ao contrário do bubble sort ou do insertion sort, que são O(n²) no pior caso.

## 7. Análise Big-O

### 7.1 Hipóteses adotadas

- **n** é a quantidade de nós da lista no momento da operação.
- **k** é a quantidade de serviços encontrados em uma pesquisa (k ≤ n).
- Conta-se como passo básico a visita a um nó ou a comparação entre dois registros.
- Os textos têm tamanho limitado pela validação do menu (80 ou 200 caracteres). Por isso, normalizar ou comparar um texto custa no máximo uma quantidade fixa de passos e é tratado como O(1) em relação a n.
- A lista não tem índice: chegar a um nó exige percorrer os anteriores.

### 7.2 Tabela de custos

<!-- larguras: 21 13 13 53 -->
| Operação (função) | Melhor caso | Pior caso | Justificativa, de acordo com o código |
|---|---|---|---|
| Inserção — `inserir` | O(n) | O(n) | Antes de inserir, `buscar_por_id` percorre os n nós para garantir que o id não existe. A ligação do nó novo no fim (`anexar_no_fim`) é O(1) por causa da referência `fim`. |
| Busca por id — `buscar_por_id` | O(1) | O(n) | Melhor caso: o id está no primeiro nó. Pior caso: está no último ou não existe. Em média percorre n/2 nós, o que também é O(n). |
| Pesquisa por título ou categoria — `pesquisar` | O(n) | O(n) | Sempre visita os n nós, porque pode haver vários resultados. Anexar cada resultado é O(1). Memória extra: O(k) nós na lista de resultados. |
| Atualização — `atualizar` | O(1) | O(n) | É uma busca por id seguida de cinco atribuições, que são O(1). |
| Exclusão — `remover` | O(1) | O(n) | Percorre até achar o nó (O(1) se for o primeiro, O(n) se for o último ou não existir). Religar os nós é O(1). |
| Listagem — `percorrer` | O(n) | O(n) | Visita cada nó uma vez. |
| Ordenação — `ordenar` (merge sort) | O(n log n) | O(n log n) | Cada nível de divisão custa O(n) (dividir e intercalar) e há cerca de log₂ n níveis. O acerto final de `fim` soma O(n). Memória extra: O(log n) da pilha de recursão; nenhum nó novo. |

### 7.3 Observações sobre a análise

- **Inserção é O(n), não O(1).** Só a ligação no fim é O(1). Como o sistema garante identificador único e não há índice, toda inserção bem-sucedida percorre a lista inteira. Uma inserção recusada por id duplicado pode parar antes (O(1) se o id repetido estiver no primeiro nó).
- **Inserir n registros em sequência é O(n²).** A primeira inserção percorre 0 nós, a segunda 1, a terceira 2, e assim por diante: 0 + 1 + ... + (n − 1) = n(n − 1)/2 comparações. É o preço da checagem de duplicidade. Para a opção 8, isso significa 15 inserções de custo O(n) cada.
- **No menu, algumas opções percorrem a lista duas vezes.** O cadastro consulta o id logo no início (para avisar antes de o usuário digitar os outros campos) e `inserir` confere de novo; atualizar e excluir primeiro buscam o serviço para mostrá-lo e depois chamam `atualizar` ou `remover`. Dois percursos são 2n passos, o que continua sendo O(n).
- **Merge sort não tem "melhor caso" mais rápido.** Mesmo com a lista já ordenada, a função divide tudo até sobrar um nó e intercala de volta. A relação é T(n) = 2·T(n/2) + O(n), que resulta em O(n log n).
- **Profundidade da recursão.** O merge sort chama a si mesmo cerca de log₂ n vezes em profundidade (10 níveis para 1.000 registros), muito abaixo do limite de recursão do Python.
- **Se os textos não tivessem limite,** os custos da pesquisa e da ordenação por título seriam multiplicados pelo tamanho dos textos comparados.

## 8. Testes e evidências

### 8.1 Como os testes foram feitos

Há dois tipos de evidência, ambos saídas reais de execução guardadas na pasta `evidencias/`:

- **`saida_testes.txt`**: saída de `python3 testes.py`. O arquivo `testes.py` executa cada cenário contra o código do sistema, compara o resultado observado com o esperado e imprime a situação (OK ou FALHOU). Os cenários do grupo 8 executam o menu de verdade, trocando o teclado por um texto com as respostas.
- **`sessao_menu.txt`**: saída de `python3 main.py < evidencias/entradas_menu.txt`, uma sessão completa do menu em que as respostas do usuário vêm do arquivo `entradas_menu.txt`. Está reproduzida no Apêndice A.

Para repetir:

```
python3 testes.py > evidencias/saida_testes.txt
python3 main.py < evidencias/entradas_menu.txt > evidencias/sessao_menu.txt
```

Nos cenários da tabela, o texto `ids: 30 10 20 | tamanho: 3 | fim: 20` é um retrato da lista obtido percorrendo os nós um a um: os identificadores na ordem do encadeamento, o valor de `tamanho` e o identificador do nó `fim`. Assim cada cenário confere também se a estrutura ficou correta depois da operação.

Os testes usam múltiplos registros (os 15 exemplos e uma lista de 200 registros) e o grupo 1 inteiro trata de operações sobre lista vazia.

### 8.2 Resultados dos cenários de teste

<!-- EVIDENCIAS:INICIO -->
**Resumo da execução:** 72 cenários executados, 72 OK, 0 FALHOU. Linha final do arquivo `evidencias/saida_testes.txt`.

**Grupo 1. OPERAÇÕES SOBRE LISTA VAZIA**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T01 | Percorrer (listar) uma lista vazia | lista recém-criada; percorrer() | 0 nó(s) visitado(s) \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | 0 nó(s) visitado(s) \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |
| T02 | Consultar por id em lista vazia | buscar_por_id(10) | não encontrado | não encontrado | OK |
| T03 | Excluir em lista vazia | remover(10) | não encontrado \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | não encontrado \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |
| T04 | Atualizar em lista vazia | atualizar(10, ...) | False | False | OK |
| T05 | Pesquisar em lista vazia | pesquisar(titulo, 'rg') | 0 resultado(s) | 0 resultado(s) | OK |
| T06 | Ordenar lista vazia (não pode dar erro) | ordenar(titulo) | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |

**Grupo 2. CADASTRO (INSERÇÃO) E VALIDAÇÃO**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T07 | Inserir o primeiro registro em lista vazia | inserir(id 30) | True \| ids: 30 \| tamanho: 1 \| fim: 30 | True \| ids: 30 \| tamanho: 1 \| fim: 30 | OK |
| T08 | Inserir mais três registros (cada um entra no fim) | inserir(id 10), inserir(id 20), inserir(id 40) | ids: 30 10 20 40 \| tamanho: 4 \| fim: 40 | ids: 30 10 20 40 \| tamanho: 4 \| fim: 40 | OK |
| T09 | Recusar identificador duplicado sem alterar a lista | inserir(id 20) com o id 20 já cadastrado | False \| ids: 30 10 20 40 \| tamanho: 4 \| fim: 40 | False \| ids: 30 10 20 40 \| tamanho: 4 \| fim: 40 | OK |
| T10 | Identificador com texto no lugar de número | validar_identificador('abc') | o identificador deve ser um número inteiro (exemplo: 101). | o identificador deve ser um número inteiro (exemplo: 101). | OK |
| T11 | Identificador com número não inteiro | validar_identificador('3.5') | o identificador deve ser um número inteiro (exemplo: 101). | o identificador deve ser um número inteiro (exemplo: 101). | OK |
| T12 | Identificador vazio | validar_identificador('') | o identificador é obrigatório. | o identificador é obrigatório. | OK |
| T13 | Identificador negativo | validar_identificador('-5') | o identificador deve estar entre 1 e 999999. | o identificador deve estar entre 1 e 999999. | OK |
| T14 | Identificador zero | validar_identificador('0') | o identificador deve estar entre 1 e 999999. | o identificador deve estar entre 1 e 999999. | OK |
| T15 | Identificador válido | validar_identificador('25') | válido | válido | OK |
| T16 | Campo obrigatório vazio (só espaços) | validar_texto('Título', '   ', 80) | o campo 'Título' é obrigatório e não pode ficar vazio. | o campo 'Título' é obrigatório e não pode ficar vazio. | OK |
| T17 | Campo de texto acima do limite | validar_texto('Título', 81 letras 'a', 80) | o campo 'Título' aceita no máximo 80 caracteres (foram digitados 81). | o campo 'Título' aceita no máximo 80 caracteres (foram digitados 81). | OK |
| T18 | Campo de texto válido | validar_texto('Título', 'Renovação da CNH', 80) | válido | válido | OK |
| T19 | Carregar os registros de exemplo (múltiplos registros) | carregar_exemplos(lista vazia) | 15 inseridos \| ids: 104 302 102 401 203 106 601 101 501 105 301 402 103 502 602 \| tamanho: 15 \| fim: 602 | 15 inseridos \| ids: 104 302 102 401 203 106 601 101 501 105 301 402 103 502 602 \| tamanho: 15 \| fim: 602 | OK |
| T20 | Carregar os exemplos de novo: todos os ids já existem | carregar_exemplos(lista já carregada) | 0 inseridos \| tamanho: 15 | 0 inseridos \| tamanho: 15 | OK |
| T21 | Registros de exemplo respeitam as validações | validar os 6 campos dos 15 exemplos | 0 problema(s) | 0 problema(s) | OK |

**Grupo 3. CONSULTA POR IDENTIFICADOR (BUSCA LINEAR)**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T22 | Consultar o registro do primeiro nó | buscar_por_id(104) | encontrado: [104] Segunda via da Carteira de Identidade (RG) | encontrado: [104] Segunda via da Carteira de Identidade (RG) | OK |
| T23 | Consultar um registro do meio da lista | buscar_por_id(101) | encontrado: [101] Carteira de Trabalho digital | encontrado: [101] Carteira de Trabalho digital | OK |
| T24 | Consultar o registro do último nó | buscar_por_id(602) | encontrado: [602] Economia de energia em casa | encontrado: [602] Economia de energia em casa | OK |
| T25 | Consultar identificador que não existe | buscar_por_id(999) | não encontrado | não encontrado | OK |

**Grupo 4. ATUALIZAÇÃO**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T26 | Atualizar um registro existente | atualizar(10, 'Título novo', 'Categoria nova', ...) | True \| Título novo \| Categoria nova \| Descrição nova \| Público novo \| Canal novo | True \| Título novo \| Categoria nova \| Descrição nova \| Público novo \| Canal novo | OK |
| T27 | Atualização não muda a posição nem os outros registros | lista após atualizar(10, ...) | ids: 30 10 20 \| tamanho: 3 \| fim: 20 \| Serviço de teste / Título novo / Serviço de teste | ids: 30 10 20 \| tamanho: 3 \| fim: 20 \| Serviço de teste / Título novo / Serviço de teste | OK |
| T28 | Atualizar identificador que não existe | atualizar(99, ...) | False \| ids: 30 10 20 \| tamanho: 3 \| fim: 20 | False \| ids: 30 10 20 \| tamanho: 3 \| fim: 20 | OK |

**Grupo 5. EXCLUSÃO (INÍCIO, MEIO E FIM)**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T29 | Excluir o primeiro nó (o início passa a ser o 2º) | lista 30 10 20 40 50; remover(30) | encontrado: [30] Serviço de teste \| ids: 10 20 40 50 \| tamanho: 4 \| fim: 50 | encontrado: [30] Serviço de teste \| ids: 10 20 40 50 \| tamanho: 4 \| fim: 50 | OK |
| T30 | Excluir um nó do meio (o anterior é religado ao seguinte) | lista 10 20 40 50; remover(20) | encontrado: [20] Serviço de teste \| ids: 10 40 50 \| tamanho: 3 \| fim: 50 | encontrado: [20] Serviço de teste \| ids: 10 40 50 \| tamanho: 3 \| fim: 50 | OK |
| T31 | Excluir o último nó (o fim passa a ser o anterior) | lista 10 40 50; remover(50) | encontrado: [50] Serviço de teste \| ids: 10 40 \| tamanho: 2 \| fim: 40 | encontrado: [50] Serviço de teste \| ids: 10 40 \| tamanho: 2 \| fim: 40 | OK |
| T32 | Excluir identificador que não existe | lista 10 40; remover(77) | não encontrado \| ids: 10 40 \| tamanho: 2 \| fim: 40 | não encontrado \| ids: 10 40 \| tamanho: 2 \| fim: 40 | OK |
| T33 | Inserir depois de excluir o último (o novo fim funciona) | lista 10 40; inserir(id 60) | ids: 10 40 60 \| tamanho: 3 \| fim: 60 | ids: 10 40 60 \| tamanho: 3 \| fim: 60 | OK |
| T34 | Excluir todos os registros: a lista volta a ficar vazia | remover(10), remover(40), remover(60) | vazia: True \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | vazia: True \| ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |
| T35 | Inserir de novo depois de esvaziar a lista | inserir(id 5) | ids: 5 \| tamanho: 1 \| fim: 5 | ids: 5 \| tamanho: 1 \| fim: 5 | OK |

**Grupo 6. PESQUISA POR TÍTULO E POR CATEGORIA**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T36 | Pesquisar no título, sem acento e em minúsculas | pesquisar(titulo, 'certidoes') | ids: 105 \| tamanho: 1 \| fim: 105 | ids: 105 \| tamanho: 1 \| fim: 105 | OK |
| T37 | Pesquisar no título, em maiúsculas, com mais de um resultado | pesquisar(titulo, 'CARTEIRA') | ids: 104 101 \| tamanho: 2 \| fim: 101 | ids: 104 101 \| tamanho: 2 \| fim: 101 | OK |
| T38 | Pesquisar na categoria ignorando o acento | pesquisar(categoria, 'saude') | ids: 401 402 \| tamanho: 2 \| fim: 402 | ids: 401 402 \| tamanho: 2 \| fim: 402 | OK |
| T39 | Pesquisar na categoria por parte da palavra | pesquisar(categoria, 'DOCUM') | ids: 104 102 106 101 105 103 \| tamanho: 6 \| fim: 103 | ids: 104 102 106 101 105 103 \| tamanho: 6 \| fim: 103 | OK |
| T40 | Pesquisar um trecho que não existe | pesquisar(titulo, 'xyz') | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |
| T41 | Pesquisar com trecho vazio não devolve a lista inteira | pesquisar(titulo, '   ') | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | ids: (nenhum) \| tamanho: 0 \| fim: (nenhum) | OK |
| T42 | A pesquisa não altera a lista original | lista original depois das pesquisas acima | ids: 104 302 102 401 203 106 601 101 501 105 301 402 103 502 602 \| tamanho: 15 \| fim: 602 | ids: 104 302 102 401 203 106 601 101 501 105 301 402 103 502 602 \| tamanho: 15 \| fim: 602 | OK |

**Grupo 7. ORDENAÇÃO (MERGE SORT NA LISTA ENCADEADA)**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T43 | Ordenar os 15 exemplos por identificador | ordenar(identificador) | ids: 101 102 103 104 105 106 203 301 302 401 402 501 502 601 602 \| tamanho: 15 \| fim: 602 | ids: 101 102 103 104 105 106 203 301 302 401 402 501 502 601 602 \| tamanho: 15 \| fim: 602 | OK |
| T44 | Ordenar os 15 exemplos por título (ordem alfabética) | ordenar(titulo) | ids: 402 203 101 105 602 301 102 302 502 501 103 104 601 106 401 \| tamanho: 15 \| fim: 401 | ids: 402 203 101 105 602 301 102 302 502 501 103 104 601 106 401 \| tamanho: 15 \| fim: 401 | OK |
| T45 | Ordenar por título ignorando acentos e maiúsculas | títulos: Zeladoria, água e esgoto, Biblioteca, Ônibus, energia | água e esgoto / Biblioteca / energia / Ônibus / Zeladoria | água e esgoto / Biblioteca / energia / Ônibus / Zeladoria | OK |
| T46 | Ordenar lista com um único registro | lista 7; ordenar(identificador) | ids: 7 \| tamanho: 1 \| fim: 7 | ids: 7 \| tamanho: 1 \| fim: 7 | OK |
| T47 | Ordenar lista com dois registros | lista 9 4; ordenar(identificador) | ids: 4 9 \| tamanho: 2 \| fim: 9 | ids: 4 9 \| tamanho: 2 \| fim: 9 | OK |
| T48 | Ordenar lista que já está em ordem | lista 1 2 3 4 5; ordenar(identificador) | ids: 1 2 3 4 5 \| tamanho: 5 \| fim: 5 | ids: 1 2 3 4 5 \| tamanho: 5 \| fim: 5 | OK |
| T49 | Ordenar lista em ordem invertida | lista 5 4 3 2 1; ordenar(identificador) | ids: 1 2 3 4 5 \| tamanho: 5 \| fim: 5 | ids: 1 2 3 4 5 \| tamanho: 5 \| fim: 5 | OK |
| T50 | Inserir e excluir depois de ordenar (início e fim corretos) | lista ordenada 1 2 3 4 5; inserir(id 6); remover(1) | encontrado: [1] Serviço de teste \| ids: 2 3 4 5 6 \| tamanho: 5 \| fim: 6 | encontrado: [1] Serviço de teste \| ids: 2 3 4 5 6 \| tamanho: 5 \| fim: 6 | OK |
| T51 | Ordenar 200 registros embaralhados | 200 ids gerados por (i * 37) % 211 + 1; ordenar(identificador) | antes ordenada: não \| depois ordenada: sim \| tamanho: 200 \| primeiro: 1 \| fim: 211 | antes ordenada: não \| depois ordenada: sim \| tamanho: 200 \| primeiro: 1 \| fim: 211 | OK |

**Grupo 8. MENU INTERATIVO E ENTRADAS INVÁLIDAS (menu executado de verdade)**

<!-- evidencias -->
| Nº | Cenário | Entrada | Esperado | Observado | Situação |
|---|---|---|---|---|---|
| T52 | Opção de menu inexistente | teclado: 99, 0 | Opção inválida: digite um número de 0 a 8. | Opção inválida: digite um número de 0 a 8. | OK |
| T53 | Texto no lugar do número da opção | teclado: abc, 0 | Opção inválida: digite um número de 0 a 8. | Opção inválida: digite um número de 0 a 8. | OK |
| T54 | Opção em branco (só Enter) | teclado: (Enter), 0 | Opção inválida: digite um número de 0 a 8. | Opção inválida: digite um número de 0 a 8. | OK |
| T55 | Listar com a lista vazia | teclado: 2, 0 | Lista vazia: nenhum serviço cadastrado. | Lista vazia: nenhum serviço cadastrado. | OK |
| T56 | Excluir com a lista vazia | teclado: 5, 0 | Lista vazia: nenhum serviço cadastrado. | Lista vazia: nenhum serviço cadastrado. | OK |
| T57 | Consulta com texto no lugar do identificador | teclado: 8, 3, abc, 0 | Entrada inválida: o identificador deve ser um número inteiro (exemplo: 101). | Entrada inválida: o identificador deve ser um número inteiro (exemplo: 101). | OK |
| T58 | Consulta de identificador que não existe | teclado: 8, 3, 999, 0 | Registro não encontrado: não existe serviço com o id 999. | Registro não encontrado: não existe serviço com o id 999. | OK |
| T59 | Cadastro com identificador duplicado | teclado: 8, 1, 104, 0 | Identificador duplicado: já existe um serviço com o id 104. | Identificador duplicado: já existe um serviço com o id 104. | OK |
| T60 | Cadastro com título vazio: o menu avisa e pergunta de novo | teclado: 1, 700, (Enter), Horta comunitária, ... | Entrada inválida: o campo 'Título' é obrigatório e não pode ficar vazio. | Entrada inválida: o campo 'Título' é obrigatório e não pode ficar vazio. | OK |
| T61 | Mesmo cadastro, depois de corrigir o título: registro gravado | continuação: ..., Praça central; depois 3, 700, 0 | Serviço 700 cadastrado com sucesso. \| [700] Horta comunitária | Serviço 700 cadastrado com sucesso. \| [700] Horta comunitária | OK |
| T62 | Atualizar pelo menu só o canal (Enter mantém os outros campos) | teclado: 8, 4, 103, (Enter) x4, Balcão 7, 3, 103, 0 | Serviço 103 atualizado com sucesso. \| Canal ou local: Balcão 7 \| [103] Renovação da CNH | Serviço 103 atualizado com sucesso. \| Canal ou local: Balcão 7 \| [103] Renovação da CNH | OK |
| T63 | Exclusão com resposta inválida na confirmação e depois 's' | teclado: 8, 5, 104, talvez, s, 3, 104, 0 | Resposta inválida: digite s para sim ou n para não. \| Serviço 104 excluído. Restam 14 serviço(s). \| Registro não encontrado: não existe serviço com o id 104. | Resposta inválida: digite s para sim ou n para não. \| Serviço 104 excluído. Restam 14 serviço(s). \| Registro não encontrado: não existe serviço com o id 104. | OK |
| T64 | Exclusão cancelada com 'n' | teclado: 8, 5, 104, n, 0 | Exclusão cancelada. Nada foi alterado. | Exclusão cancelada. Nada foi alterado. | OK |
| T65 | Pesquisa pelo menu sem resultados | teclado: 8, 6, 1, zzz, 0 | Nenhum serviço encontrado com 'zzz' em título. | Nenhum serviço encontrado com 'zzz' em título. | OK |
| T66 | Pesquisa pelo menu por categoria | teclado: 8, 6, 2, EDUCACAO, 0 | Total: 2 serviço(s). \| [302] Matrícula na rede municipal de ensino \| [301] Educação de Jovens e Adultos (EJA) | Total: 2 serviço(s). \| [302] Matrícula na rede municipal de ensino \| [301] Educação de Jovens e Adultos (EJA) | OK |
| T67 | Critério de ordenação inexistente | teclado: 8, 7, 5, 0 | Opção inválida: digite 1 ou 2. | Opção inválida: digite 1 ou 2. | OK |
| T68 | Ordenar pelo menu por identificador | teclado: 8, 7, 2, 0 | Lista ordenada por identificador: \| [101] aparece antes de [602]: True | Lista ordenada por identificador: \| [101] aparece antes de [602]: True | OK |
| T69 | Carregar exemplos duas vezes: ids repetidos são ignorados | teclado: 8, 8, 0 | 15 não entraram porque o identificador já estava em uso. | 15 não entraram porque o identificador já estava em uso. | OK |
| T70 | Sair pelo menu e aviso de protótipo educacional | teclado: 0 | AVISO: protótipo educacional com dados FICTÍCIOS. \| Sistema encerrado. Até logo! | AVISO: protótipo educacional com dados FICTÍCIOS. \| Sistema encerrado. Até logo! | OK |
| T71 | Fim da entrada (EOF / Ctrl+D) no meio de um cadastro | teclado: 8, 1 e a entrada termina | Entrada encerrada. Sistema encerrado. \| erros técnicos: 0 | Entrada encerrada. Sistema encerrado. \| erros técnicos: 0 | OK |
| T72 | Ctrl+C durante a leitura da opção | teclado: Ctrl+C (KeyboardInterrupt simulado) | Programa interrompido pelo usuário (Ctrl+C). Sistema encerrado. \| erros técnicos: 0 | Programa interrompido pelo usuário (Ctrl+C). Sistema encerrado. \| erros técnicos: 0 | OK |
<!-- EVIDENCIAS:FIM -->

### 8.3 Roteiro da sessão do menu

A sessão do Apêndice A segue este roteiro. Todas as mensagens esperadas apareceram na saída gravada.

<!-- larguras: 7 31 26 36 -->
| Passo | O que foi feito | Entrada digitada | Resultado esperado |
|---|---|---|---|
| 1 | Listar e consultar com a lista vazia | `2`; `3` | Mensagem de lista vazia |
| 2 | Opções inexistentes | `99`; `abc` | Mensagem de opção inválida |
| 3 | Carregar exemplos e listar | `8`; `2` | 15 registros na ordem de inserção |
| 4 | Cadastro com id inválido | `1`, `abc` | Identificador deve ser número inteiro |
| 5 | Cadastro com id duplicado | `1`, `104` | Identificador duplicado |
| 6 | Cadastro com título vazio e depois correto | `1`, `700`, Enter, dados válidos | Aviso de campo obrigatório; serviço 700 cadastrado |
| 7 | Consultas | `3`, `700`; `3`, `999`; `3`, `-5` | Mostra o 700; não encontrado; id fora da faixa |
| 8 | Atualização mantendo três campos | `4`, `700`, novo título, Enter três vezes, novo canal | Serviço 700 atualizado; campos mantidos iguais |
| 9 | Atualização de id inexistente | `4`, `999` | Registro não encontrado |
| 10 | Pesquisas | `6`, `1`, `carteira`; `6`, `2`, `saude`; `6`, `1`, `xyz`; `6`, `3` | 2 resultados; 2 resultados; nenhum resultado; opção inválida |
| 11 | Exclusão do primeiro nó | `5`, `104`, `talvez`, `s` | Resposta inválida; depois excluído, restam 15 |
| 12 | Exclusão de nó do meio | `5`, `105`, `s` | Excluído, restam 14 |
| 13 | Exclusão do último nó | `5`, `700`, `s` | Excluído, restam 13 |
| 14 | Exclusão cancelada e id inexistente | `5`, `602`, `n`; `5`, `999` | Exclusão cancelada; não encontrado |
| 15 | Ordenação por título | `7`, `1` | 13 registros em ordem alfabética, sem 104, 105 e 700 |
| 16 | Ordenação por identificador | `7`, `2` | 13 registros de 101 a 602 |
| 17 | Critério inexistente e saída | `7`, `9`; `0` | Opção inválida; sistema encerrado |

## 9. Limitações

- Os dados ficam apenas na memória: ao sair, os registros cadastrados são perdidos. Gravação em arquivo não foi pedida no enunciado.
- A checagem de identificador duplicado torna a inserção O(n). Para listas muito grandes seria preciso uma estrutura auxiliar de índice, o que foge do objetivo do trabalho.
- Os limites de tamanho dos textos são aplicados pelo menu. Código que chame `lista.inserir` diretamente precisa validar os campos antes.
- A pesquisa encontra trechos exatos do texto (sem considerar erros de digitação).

## Apêndice A — Sessão real do menu

Conteúdo do arquivo `evidencias/sessao_menu.txt`, sem alterações. No PDF, linhas muito longas continuam na linha de baixo, com recuo.

<!-- SESSAO:INICIO -->
```text
================================================================
 AVISO: protótipo educacional com dados FICTÍCIOS.
 Não é um canal oficial de atendimento e não coleta
 dados pessoais. Os dados ficam só na memória e somem
 ao sair. Dica: a opção 8 carrega registros de exemplo.
================================================================

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 2
--- Listar todos os serviços ---
Lista vazia: nenhum serviço cadastrado.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 3
--- Consultar serviço pelo identificador ---
Lista vazia: nenhum serviço cadastrado.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 99
Opção inválida: digite um número de 0 a 8.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: abc
Opção inválida: digite um número de 0 a 8.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 8
--- Carregar registros de exemplo ---
15 registro(s) de exemplo carregado(s).
A lista tem agora 15 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 2
--- Listar todos os serviços ---
[104] Segunda via da Carteira de Identidade (RG)
    Categoria     : Documentos
    Descrição     : Segunda via custa R$ 38,00 e fica pronta em 10 dias úteis. Agendamento obrigatório pelo portal. Leve certidão e comprovante de residência.
    Público-alvo  : Qualquer pessoa; menores de 12 anos acompanhados do responsável legal
    Canal ou local: Posto de Identificação de Aurora
[302] Matrícula na rede municipal de ensino
    Categoria     : Educação
    Descrição     : Orientação para matricular crianças e adolescentes nas escolas municipais. Matrícula gratuita, feita na escola mais próxima de casa.
    Público-alvo  : Responsáveis por crianças e adolescentes em idade escolar
    Canal ou local: Secretaria de Educação de Aurora ou escola municipal mais próxima
[102] Inscrição no CPF
    Categoria     : Documentos
    Descrição     : Inscrição e correção de dados gratuitas pelo portal, com comprovante em até 2 dias úteis. O atendimento presencial tem taxa de R$ 7,00.
    Público-alvo  : Quem precisa se inscrever no CPF ou corrigir dados
    Canal ou local: Portal da Central do Cidadão ou balcão de atendimento
[401] Vacinação de rotina
    Categoria     : Saúde
    Descrição     : Aplicação das vacinas do calendário básico para todas as idades. Gratuita e sem agendamento; leve a carteira de vacinação.
    Público-alvo  : Crianças, adultos e idosos
    Canal ou local: Unidade Básica de Saúde Central de Aurora
[203] Cadastro em programas sociais
    Categoria     : Assistência social
    Descrição     : Orientação e inscrição de famílias de baixa renda nos programas sociais do município. Atendimento gratuito.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora
[106] Título de eleitor
    Categoria     : Documentos
    Descrição     : Primeira via, segunda via e transferência gratuitas. O título digital sai em até 5 dias úteis. O cadastro fecha 150 dias antes de cada eleição.
    Público-alvo  : Eleitores a partir de 16 anos
    Canal ou local: Portal da Central do Cidadão ou Central Eleitoral de Aurora
[601] Tarifa social de energia elétrica
    Categoria     : Energia
    Descrição     : Orientação sobre o desconto na conta de luz para famílias de baixa renda e sobre como pedir o benefício.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora ou portal da Central do Cidadão
[101] Carteira de Trabalho digital
    Categoria     : Documentos
    Descrição     : Gratuita em qualquer canal. A versão digital fica disponível logo após o cadastro. Não precisa de agendamento.
    Público-alvo  : Trabalhadores; menores de 18 anos acompanhados do responsável legal
    Canal ou local: Portal ou aplicativo da Central do Cidadão
[501] Ouvidoria comunitária
    Categoria     : Atendimento comunitário
    Descrição     : Canal para registrar sugestões, elogios e reclamações sobre os serviços públicos do bairro.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Balcão da Central do Cidadão, de segunda a sexta, das 8h às 17h
[105] Certidões de nascimento, casamento e óbito
    Categoria     : Documentos
    Descrição     : No balcão: R$ 55,00, pronta em 5 dias úteis. Pelo portal, em PDF: R$ 49,00, pronta em 3 dias úteis. Isenção no balcão para baixa renda.
    Público-alvo  : A própria pessoa ou terceiro com procuração simples
    Canal ou local: Cartório Central de Aurora ou portal da Central do Cidadão
[301] Educação de Jovens e Adultos (EJA)
    Categoria     : Educação
    Descrição     : Turmas noturnas gratuitas para quem não concluiu o ensino fundamental ou médio na idade regular.
    Público-alvo  : Jovens e adultos a partir de 15 anos
    Canal ou local: Escolas municipais com turmas de EJA
[402] Agendamento de consulta médica
    Categoria     : Saúde
    Descrição     : Marcação de consulta com clínico geral na unidade de saúde do bairro. Leve documento original com foto.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Unidade Básica de Saúde do bairro
[103] Renovação da CNH
    Categoria     : Documentos
    Descrição     : Taxa de R$ 180,00; exame médico pago à parte na clínica credenciada. A nova CNH fica pronta em 7 dias úteis após a aprovação no exame.
    Público-alvo  : Motoristas com CNH vencida ou a até 30 dias do vencimento
    Canal ou local: Agendamento obrigatório pelo portal da Central do Cidadão
[502] Ônibus da Cidadania: atendimento itinerante
    Categoria     : Atendimento comunitário
    Descrição     : Unidade móvel que leva orientação sobre documentos e serviços aos bairros mais distantes. Consulte o calendário no portal.
    Público-alvo  : Moradores de bairros distantes do centro
    Canal ou local: Praças e escolas dos bairros, conforme calendário do portal
[602] Economia de energia em casa
    Categoria     : Energia
    Descrição     : Orientações simples para reduzir o consumo: lâmpadas de LED, banho mais curto e aparelhos fora da tomada quando não estão em uso.
    Público-alvo  : Todos os moradores
    Canal ou local: Portal da Central do Cidadão e mutirões de bairro
Total: 15 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 1
--- Cadastrar serviço ---
Cadastre apenas informações do serviço. Não digite dados
pessoais (nome, CPF, telefone ou endereço de pessoas).
Identificador (número inteiro): abc
Entrada inválida: o identificador deve ser um número inteiro (exemplo: 101).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 1
--- Cadastrar serviço ---
Cadastre apenas informações do serviço. Não digite dados
pessoais (nome, CPF, telefone ou endereço de pessoas).
Identificador (número inteiro): 104
Identificador duplicado: já existe um serviço com o id 104.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 1
--- Cadastrar serviço ---
Cadastre apenas informações do serviço. Não digite dados
pessoais (nome, CPF, telefone ou endereço de pessoas).
Identificador (número inteiro): 700
Título: 
Entrada inválida: o campo 'Título' é obrigatório e não pode ficar vazio.
Título: Horta comunitária do bairro
Categoria: Atendimento comunitário
Descrição: Canteiros coletivos mantidos por voluntários. Qualquer morador pode participar dos mutirões de plantio.
Público-alvo: Moradores de Aurora
Canal ou local de atendimento: Praça Central de Aurora
Serviço 700 cadastrado com sucesso.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 3
--- Consultar serviço pelo identificador ---
Identificador (número inteiro): 700
[700] Horta comunitária do bairro
    Categoria     : Atendimento comunitário
    Descrição     : Canteiros coletivos mantidos por voluntários. Qualquer morador pode participar dos mutirões de plantio.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Praça Central de Aurora

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 3
--- Consultar serviço pelo identificador ---
Identificador (número inteiro): 999
Registro não encontrado: não existe serviço com o id 999.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 3
--- Consultar serviço pelo identificador ---
Identificador (número inteiro): -5
Entrada inválida: o identificador deve estar entre 1 e 999999.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 4
--- Atualizar serviço ---
Identificador (número inteiro): 700
Dados atuais:
[700] Horta comunitária do bairro
    Categoria     : Atendimento comunitário
    Descrição     : Canteiros coletivos mantidos por voluntários. Qualquer morador pode participar dos mutirões de plantio.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Praça Central de Aurora
Digite os novos dados. O identificador não pode ser alterado.
Título (Enter mantém o atual): Horta comunitária e compostagem
Categoria (Enter mantém o atual): 
Descrição (Enter mantém o atual): 
Público-alvo (Enter mantém o atual): 
Canal ou local de atendimento (Enter mantém o atual): Praça Central de Aurora, ao lado da biblioteca
Serviço 700 atualizado com sucesso.
[700] Horta comunitária e compostagem
    Categoria     : Atendimento comunitário
    Descrição     : Canteiros coletivos mantidos por voluntários. Qualquer morador pode participar dos mutirões de plantio.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Praça Central de Aurora, ao lado da biblioteca

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 4
--- Atualizar serviço ---
Identificador (número inteiro): 999
Registro não encontrado: não existe serviço com o id 999.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 6
--- Pesquisar por título ou categoria ---
 1 - Pesquisar no título
 2 - Pesquisar na categoria
Onde pesquisar: 1
Trecho procurado: carteira
Serviços com 'carteira' em título:
[104] Segunda via da Carteira de Identidade (RG)
    Categoria     : Documentos
    Descrição     : Segunda via custa R$ 38,00 e fica pronta em 10 dias úteis. Agendamento obrigatório pelo portal. Leve certidão e comprovante de residência.
    Público-alvo  : Qualquer pessoa; menores de 12 anos acompanhados do responsável legal
    Canal ou local: Posto de Identificação de Aurora
[101] Carteira de Trabalho digital
    Categoria     : Documentos
    Descrição     : Gratuita em qualquer canal. A versão digital fica disponível logo após o cadastro. Não precisa de agendamento.
    Público-alvo  : Trabalhadores; menores de 18 anos acompanhados do responsável legal
    Canal ou local: Portal ou aplicativo da Central do Cidadão
Total: 2 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 6
--- Pesquisar por título ou categoria ---
 1 - Pesquisar no título
 2 - Pesquisar na categoria
Onde pesquisar: 2
Trecho procurado: saude
Serviços com 'saude' em categoria:
[401] Vacinação de rotina
    Categoria     : Saúde
    Descrição     : Aplicação das vacinas do calendário básico para todas as idades. Gratuita e sem agendamento; leve a carteira de vacinação.
    Público-alvo  : Crianças, adultos e idosos
    Canal ou local: Unidade Básica de Saúde Central de Aurora
[402] Agendamento de consulta médica
    Categoria     : Saúde
    Descrição     : Marcação de consulta com clínico geral na unidade de saúde do bairro. Leve documento original com foto.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Unidade Básica de Saúde do bairro
Total: 2 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 6
--- Pesquisar por título ou categoria ---
 1 - Pesquisar no título
 2 - Pesquisar na categoria
Onde pesquisar: 1
Trecho procurado: xyz
Nenhum serviço encontrado com 'xyz' em título.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 6
--- Pesquisar por título ou categoria ---
 1 - Pesquisar no título
 2 - Pesquisar na categoria
Onde pesquisar: 3
Opção inválida: digite 1 ou 2.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 5
--- Excluir serviço ---
Identificador (número inteiro): 104
[104] Segunda via da Carteira de Identidade (RG)
    Categoria     : Documentos
    Descrição     : Segunda via custa R$ 38,00 e fica pronta em 10 dias úteis. Agendamento obrigatório pelo portal. Leve certidão e comprovante de residência.
    Público-alvo  : Qualquer pessoa; menores de 12 anos acompanhados do responsável legal
    Canal ou local: Posto de Identificação de Aurora
Confirma a exclusão deste serviço? (s/n): talvez
Resposta inválida: digite s para sim ou n para não.
Confirma a exclusão deste serviço? (s/n): s
Serviço 104 excluído. Restam 15 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 5
--- Excluir serviço ---
Identificador (número inteiro): 105
[105] Certidões de nascimento, casamento e óbito
    Categoria     : Documentos
    Descrição     : No balcão: R$ 55,00, pronta em 5 dias úteis. Pelo portal, em PDF: R$ 49,00, pronta em 3 dias úteis. Isenção no balcão para baixa renda.
    Público-alvo  : A própria pessoa ou terceiro com procuração simples
    Canal ou local: Cartório Central de Aurora ou portal da Central do Cidadão
Confirma a exclusão deste serviço? (s/n): s
Serviço 105 excluído. Restam 14 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 5
--- Excluir serviço ---
Identificador (número inteiro): 700
[700] Horta comunitária e compostagem
    Categoria     : Atendimento comunitário
    Descrição     : Canteiros coletivos mantidos por voluntários. Qualquer morador pode participar dos mutirões de plantio.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Praça Central de Aurora, ao lado da biblioteca
Confirma a exclusão deste serviço? (s/n): s
Serviço 700 excluído. Restam 13 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 5
--- Excluir serviço ---
Identificador (número inteiro): 602
[602] Economia de energia em casa
    Categoria     : Energia
    Descrição     : Orientações simples para reduzir o consumo: lâmpadas de LED, banho mais curto e aparelhos fora da tomada quando não estão em uso.
    Público-alvo  : Todos os moradores
    Canal ou local: Portal da Central do Cidadão e mutirões de bairro
Confirma a exclusão deste serviço? (s/n): n
Exclusão cancelada. Nada foi alterado.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 5
--- Excluir serviço ---
Identificador (número inteiro): 999
Registro não encontrado: não existe serviço com o id 999.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 7
--- Ordenar serviços ---
 1 - Por título (ordem alfabética)
 2 - Por identificador (ordem crescente)
Critério: 1
Lista ordenada por título:
[402] Agendamento de consulta médica
    Categoria     : Saúde
    Descrição     : Marcação de consulta com clínico geral na unidade de saúde do bairro. Leve documento original com foto.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Unidade Básica de Saúde do bairro
[203] Cadastro em programas sociais
    Categoria     : Assistência social
    Descrição     : Orientação e inscrição de famílias de baixa renda nos programas sociais do município. Atendimento gratuito.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora
[101] Carteira de Trabalho digital
    Categoria     : Documentos
    Descrição     : Gratuita em qualquer canal. A versão digital fica disponível logo após o cadastro. Não precisa de agendamento.
    Público-alvo  : Trabalhadores; menores de 18 anos acompanhados do responsável legal
    Canal ou local: Portal ou aplicativo da Central do Cidadão
[602] Economia de energia em casa
    Categoria     : Energia
    Descrição     : Orientações simples para reduzir o consumo: lâmpadas de LED, banho mais curto e aparelhos fora da tomada quando não estão em uso.
    Público-alvo  : Todos os moradores
    Canal ou local: Portal da Central do Cidadão e mutirões de bairro
[301] Educação de Jovens e Adultos (EJA)
    Categoria     : Educação
    Descrição     : Turmas noturnas gratuitas para quem não concluiu o ensino fundamental ou médio na idade regular.
    Público-alvo  : Jovens e adultos a partir de 15 anos
    Canal ou local: Escolas municipais com turmas de EJA
[102] Inscrição no CPF
    Categoria     : Documentos
    Descrição     : Inscrição e correção de dados gratuitas pelo portal, com comprovante em até 2 dias úteis. O atendimento presencial tem taxa de R$ 7,00.
    Público-alvo  : Quem precisa se inscrever no CPF ou corrigir dados
    Canal ou local: Portal da Central do Cidadão ou balcão de atendimento
[302] Matrícula na rede municipal de ensino
    Categoria     : Educação
    Descrição     : Orientação para matricular crianças e adolescentes nas escolas municipais. Matrícula gratuita, feita na escola mais próxima de casa.
    Público-alvo  : Responsáveis por crianças e adolescentes em idade escolar
    Canal ou local: Secretaria de Educação de Aurora ou escola municipal mais próxima
[502] Ônibus da Cidadania: atendimento itinerante
    Categoria     : Atendimento comunitário
    Descrição     : Unidade móvel que leva orientação sobre documentos e serviços aos bairros mais distantes. Consulte o calendário no portal.
    Público-alvo  : Moradores de bairros distantes do centro
    Canal ou local: Praças e escolas dos bairros, conforme calendário do portal
[501] Ouvidoria comunitária
    Categoria     : Atendimento comunitário
    Descrição     : Canal para registrar sugestões, elogios e reclamações sobre os serviços públicos do bairro.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Balcão da Central do Cidadão, de segunda a sexta, das 8h às 17h
[103] Renovação da CNH
    Categoria     : Documentos
    Descrição     : Taxa de R$ 180,00; exame médico pago à parte na clínica credenciada. A nova CNH fica pronta em 7 dias úteis após a aprovação no exame.
    Público-alvo  : Motoristas com CNH vencida ou a até 30 dias do vencimento
    Canal ou local: Agendamento obrigatório pelo portal da Central do Cidadão
[601] Tarifa social de energia elétrica
    Categoria     : Energia
    Descrição     : Orientação sobre o desconto na conta de luz para famílias de baixa renda e sobre como pedir o benefício.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora ou portal da Central do Cidadão
[106] Título de eleitor
    Categoria     : Documentos
    Descrição     : Primeira via, segunda via e transferência gratuitas. O título digital sai em até 5 dias úteis. O cadastro fecha 150 dias antes de cada eleição.
    Público-alvo  : Eleitores a partir de 16 anos
    Canal ou local: Portal da Central do Cidadão ou Central Eleitoral de Aurora
[401] Vacinação de rotina
    Categoria     : Saúde
    Descrição     : Aplicação das vacinas do calendário básico para todas as idades. Gratuita e sem agendamento; leve a carteira de vacinação.
    Público-alvo  : Crianças, adultos e idosos
    Canal ou local: Unidade Básica de Saúde Central de Aurora
Total: 13 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 7
--- Ordenar serviços ---
 1 - Por título (ordem alfabética)
 2 - Por identificador (ordem crescente)
Critério: 2
Lista ordenada por identificador:
[101] Carteira de Trabalho digital
    Categoria     : Documentos
    Descrição     : Gratuita em qualquer canal. A versão digital fica disponível logo após o cadastro. Não precisa de agendamento.
    Público-alvo  : Trabalhadores; menores de 18 anos acompanhados do responsável legal
    Canal ou local: Portal ou aplicativo da Central do Cidadão
[102] Inscrição no CPF
    Categoria     : Documentos
    Descrição     : Inscrição e correção de dados gratuitas pelo portal, com comprovante em até 2 dias úteis. O atendimento presencial tem taxa de R$ 7,00.
    Público-alvo  : Quem precisa se inscrever no CPF ou corrigir dados
    Canal ou local: Portal da Central do Cidadão ou balcão de atendimento
[103] Renovação da CNH
    Categoria     : Documentos
    Descrição     : Taxa de R$ 180,00; exame médico pago à parte na clínica credenciada. A nova CNH fica pronta em 7 dias úteis após a aprovação no exame.
    Público-alvo  : Motoristas com CNH vencida ou a até 30 dias do vencimento
    Canal ou local: Agendamento obrigatório pelo portal da Central do Cidadão
[106] Título de eleitor
    Categoria     : Documentos
    Descrição     : Primeira via, segunda via e transferência gratuitas. O título digital sai em até 5 dias úteis. O cadastro fecha 150 dias antes de cada eleição.
    Público-alvo  : Eleitores a partir de 16 anos
    Canal ou local: Portal da Central do Cidadão ou Central Eleitoral de Aurora
[203] Cadastro em programas sociais
    Categoria     : Assistência social
    Descrição     : Orientação e inscrição de famílias de baixa renda nos programas sociais do município. Atendimento gratuito.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora
[301] Educação de Jovens e Adultos (EJA)
    Categoria     : Educação
    Descrição     : Turmas noturnas gratuitas para quem não concluiu o ensino fundamental ou médio na idade regular.
    Público-alvo  : Jovens e adultos a partir de 15 anos
    Canal ou local: Escolas municipais com turmas de EJA
[302] Matrícula na rede municipal de ensino
    Categoria     : Educação
    Descrição     : Orientação para matricular crianças e adolescentes nas escolas municipais. Matrícula gratuita, feita na escola mais próxima de casa.
    Público-alvo  : Responsáveis por crianças e adolescentes em idade escolar
    Canal ou local: Secretaria de Educação de Aurora ou escola municipal mais próxima
[401] Vacinação de rotina
    Categoria     : Saúde
    Descrição     : Aplicação das vacinas do calendário básico para todas as idades. Gratuita e sem agendamento; leve a carteira de vacinação.
    Público-alvo  : Crianças, adultos e idosos
    Canal ou local: Unidade Básica de Saúde Central de Aurora
[402] Agendamento de consulta médica
    Categoria     : Saúde
    Descrição     : Marcação de consulta com clínico geral na unidade de saúde do bairro. Leve documento original com foto.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Unidade Básica de Saúde do bairro
[501] Ouvidoria comunitária
    Categoria     : Atendimento comunitário
    Descrição     : Canal para registrar sugestões, elogios e reclamações sobre os serviços públicos do bairro.
    Público-alvo  : Moradores de Aurora
    Canal ou local: Balcão da Central do Cidadão, de segunda a sexta, das 8h às 17h
[502] Ônibus da Cidadania: atendimento itinerante
    Categoria     : Atendimento comunitário
    Descrição     : Unidade móvel que leva orientação sobre documentos e serviços aos bairros mais distantes. Consulte o calendário no portal.
    Público-alvo  : Moradores de bairros distantes do centro
    Canal ou local: Praças e escolas dos bairros, conforme calendário do portal
[601] Tarifa social de energia elétrica
    Categoria     : Energia
    Descrição     : Orientação sobre o desconto na conta de luz para famílias de baixa renda e sobre como pedir o benefício.
    Público-alvo  : Famílias de baixa renda
    Canal ou local: Centro de Assistência Social de Aurora ou portal da Central do Cidadão
[602] Economia de energia em casa
    Categoria     : Energia
    Descrição     : Orientações simples para reduzir o consumo: lâmpadas de LED, banho mais curto e aparelhos fora da tomada quando não estão em uso.
    Público-alvo  : Todos os moradores
    Canal ou local: Portal da Central do Cidadão e mutirões de bairro
Total: 13 serviço(s).

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 7
--- Ordenar serviços ---
 1 - Por título (ordem alfabética)
 2 - Por identificador (ordem crescente)
Critério: 9
Opção inválida: digite 1 ou 2.

================================================================
 MENU - Citizen Assist AI (serviços e orientações ao cidadão)
  1 Cadastrar    2 Listar todos        3 Consultar por id
  4 Atualizar    5 Excluir             6 Pesquisar (título/categoria)
  7 Ordenar      8 Carregar exemplos   0 Sair
================================================================
Escolha uma opção: 0
Sistema encerrado. Até logo!
```
<!-- SESSAO:FIM -->
