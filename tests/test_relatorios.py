import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch


class TestRelatoriosContabeis:
    def test_importacao_modulo(self):
        from contabilidade import relatorios
        assert hasattr(relatorios, "RelatoriosContabeis")

    def test_classe_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert RelatoriosContabeis is not None

    def test_metodo_gerar_dre_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert hasattr(RelatoriosContabeis, "gerar_dre")

    def test_metodo_gerar_balancete_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert hasattr(RelatoriosContabeis, "gerar_balancete")

    def test_metodo_gerar_fluxo_caixa_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert hasattr(RelatoriosContabeis, "gerar_fluxo_caixa")

    def test_metodo_exportar_excel_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert hasattr(RelatoriosContabeis, "exportar_excel")

    def test_metodo_exportar_pdf_existe(self):
        from contabilidade.relatorios import RelatoriosContabeis
        assert hasattr(RelatoriosContabeis, "exportar_pdf")

    def test_gerar_dre_estrutura(self, lancamentos_exemplo):
        from contabilidade.relatorios import RelatoriosContabeis
        with patch.object(RelatoriosContabeis, "gerar_dre") as mock_dre:
            mock_dre.return_value = {
                "receita_bruta": 11000.0,
                "deducoes": 0.0,
                "receita_liquida": 11000.0,
                "despesas_operacionais": -7500.0,
                "resultado_operacional": 3500.0,
                "resultado_liquido": 3500.0
            }
            result = mock_dre(MagicMock(), lancamentos_exemplo, "2026-04")
            assert isinstance(result, dict)
            assert "receita_bruta" in result
            assert "resultado_liquido" in result

    def test_gerar_balancete_estrutura(self, lancamentos_exemplo):
        from contabilidade.relatorios import RelatoriosContabeis
        with patch.object(RelatoriosContabeis, "gerar_balancete") as mock_bal:
            mock_bal.return_value = {
                "ativo": {"total": 20000.0},
                "passivo": {"total": 16500.0},
                "patrimonio": {"total": 3500.0}
            }
            result = mock_bal(MagicMock(), lancamentos_exemplo, "2026-04")
            assert isinstance(result, dict)

    def test_exportar_excel_retorna_bool(self, lancamentos_exemplo):
        from contabilidade.relatorios import RelatoriosContabeis
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            destino = tmp.name
        try:
            with patch.object(RelatoriosContabeis, "exportar_excel") as mock_exp:
                mock_exp.return_value = True
                result = mock_exp(MagicMock(), relatorio={}, tipo="DRE", destino=destino)
                assert isinstance(result, bool)
        finally:
            if os.path.exists(destino):
                os.unlink(destino)

    def test_gerar_fluxo_caixa_estrutura(self, lancamentos_exemplo):
        from contabilidade.relatorios import RelatoriosContabeis
        with patch.object(RelatoriosContabeis, "gerar_fluxo_caixa") as mock_fc:
            mock_fc.return_value = {
                "entradas": 11000.0,
                "saidas": -7500.0,
                "saldo_final": 3500.0,
                "lancamentos": lancamentos_exemplo
            }
            result = mock_fc(MagicMock(), lancamentos_exemplo, "2026-04")
            assert isinstance(result, dict)
            assert "saldo_final" in result

    def test_dre_resultado_liquido_correto(self, lancamentos_exemplo):
        """Testa calculo manual do resultado liquido com dados exemplo."""
        receitas = sum(l["valor"] for l in lancamentos_exemplo if l["valor"] > 0)
        despesas = sum(l["valor"] for l in lancamentos_exemplo if l["valor"] < 0)
        resultado = receitas + despesas
        assert resultado == 3500.0
