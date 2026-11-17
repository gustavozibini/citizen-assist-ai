# -*- coding: utf-8 -*-
"""
Citizen Assist AI - testes do módulo de Energia
Aluno: Gustavo Zibini Belizario - RM 561376 (FIAP, 1CC, Global Solution 2026.2)

Confere:
1. os cálculos contra contas feitas à mão (escritas aqui mesmo, passo a passo);
2. o tratamento de entradas inválidas;
3. a coerência entre as respostas do assistente e a tabela comparativa (resultados/comparacao.csv).
Uso:  python3 testes_energia.py -v
"""

import csv
import re
import unittest
from pathlib import Path

import assistente_energia as assistente
import calculos_energia as calc
from calculos_energia import fmt, fmt_payback, fmt_reais

P = calc.carregar_premissas()
PASTA = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 1. Cálculos conferidos com contas feitas à mão
# ---------------------------------------------------------------------------

class TestCalculosAMao(unittest.TestCase):
    """Valores esperados calculados à mão a partir de premissas.csv (caso-base)."""

    def setUp(self):
        self.lista = calc.comparar_alternativas(P)
        self.tarifa = 0.47242 + 0.31696  # TUSD + TE = 0,78938 R$/kWh

    def test_energia_e_igual_potencia_vezes_tempo(self):
        # 5500 W durante 1 hora = 5,5 kWh
        self.assertAlmostEqual(calc.energia_kwh(5500, 1), 5.5)

    def test_caso_base_A(self):
        # horas no mês = 4 pessoas x 1 banho x (10/60) h x 30 dias = 20 h
        # energia = 5,5 kW x 20 h = 110 kWh/mês
        # custo = 110 x 0,78938 = 86,8318 R$/mês
        a = calc.buscar(self.lista, "A")
        self.assertAlmostEqual(a["consumo_kwh_mes"], 110.0, places=6)
        self.assertAlmostEqual(a["consumo_kwh_ano"], 1320.0, places=6)
        self.assertAlmostEqual(a["custo_mes"], 86.8318, places=4)
        self.assertAlmostEqual(a["custo_ano"], 86.8318 * 12, places=3)
        # CO2 = 1320 kWh x 0,0385 kg/kWh = 50,82 kg/ano
        self.assertAlmostEqual(a["co2_ano"], 50.82, places=4)

    def test_habitos_B(self):
        # potência média = (5500 x 0,7 x 6 meses + 5500 x 6 meses) / 12 = 4675 W
        # horas = 4 x 1 x (6/60) x 30 = 12 h  ->  4,675 kW x 12 h = 56,1 kWh/mês
        # economia = (110 - 56,1) x 0,78938 = 42,547582 R$/mês
        b = calc.buscar(self.lista, "B")
        self.assertAlmostEqual(b["consumo_kwh_mes"], 56.1, places=6)
        self.assertAlmostEqual(b["economia_mes"], 42.547582, places=5)
        self.assertEqual(b["investimento"], 0)
        self.assertEqual(fmt_payback(b), "sem investimento")

    def test_solar_comercial_C1(self):
        # teto do coletor = 2 m2 x 4,589 x 0,40 x 30 = 110,136 kWh/mês (não limita)
        # energia solar = 0,70 x 110 = 77 kWh/mês  ->  rede = 33 kWh/mês
        # economia = 77 x 0,78938 = 60,78226 R$/mês
        # payback = 3359,57 / 60,78226 = 55,27 meses
        c1 = calc.buscar(self.lista, "C1")
        self.assertAlmostEqual(c1["consumo_kwh_mes"], 33.0, places=6)
        self.assertAlmostEqual(c1["economia_mes"], 60.78226, places=5)
        self.assertAlmostEqual(c1["payback_meses"], 3359.57 / 60.78226, places=4)
        self.assertAlmostEqual(c1["payback_meses"], 55.27, places=2)
        # CO2 evitado = 77 x 12 x 0,0385 = 35,574 kg/ano
        self.assertAlmostEqual(c1["co2_evitado_ano"], 35.574, places=4)

    def test_asbc_C2(self):
        # energia solar = min(0,50 x 110 ; 2 x 4,589 x 0,25 x 30 = 68,835) = 55 kWh/mês
        # payback = 1500 / (55 x 0,78938) = 1500 / 43,4159 = 34,55 meses
        c2 = calc.buscar(self.lista, "C2")
        self.assertAlmostEqual(c2["consumo_kwh_mes"], 55.0, places=6)
        self.assertAlmostEqual(c2["payback_meses"], 34.55, places=2)

    def test_fotovoltaica_D(self):
        # kWp = 110 / (4,589 x 30 x 0,75) = 110 / 103,2525 = 1,06535 kWp
        # investimento = 1,06535 x (12000 / 2) = 6392,1 R$
        d = calc.buscar(self.lista, "D")
        kwp = 110 / (4.589 * 30 * 0.75)
        self.assertAlmostEqual(d["investimento"], kwp * 6000, places=4)
        self.assertAlmostEqual(d["investimento"], 6392.10, places=1)
        self.assertAlmostEqual(d["payback_meses"], 6392.10 / 86.8318, places=1)

    def test_teto_do_coletor_limita_a_energia_solar(self):
        # pedido de 100% de 200 kWh, mas o coletor só capta 2 x 4 x 0,5 x 30 = 120 kWh
        self.assertAlmostEqual(calc.energia_solar_util_kwh_mes(200, 1.0, 2, 4, 0.5, 30), 120)

    def test_tarifa_social(self):
        # 80 kWh gratuitos; excedente a 0,30631 + 0,30560 = 0,61191 R$/kWh
        self.assertEqual(calc.conta_tarifa_social(50, P), 0)
        self.assertAlmostEqual(calc.conta_tarifa_social(90, P), 10 * 0.61191, places=6)
        # casa com 100 kWh de outros aparelhos: o banho de 110 kWh é todo pago
        # 110 x 0,61191 = 67,3101 R$/mês
        a_social = calc.buscar(calc.comparar_alternativas(P, tarifa_social=True), "A")
        self.assertAlmostEqual(a_social["custo_mes"], 67.3101, places=4)

    def test_payback_casos_especiais(self):
        self.assertEqual(calc.payback_meses(0, 50), 0)
        self.assertIsNone(calc.payback_meses(1000, 0))
        self.assertAlmostEqual(calc.payback_meses(1200, 100), 12)

    def test_mesma_necessidade_em_todas_as_alternativas(self):
        # nenhuma alternativa pode gastar mais que o caso-base nem ter economia negativa
        a = calc.buscar(self.lista, "A")
        for alt in self.lista:
            self.assertLessEqual(alt["consumo_kwh_mes"], a["consumo_kwh_mes"] + 1e-9)
            self.assertGreaterEqual(alt["economia_mes"], -1e-9)

    def test_formato_brasileiro(self):
        self.assertEqual(fmt(1234.5, 1), "1.234,5")
        self.assertEqual(fmt_reais(86.8318), "R$ 86,83")


