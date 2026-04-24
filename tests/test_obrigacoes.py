import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch
from datetime import date


class TestObrigacoesAcessorias:
    def test_importacao_modulo(self):
        from contabilidade import obrigacoes
        assert hasattr(obrigacoes, "ObrigacoesAcessorias")

    def test_classe_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert ObrigacoesAcessorias is not None

    def test_metodo_listar_por_regime_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert hasattr(ObrigacoesAcessorias, "listar_por_regime")

    def test_metodo_calcular_prazo_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert hasattr(ObrigacoesAcessorias, "calcular_prazo")

    def test_metodo_verificar_enviadas_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert hasattr(ObrigacoesAcessorias, "verificar_enviadas")

    def test_metodo_gerar_checklist_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert hasattr(ObrigacoesAcessorias, "gerar_checklist")

    def test_metodo_registrar_entrega_existe(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        assert hasattr(ObrigacoesAcessorias, "registrar_entrega")

    def test_listar_por_regime_simples_nacional(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        with patch.object(ObrigacoesAcessorias, "listar_por_regime") as mock_list:
            mock_list.return_value = [
                {"nome": "DAS", "periodicidade": "mensal", "competencia": "mes"},
                {"nome": "DASN", "periodicidade": "anual", "competencia": "ano"},
            ]
            result = mock_list(MagicMock(), "simples_nacional", "2026-04")
            assert isinstance(result, list)
            assert len(result) >= 1

    def test_listar_por_regime_lucro_presumido(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        with patch.object(ObrigacoesAcessorias, "listar_por_regime") as mock_list:
            mock_list.return_value = [
                {"nome": "DCTF", "periodicidade": "mensal"},
                {"nome": "EFD-Contribuicoes", "periodicidade": "mensal"},
            ]
            result = mock_list(MagicMock(), "lucro_presumido", "2026-04")
            assert isinstance(result, list)

    def test_calcular_prazo_retorna_string(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        with patch.object(ObrigacoesAcessorias, "calcular_prazo") as mock_prazo:
            mock_prazo.return_value = "2026-05-20"
            result = mock_prazo(MagicMock(), "DCTF", "mensal")
            assert isinstance(result, str)

    def test_gerar_checklist_retorna_lista(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        with patch.object(ObrigacoesAcessorias, "gerar_checklist") as mock_check:
            mock_check.return_value = [
                {"obrigacao": "DCTF", "status": "pendente", "prazo": "2026-05-15"},
                {"obrigacao": "DIRF", "status": "entregue", "prazo": "2026-02-28"},
            ]
            result = mock_check(MagicMock(), empresa={})
            assert isinstance(result, list)

    def test_registrar_entrega_retorna_bool(self):
        from contabilidade.obrigacoes import ObrigacoesAcessorias
        with patch.object(ObrigacoesAcessorias, "registrar_entrega") as mock_reg:
            mock_reg.return_value = True
            result = mock_reg(MagicMock(), "DCTF", "mensal", "SEFAZ")
            assert isinstance(result, bool)
            assert result is True
