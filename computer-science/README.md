# Computer Science — Módulo de decisão lógica

**Gustavo Zibini Belizario — RM 561376 — 1CC**

Situação: *"O cidadão pode ser atendido no balcão agora?"* (regras da ficha FC-07, versão 01/10/2026).

| Var. | 1 | 0 |
|---|---|---|
| A | Dia útil | Sábado, domingo ou feriado |
| B | Entre 8h e 17h | Fora do horário |
| C | Serviço exige agendamento (RG, CNH) | Não exige |
| D | Tem agendamento | Não tem |
| S | Pode ser atendido | Não pode (mostra o motivo) |

- Forma canônica: `S = Σm(12, 13, 15) = ABC'D' + ABC'D + ABCD`
- Simplificada (álgebra e Karnaugh): `S = A·B·(C' + D)`
- De Morgan: `S = A·B·(C·D')'`
- Circuitos: 6 portas (original) → 3 portas (simplificado)

## Executar

```bash
python3 decisao_logica.py   # programa interativo
python3 testes_decisao.py   # valida as 16 combinações
python3 gerar_figuras.py    # mapa de Karnaugh e circuitos (requer schemdraw, matplotlib)
python3 gerar_relatorio.py  # gera Relatorio_Computer_Science.pdf (requer reportlab)
```

## Simulação no logic.ly

Monte o circuito simplificado em https://logic.ly/demo: 4 chaves (A, B, C, D), NOT, OR de 2 entradas, AND de 3 entradas, lâmpada em S. Ligações: C → NOT → OR; D → OR; A, B e saída da OR → AND; AND → lâmpada. Salve os prints em `prints/` e rode `gerar_relatorio.py` de novo.

Protótipo educacional: não é canal oficial e não confirma atendimento, serviços ou direitos.