# ---------------------------------------------------------------------------
# 2. Entradas inválidas
# ---------------------------------------------------------------------------

class TestEntradasInvalidas(unittest.TestCase):

    def test_vazio_e_none(self):
        for texto in ("", "   ", None):
            resposta = assistente.responder(texto)
            self.assertIn("não digitou nada", resposta)

    def test_texto_muito_longo(self):
        self.assertIn("muito longa", assistente.responder("a" * 1000))

    def test_texto_sem_sentido_e_fora_do_escopo(self):
        for texto in ("asdfghjkl", "????", "12345", "qual a previsão do tempo?", "quem ganhou o jogo?"):
            self.assertIn("fora do que eu sei", assistente.responder(texto), texto)

    def test_dados_pessoais_nao_sao_aceitos_nem_repetidos(self):
        exemplos = ["meu cpf é 123.456.789-00", "meu telefone é (11) 98765-4321",
                    "manda para fulano@email.com", "minha instalação é 123456789",
                    "CPF 12345678900"]
        for texto in exemplos:
            resposta = assistente.responder(texto)
            self.assertIn("não digite CPF", resposta, texto)
            self.assertNotIn("98765", resposta)
            self.assertNotIn("123.456.789", resposta)

    def test_numero_negativo_absurdo_ou_texto(self):
        self.assertIsNotNone(assistente.ler_numero("-3", 1, 15)[1])
        self.assertIsNotNone(assistente.ler_numero("999", 1, 15)[1])
        self.assertIsNotNone(assistente.ler_numero("abc", 1, 15)[1])
        self.assertIsNotNone(assistente.ler_numero("nan", 1, 15)[1])
        self.assertIsNotNone(assistente.ler_numero("inf", 1, 15)[1])
        self.assertEqual(assistente.ler_numero("5.500", 1000, 9000), (5500.0, None))
        self.assertEqual(assistente.ler_numero("7,5", 1, 60), (7.5, None))

    def test_calculadora_em_texto_com_numero_absurdo(self):
        resposta = assistente.responder("calcular 500 pessoas 8 minutos")
        self.assertIn("fora do esperado", resposta)

    def test_menu_com_entradas_ruins_nao_quebra(self):
        entradas = iter(["x", "", "7", "-2", "abc", "9999", "", "texto", "5", "sei la", "",
                         "8", "", "0"])
        saidas = []
        assistente.executar_menu(entrada=lambda _msg: next(entradas), saida=saidas.append)
        tudo = "\n".join(saidas)
        self.assertIn("Opção inválida", tudo)
        self.assertIn("Digite um número entre 1 e 15", tudo)
        self.assertIn("Vou usar o valor padrão", tudo)
        self.assertIn("não digitou nada", tudo)
        self.assertIn("Até logo", tudo)

    def test_menu_fim_de_entrada(self):
        def entrada_que_acaba(_msg):
            raise EOFError
        saidas = []
        assistente.executar_menu(entrada=entrada_que_acaba, saida=saidas.append)
        self.assertIn("Encerrando", saidas[-1])


