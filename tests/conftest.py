import pytest
import sys
import os
import tempfile
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture
def banco_temp():
    """Banco SQLite temporario para testes."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        path = tmp.name
    yield path
    os.unlink(path)

@pytest.fixture
def lancamentos_exemplo():
    """Lancamentos contabeis de exemplo para testes."""
    return [
        {"descricao": "SALARIO FUNCIONARIOS", "valor": -5000.0, "data": "2026-04-05",
         "categoria": "despesa", "conta": "6.1.1"},
        {"descricao": "RECEITA SERVICOS CONTABEIS", "valor": 8000.0, "data": "2026-04-10",
         "categoria": "receita", "conta": "3.1.1"},
        {"descricao": "ALUGUEL ESCRITORIO", "valor": -2500.0, "data": "2026-04-01",
         "categoria": "despesa", "conta": "6.2.1"},
        {"descricao": "HONORARIOS CONTABEIS", "valor": 3000.0, "data": "2026-04-15",
         "categoria": "receita", "conta": "3.1.2"},
    ]

@pytest.fixture
def extrato_bancario():
    """Extrato bancario de exemplo."""
    return [
        {"data": "2026-04-05", "descricao": "PAGTO SALARIO", "valor": -5000.0, "id": "EXT001"},
        {"data": "2026-04-10", "descricao": "TED RECEBIDA", "valor": 8000.0, "id": "EXT002"},
        {"data": "2026-04-01", "descricao": "DEBITO ALUGUEL", "valor": -2500.0, "id": "EXT003"},
    ]
