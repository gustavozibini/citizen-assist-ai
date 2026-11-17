# Citizen Assist AI — DSA

**Global Solution 2026.2 — FIAP — Data Structures and Algorithms (DSA)**

- **Aluno:** Gustavo Zibini Belizario — RM 561376
- **Curso:** Ciência da Computação — 1º ano — entrega individual
- **Linguagem:** Python 3, apenas biblioteca padrão

> Protótipo educacional com dados fictícios ("Central do Cidadão de Aurora"). Não é canal oficial de atendimento e não coleta dados pessoais.

## Objetivo

Sistema de terminal, com menu interativo, para cadastrar, listar, consultar, atualizar, excluir, pesquisar e ordenar serviços e orientações ao cidadão (documentos, assistência social, educação, saúde, atendimento comunitário e energia).

Todos os registros ficam em uma **lista simplesmente encadeada implementada à mão** (classes `No` e `ListaEncadeada`). A busca é **linear** (por identificador e por trecho do título ou da categoria, ignorando maiúsculas e acentos) e a ordenação é um **merge sort feito sobre os próprios nós da lista** (por título ou por identificador). O código não usa `sorted()`, `list.sort()` nem listas nativas para guardar, buscar ou ordenar.

Cada registro tem: identificador único, título, categoria, descrição, público-alvo e canal ou local de atendimento.

## Como executar

Basta ter o Python 3 instalado (testado no 3.13). Não há nada para instalar ou compilar. Dentro desta pasta:

```
python3 main.py      # abre o menu interativo
python3 testes.py    # executa os 72 cenários de teste
```

No Windows, use `python` no lugar de `python3`.

O menu começa com a lista vazia. A **opção 8** carrega 15 registros de exemplo. A opção 0 encerra o sistema; Ctrl+C e Ctrl+D também encerram sem mostrar erro técnico.

Outro programa pode abrir o menu assim:

```python
from main import executar_menu
executar_menu()
```

### Regerar as evidências e o PDF (opcional)

```
python3 testes.py > evidencias/saida_testes.txt
python3 main.py < evidencias/entradas_menu.txt > evidencias/sessao_menu.txt
python3 ferramentas/gerar_documentacao.py    # precisa de: pip install reportlab
```

## Organização dos arquivos

| Arquivo | Conteúdo |
|---|---|
| `servico.py` | Classe `Servico` (o registro) e as funções de validação e de normalização de texto |
| `lista_encadeada.py` | Classes `No` e `ListaEncadeada`: inserção, percurso, busca por id, atualização e remoção |
| `algoritmos.py` | Pesquisa por título ou categoria e ordenação por merge sort |
| `dados_exemplo.py` | 15 registros fictícios de exemplo |
| `main.py` | Menu interativo e função `executar_menu()` |
| `testes.py` | 72 cenários: entrada, esperado, observado e OK/FALHOU |
| `evidencias/saida_testes.txt` | Saída real de `python3 testes.py` |
| `evidencias/sessao_menu.txt` | Saída real do menu executado com as respostas de `evidencias/entradas_menu.txt` |
| `Documentacao_DSA.pdf` | Documentação técnica completa, com análise Big-O e tabela de evidências |
| `DOCUMENTACAO.md` | Mesmo conteúdo do PDF, em Markdown |
| `ferramentas/gerar_documentacao.py` | Ferramenta de apoio que gera o PDF (não faz parte do sistema) |

## Resumo da análise Big-O

n = quantidade de nós da lista; textos com tamanho limitado pela validação.

| Operação | Melhor caso | Pior caso |
|---|---|---|
| Inserção (confere id duplicado percorrendo a lista) | O(n) | O(n) |
| Busca por identificador | O(1) | O(n) |
| Pesquisa por título ou categoria | O(n) | O(n) |
| Atualização | O(1) | O(n) |
| Exclusão | O(1) | O(n) |
| Ordenação (merge sort) | O(n log n) | O(n log n) |

A justificativa de cada linha está na seção 7 da documentação.