# ---------------------------------------------------------------------------
# 3. Coerência entre o assistente e a tabela comparativa
# ---------------------------------------------------------------------------

def ler_tabela():
    """Lê resultados/comparacao.csv em {(cenario, codigo): linha}."""
    with open(PASTA / "resultados" / "comparacao.csv", encoding="utf-8") as arquivo:
        return {(l["cenario"], l["codigo"]): l for l in csv.DictReader(arquivo, delimiter=";")}


class TestCoerenciaAssistenteTabela(unittest.TestCase):

    def setUp(self):
        self.tabela = ler_tabela()

    def valor(self, codigo, coluna, cenario="tarifa_convencional"):
        return float(self.tabela[(cenario, codigo)][coluna])

    def test_tabela_esta_atualizada(self):
        # o CSV gravado tem que bater com o cálculo atual (senão rode calculos_energia.py)
        for cenario, social in (("tarifa_convencional", False), ("tarifa_social", True)):
            for alt in calc.comparar_alternativas(P, tarifa_social=social):
                for coluna in ("consumo_kwh_mes", "custo_mes", "investimento", "economia_mes", "co2_evitado_ano"):
                    self.assertAlmostEqual(self.valor(alt["codigo"], coluna, cenario), alt[coluna], places=2)

    def test_resposta_gasto(self):
        resposta = assistente.responder("Quanto gasta o chuveiro?")
        self.assertIn(fmt(self.valor("A", "consumo_kwh_mes")) + " kWh", resposta)
        self.assertIn(fmt_reais(self.valor("A", "custo_mes")), resposta)
        self.assertIn(fmt_reais(self.valor("A", "custo_ano")), resposta)

    def test_resposta_economizar(self):
        resposta = assistente.responder("Como economizar no banho?")
        self.assertIn(fmt(self.valor("B", "consumo_kwh_mes")), resposta)
        self.assertIn(fmt_reais(self.valor("B", "economia_mes")), resposta)

    def test_resposta_solar(self):
        resposta = assistente.responder("Vale a pena aquecedor solar?")
        for codigo in ("C1", "C2"):
            self.assertIn(fmt_reais(self.valor(codigo, "investimento")), resposta)
            self.assertIn(fmt_reais(self.valor(codigo, "economia_mes")), resposta)
            self.assertIn(fmt(self.valor(codigo, "payback_meses"), 0) + " meses", resposta)

    def test_resposta_fotovoltaica(self):
        resposta = assistente.responder("E painel fotovoltaico?")
        self.assertIn(fmt_reais(self.valor("D", "investimento")), resposta)
        self.assertIn(fmt(self.valor("D", "payback_meses"), 0) + " meses", resposta)

    def test_resposta_tarifa_social(self):
        resposta = assistente.responder("O que é a Tarifa Social e quem tem direito?")
        self.assertIn(fmt_reais(self.valor("A", "custo_mes", "tarifa_social")), resposta)
        self.assertIn("80 kWh", resposta)
        self.assertIn("CadÚnico", resposta)

    def test_resposta_co2(self):
        resposta = assistente.responder("Quanto CO2 eu evito?")
        for codigo in ("B", "C1", "C2", "D"):
            self.assertIn(fmt(self.valor(codigo, "co2_evitado_ano")) + " kg", resposta)

    def test_calculadora_caso_base_igual_a_tabela(self):
        resposta = assistente.calcular_caso(P["moradores"], P["minutos_banho_base"], P["potencia_chuveiro_w"])
        self.assertIn(fmt(self.valor("A", "consumo_kwh_mes")) + " kWh", resposta)
        for codigo in ("B", "C1", "C2", "D"):
            self.assertIn(fmt_reais(self.valor(codigo, "economia_mes")), resposta)

    def test_numeros_do_readme_saem_do_codigo(self):
        # o bloco gerado do README tem que estar atualizado
        readme = (PASTA / "README.md").read_text(encoding="utf-8")
        comparacao = (PASTA / "resultados" / "comparacao.md").read_text(encoding="utf-8")
        tabela = calc.tabela_markdown(calc.comparar_alternativas(P), P)
        self.assertIn(tabela, readme)
        # todo número decimal citado fora do bloco gerado existe na comparação ou nas premissas
        fora = (readme.split(calc.MARCA_INICIO)[0] + readme.split(calc.MARCA_FIM)[1])
        premissas = (PASTA / "dados" / "premissas.csv").read_text(encoding="utf-8")
        for numero in set(re.findall(r"\d[\d.]*,\d+", fora)):
            como_ponto = numero.replace(".", "").replace(",", ".")
            em_kg_por_kwh = str(float(como_ponto) / 1000)  # 38,5 kg/MWh = 0.0385 kg/kWh
            self.assertTrue(numero in comparacao or como_ponto in premissas
                            or em_kg_por_kwh in premissas, numero)

    def test_toda_resposta_tem_fonte_e_aviso(self):
        perguntas = ["quanto gasta o chuveiro", "como economizar", "aquecedor solar",
                     "fotovoltaica", "tarifa social", "co2", "fontes"]
        for pergunta in perguntas:
            resposta = assistente.responder(pergunta)
            self.assertIn("Fonte:", resposta, pergunta)
            self.assertIn("Não há garantia de economia", resposta, pergunta)
            self.assertIn("protótipo educacional", resposta, pergunta)


if __name__ == "__main__":
    unittest.main()
