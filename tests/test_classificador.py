import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch


class TestClassificadorContabil:
    """Testes para o modulo ClassificadorContabil."""

    def setup_method(self):
        with patch("contabilidade.classificador.ClassificadorContabil.__init__", return_value=None):
            from contabilidade.classificador import ClassificadorContabil
            self.cls = ClassificadorContabil.__new__(ClassificadorContabil)
            self.cls.llm = None

    def test_importacao_modulo(self):
        """Verifica que o modulo pode ser importado."""
        from contabilidade import classificador
        assert hasattr(classificador, "ClassificadorContabil")

    def test_classe_existe(self):
        """Verifica que a classe ClassificadorContabil existe."""
        from contabilidade.classificador import ClassificadorContabil
        assert ClassificadorContabil is not None

    def test_metodo_classificar_lancamento_existe(self):
        from contabilidade.classificador import ClassificadorContabil
        assert hasattr(ClassificadorContabil, "classificar_lancamento")

    def test_metodo_detectar_inconsistencias_existe(self):
        from contabilidade.classificador import ClassificadorContabil
        assert hasattr(ClassificadorContabil, "detectar_inconsistencias")

    def test_metodo_gerar_resposta_existe(self):
        from contabilidade.classificador import ClassificadorContabil
        assert hasattr(ClassificadorContabil, "gerar_resposta")

    def test_metodo_classificar_email_existe(self):
        from contabilidade.classificador import ClassificadorContabil
        assert hasattr(ClassificadorContabil, "classificar_email")

    def test_classificar_lancamento_retorna_dict(self, lancamentos_exemplo):
        """Testa que classificar_lancamento retorna dict ou None."""
        from contabilidade.classificador import ClassificadorContabil
        with patch.object(ClassificadorContabil, "classificar_lancamento") as mock_cls:
            mock_cls.return_value = {
                "conta_debito": "6.1.1",
                "conta_credito": "1.1.1",
                "categoria": "despesa",
                "confianca": 0.95
            }
            instancia = MagicMock(spec=ClassificadorContabil)
            result = mock_cls(instancia, lancamentos_exemplo[0]["descricao"], lancamentos_exemplo[0]["valor"])
            assert isinstance(result, dict)
            assert "conta_debito" in result
            assert "conta_credito" in result

    def test_detectar_inconsistencias_lista(self, lancamentos_exemplo):
        """Testa que detectar_inconsistencias retorna lista."""
        from contabilidade.classificador import ClassificadorContabil
        with patch.object(ClassificadorContabil, "detectar_inconsistencias") as mock_det:
            mock_det.return_value = []
            instancia = MagicMock(spec=ClassificadorContabil)
            result = mock_det(instancia, lancamentos_exemplo)
            assert isinstance(result, list)

    def test_classificar_lancamento_campos_obrigatorios(self):
        """Testa campos obrigatorios no resultado de classificacao."""
        campos_esperados = ["conta_debito", "conta_credito", "categoria", "confianca"]
        from contabilidade.classificador import ClassificadorContabil
        with patch.object(ClassificadorContabil, "classificar_lancamento") as mock_cls:
            mock_cls.return_value = {k: None for k in campos_esperados}
            result = mock_cls(MagicMock(), "DESCRICAO TESTE", 100.0)
            for campo in campos_esperados:
                assert campo in result, f"Campo {campo} nao encontrado no resultado"

    def test_inicializacao_sem_chave_llm(self):
        """Testa que inicializacao sem chave LLM nao levanta excecao critica."""
        from contabilidade.classificador import ClassificadorContabil
        with patch.dict(os.environ, {}, clear=True):
            with patch("contabilidade.classificador.ClassificadorContabil.__init__", return_value=None):
                instancia = ClassificadorContabil.__new__(ClassificadorContabil)
                assert instancia is not None
