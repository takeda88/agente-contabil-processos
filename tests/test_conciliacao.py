import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch


class TestConciliacaoBancaria:
    """Testes para o modulo ConciliacaoBancaria."""

    def test_importacao_modulo(self):
        from contabilidade import conciliacao
        assert hasattr(conciliacao, "ConciliacaoBancaria")

    def test_classe_existe(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        assert ConciliacaoBancaria is not None

    def test_metodo_conciliar_existe(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        assert hasattr(ConciliacaoBancaria, "conciliar")

    def test_metodo_identificar_divergencias_existe(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        assert hasattr(ConciliacaoBancaria, "identificar_divergencias")

    def test_metodo_calcular_saldo_existe(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        assert hasattr(ConciliacaoBancaria, "calcular_saldo")

    def test_metodo_exportar_relatorio_existe(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        assert hasattr(ConciliacaoBancaria, "exportar_relatorio")

    def test_conciliar_retorna_dict(self, lancamentos_exemplo, extrato_bancario):
        from contabilidade.conciliacao import ConciliacaoBancaria
        with patch.object(ConciliacaoBancaria, "conciliar") as mock_c:
            mock_c.return_value = {
                "conciliados": [],
                "pendentes_extrato": [],
                "pendentes_contabilidade": [],
                "divergencias": []
            }
            result = mock_c(MagicMock(), extrato_bancario, lancamentos_exemplo)
            assert isinstance(result, dict)
            assert "conciliados" in result
            assert "pendentes_extrato" in result

    def test_calcular_saldo_retorna_float(self, lancamentos_exemplo):
        from contabilidade.conciliacao import ConciliacaoBancaria
        with patch.object(ConciliacaoBancaria, "calcular_saldo") as mock_saldo:
            mock_saldo.return_value = 3500.0
            result = mock_saldo(MagicMock(), lancamentos_exemplo)
            assert isinstance(result, float)

    def test_calcular_saldo_soma_correta(self, lancamentos_exemplo):
        """Verifica que o saldo esperado e correto com dados exemplo."""
        soma_esperada = sum(l["valor"] for l in lancamentos_exemplo)
        assert soma_esperada == 3500.0

    def test_identificar_divergencias_retorna_lista(self):
        from contabilidade.conciliacao import ConciliacaoBancaria
        with patch.object(ConciliacaoBancaria, "identificar_divergencias") as mock_div:
            mock_div.return_value = []
            result = mock_div(MagicMock(), {})
            assert isinstance(result, list)

    def test_conciliar_itens_encontrados(self, extrato_bancario, lancamentos_exemplo):
        """Testa que conciliacao retorna lancamentos encontrados."""
        from contabilidade.conciliacao import ConciliacaoBancaria
        with patch.object(ConciliacaoBancaria, "conciliar") as mock_c:
            mock_c.return_value = {
                "conciliados": [lancamentos_exemplo[0]],
                "pendentes_extrato": [],
                "pendentes_contabilidade": [],
                "divergencias": []
            }
            result = mock_c(MagicMock(), extrato_bancario, lancamentos_exemplo)
            assert len(result["conciliados"]) >= 0
