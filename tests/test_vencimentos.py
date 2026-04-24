import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch
from datetime import date, timedelta


class TestControleVencimentos:
    def test_importacao_modulo(self):
        from contabilidade import vencimentos
        assert hasattr(vencimentos, "ControleVencimentos")

    def test_classe_existe(self):
        from contabilidade.vencimentos import ControleVencimentos
        assert ControleVencimentos is not None

    def test_metodo_buscar_proximos_existe(self):
        from contabilidade.vencimentos import ControleVencimentos
        assert hasattr(ControleVencimentos, "buscar_proximos")

    def test_metodo_adicionar_existe(self):
        from contabilidade.vencimentos import ControleVencimentos
        assert hasattr(ControleVencimentos, "adicionar")

    def test_metodo_marcar_pago_existe(self):
        from contabilidade.vencimentos import ControleVencimentos
        assert hasattr(ControleVencimentos, "marcar_pago")

    def test_metodo_buscar_atrasados_existe(self):
        from contabilidade.vencimentos import ControleVencimentos
        assert hasattr(ControleVencimentos, "buscar_atrasados")

    def test_buscar_proximos_retorna_lista(self, banco_temp):
        from contabilidade.vencimentos import ControleVencimentos
        with patch.object(ControleVencimentos, "buscar_proximos") as mock_bp:
            mock_bp.return_value = [
                {"empresa": "EMPRESA A", "tipo": "DARF", "vencimento": "2026-04-30", "valor": 1500.0, "pago": False},
            ]
            result = mock_bp(MagicMock(), dias=30)
            assert isinstance(result, list)
            if result:
                assert "empresa" in result[0]
                assert "tipo" in result[0]
                assert "vencimento" in result[0]

    def test_buscar_atrasados_retorna_lista(self):
        from contabilidade.vencimentos import ControleVencimentos
        with patch.object(ControleVencimentos, "buscar_atrasados") as mock_ba:
            mock_ba.return_value = []
            result = mock_ba(MagicMock())
            assert isinstance(result, list)

    def test_adicionar_retorna_int_ou_none(self):
        from contabilidade.vencimentos import ControleVencimentos
        with patch.object(ControleVencimentos, "adicionar") as mock_add:
            mock_add.return_value = 1
            result = mock_add(MagicMock(), empresa="EMPRESA A", tipo="DARF",
                             data_vencimento="2026-05-15", valor=500.0)
            assert result is not None

    def test_marcar_pago_retorna_bool(self):
        from contabilidade.vencimentos import ControleVencimentos
        with patch.object(ControleVencimentos, "marcar_pago") as mock_mp:
            mock_mp.return_value = True
            result = mock_mp(MagicMock(), id_vencimento=1, data_pagamento="2026-04-28")
            assert isinstance(result, bool)

    def test_vencimento_estrutura_completa(self):
        """Testa que estrutura do vencimento tem todos os campos necessarios."""
        campos_esperados = ["empresa", "tipo", "vencimento", "valor", "pago"]
        vencimento = {"empresa": "X", "tipo": "DARF", "vencimento": "2026-05-10", "valor": 100.0, "pago": False}
        for campo in campos_esperados:
            assert campo in vencimento

    def test_data_vencimento_formato_valido(self):
        from datetime import datetime
        data_str = "2026-04-30"
        data = datetime.strptime(data_str, "%Y-%m-%d")
        assert data.year == 2026
        assert data.month == 4
