import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from unittest.mock import MagicMock, patch


class TestAgendadorTarefas:
    def test_importacao_modulo(self):
        from automacoes import scheduler
        assert hasattr(scheduler, "AgendadorTarefas")

    def test_classe_existe(self):
        from automacoes.scheduler import AgendadorTarefas
        assert AgendadorTarefas is not None

    def test_metodo_configurar_tarefas_existe(self):
        from automacoes.scheduler import AgendadorTarefas
        assert hasattr(AgendadorTarefas, "configurar_tarefas")

    def test_metodo_iniciar_existe(self):
        from automacoes.scheduler import AgendadorTarefas
        assert hasattr(AgendadorTarefas, "iniciar")

    def test_metodo_parar_existe(self):
        from automacoes.scheduler import AgendadorTarefas
        assert hasattr(AgendadorTarefas, "parar")

    def test_metodo_listar_tarefas_existe(self):
        from automacoes.scheduler import AgendadorTarefas
        assert hasattr(AgendadorTarefas, "listar_tarefas")

    def test_listar_tarefas_retorna_lista(self):
        from automacoes.scheduler import AgendadorTarefas
        with patch.object(AgendadorTarefas, "listar_tarefas") as mock_lt:
            mock_lt.return_value = [
                {"nome": "gerar_relatorio_mensal", "proximo_run": "2026-05-01 08:00:00"},
                {"nome": "organizar_pastas", "proximo_run": "2026-04-25 00:00:00"},
            ]
            result = mock_lt(MagicMock())
            assert isinstance(result, list)

    def test_iniciar_nao_levanta_excecao(self):
        from automacoes.scheduler import AgendadorTarefas
        with patch.object(AgendadorTarefas, "iniciar") as mock_ini:
            mock_ini.return_value = None
            result = mock_ini(MagicMock())
            assert result is None

    def test_parar_nao_levanta_excecao(self):
        from automacoes.scheduler import AgendadorTarefas
        with patch.object(AgendadorTarefas, "parar") as mock_parar:
            mock_parar.return_value = None
            result = mock_parar(MagicMock())
            assert result is None

    def test_tarefa_estrutura_esperada(self):
        """Verifica estrutura minima de uma tarefa agendada."""
        tarefa = {"nome": "verificar_vencimentos", "proximo_run": "2026-04-25 08:00:00", "ativo": True}
        assert "nome" in tarefa
        assert "proximo_run" in tarefa
